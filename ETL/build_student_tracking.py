import os, sys

pathname = os.path.dirname(sys.argv[0])
full_pathname = os.path.abspath(pathname)
split_pathname = full_pathname.split(sep="mvesc")
base_pathname = os.path.join(split_pathname[0], "mvesc")
parentdir = os.path.join(base_pathname, "ETL")
from mvesc_utility_functions import *


'''
Joint note from JG and ZZ:
This python file generates a SQL query to build a table tracking
students over time. Each column represents a year and the grade the
student was in that year.

No students are lost in the process
(except 34 pre-K students that leave in pre-K that JG removes).
    These pre-K students are all
    students from Riverview district that seemed to enter and leave district in
    same year and are not useful for our analysis.

This problem is tricky because students can have multiple observations
per year (multiple grades).
    Left in duplicate records because of grade level errors, we will need to clean
these later.

As for conflicting withdrawals for a student,
    we retained only the most recent withdrawal Date
    and reason. Each of 37,914 students is in table at least once. (JG)
'''

def build_wide_format(cursor, grade_begin=6, year_begin=0, year_end=3000,
    schema = 'clean', snapshots = 'all_snapshots',
    tracking = 'wrk_tracking_students'):

    """ Gets the range of school years covered by the data in the snapshots
    table, and generates the appropriate sql query to track all students in
    the snapshots table over that range of years. Executes query to build this
    data table, by default in clean.wrk_tracking_students.

    :param psycopg2.cursor cursor: cursor to execute queries
    :param str schema: name of schema where snapshots table lives
    :param str snapshots: name of table where snapshots table lives
    :return nothing (executes query in database)
    """
    get_year_range = """
    select min(school_year), max(school_year) from
        {schema}.{snapshots}""".format(schema=schema, snapshots=snapshots)
    cursor.execute(get_year_range)
    min_year, max_year = cursor.fetchone()
    min_year = int(min_year) # these should already be integers anyway
    max_year = int(max_year)

    # generate SQL query based on min/max_year
    query_build_wide_table = sql_gen_tracking_students(min_year, max_year,
            schema = schema, snapshots = snapshots, table = tracking)

    query_survival = cohort_survival_analysis(max(min_year, year_begin),
        min(max_year, year_end), grade_begin = grade_begin, schema = schema,
        table = tracking)
    cursor.execute(query_build_wide_table)
    cursor.execute(query_survival)
    col_names = [desc[0] for desc in cursor.description]
    print(col_names)
    cohort_results = cursor.fetchall()
    cohort_results = None

    sql_query_add_columns = """
    alter table {schema}.{tracking} add column outcome_bucket varchar(30);
    alter table {schema}.{tracking} add column outcome_category varchar(30);
    """.format(schema = schema, tracking = tracking)

    cursor.execute(sql_query_add_columns)
    return(cohort_results)

def sql_gen_tracking_students(year_begin, year_end,
    schema = 'clean', snapshots = 'all_snapshots',
    table = 'wrk_tracking_students'):

    """ Generates sql query to create a table that tracks a student's
    grade over time. Repeatedly performs full outer joins for all the
    students we observe in a given year, from year_begin to year_end.

    If a student appears multiple times with the same grade level, or if their
    grade level is missing in some but not all entries, they will appear only
    once. Duplicate entries will happen only when there is conflicting grade
    level information for some years.

    This subquery is then left-joined with all withdrawal reasons, creating a
    distinct row for each given withdrawal reason, except did not withdraw.

    :param int year_begin: the first year we'd like to start tracking with
    :param int year_end: the last year to track a student to
    :return: sql query string
    :rtype: str
    """

    # remove previously created table if exists
    query_frame = """
    drop table if exists {}.{};
    create table {}.{} as
        (select * from
            (select * from (
    """.format(schema, table, schema, table)


    # perform a subquery for each year, getting the distinct
    #   student lookup & grade pairs
    #   and add that as a column for that year (using full joins)
    #       if a student is recorded as two distinct grades that year,
    #       they currently get duplicate rows
    #       SUGGESTED FIX: choose the lowest or highest grade for each year
    #       only keeping one distinct row per student ID & year
    for year in range(year_begin, year_end+1):
        subquery = """
        (select distinct student_lookup, grade as "{}" from {}.{}
            where school_year = {} and grade is not null) as grades_{}
        """.format(year, schema, snapshots, year, year)
        if year == year_begin:
            query_frame += subquery
        else:
            # perform string substitution of subquery
            query_frame += """
            full join {} using (student_lookup)
            """.format(subquery)

    # after getting grades for each year, get the unique and most recent withdrawal
    #   reason for each student
    # Adds this via left-join of a large subquery
    #   which creates the 'latest_withdrawal' and 'latest_reason' subtables
    #   The latest_withdrawal subtable is created by a subquery getting unique
    #       distinct student / withdraw reason / withdraw date
    #       where withdraw_reason is not null (empty withdrawal code)
    #       and not 'did not withdraw'
    #       but keeping only the latest date.
    # NOTE: this keeps only one row for students with multiple unique withdrawal codes
    query_frame += """ )
    order by student_lookup) as students_grades_only
    left join
        (select latest_reason.* from
            (select student_lookup, max(district_withdraw_date)
            as last_date from
                (select distinct student_lookup, withdraw_reason,
                district_withdraw_date from {}.{}
                    where withdraw_reason <> '{}'
                    and withdraw_reason is not null
                order by student_lookup, district_withdraw_date) as all_withdraw_reasons
            group by student_lookup) as latest_withdrawal
        """.format(schema, snapshots, 'did not withdraw')

    # This is the second part of the large subquery above
    # It gets a 'latest_reason' subtable
    #   It gets all the unique student / reason / date / irn codes
    #       and then left joins on student + latest_date column
    # Finally, this large subquery is wrapped in the above code section by
    #   only keeping those columns from the latest_reason subtable
    query_frame += """
        left join
            (select distinct student_lookup, withdraw_reason, withdrawn_to_irn,
            district_withdraw_date from {}.{}) as latest_reason
        on latest_withdrawal.student_lookup = latest_reason.student_lookup and
        latest_withdrawal.last_date = latest_reason.district_withdraw_date)
        as last_withdrawal_only using (student_lookup));
    """.format(schema, snapshots)

    # call query as cursor.execute(sql_gen_tracking_students())
    return query_frame

# This function is not documented because it's not used
#   It was used to see how the numbers of students change across years.
def cohort_survival_analysis(year_begin, year_end, grade_begin,
    schema = 'clean', table = 'wrk_tracking_students'):
    """
    Returns a sql query to count the number of students in a particular cohort that advance to the next grade level and stay in the system each year,
    returning for each year the grade level, school year, and number of students
    remaining on-track with the cohort.
    """
    joined_query = ''
    next_grade = grade_begin
    for year in range(year_begin, year_end+1):
        if (year != year_begin):
            #next_grade = '%02d' % (int(next_grade)+1)
            next_grade = next_grade +1
        if (next_grade > 12):
            break
        subquery_get_count = """
        (select {next_grade} as grade, {year} as school_year, count(*) from
            (select distinct(student_lookup)
                from {schema}.{table} where "{year_begin}" = {grade_begin})
                as grade_{grade_begin}_in_{year_begin}
        """.format(schema=schema, table=table, year_begin=year_begin,
                    grade_begin=grade_begin, year=year, next_grade=next_grade)
        if (year == year_begin):
            joined_query += """ %s )""" % (subquery_get_count)

        else:
            subquery_next_year = """
            where student_lookup in (select distinct(student_lookup)
                from {schema}.{table} where "{year}" = {next_grade}))
            """.format(schema=schema, table=table, year_begin=year_begin,
                grade_begin=grade_begin, year=year, next_grade=next_grade)

            joined_query += """
            union {query_1} {query_2}
            """.format(query_1 = subquery_get_count,
            query_2 = subquery_next_year)

    joined_query += """ order by school_year;"""
    return(joined_query)

def main():
    """
    Build a table (clean.wrk_tracking_students) that shows for all students in
    clean.all_snapshots, what grade they were in during each school year, and
    if they have a withdrawal reason and date, their most recent withdrawal
    information. Student may be duplicated if there are records of them
    attending different conflicting grades during same school year.
    """
    with postgres_pgconnection_generator() as connection:
        with connection.cursor() as cursor:
            #print(sql_gen_tracking_students(2006, 2015))
            #print(cohort_survival_analysis(2006, 2015, 6))
            print(build_wide_format(cursor))
        connection.commit()
    execute_sql_script(os.path.join(parentdir,'sql',
        'remove_duplicate_withdrawals_from_tracking.sql'))
    
    print('done!')

if __name__ == "__main__":
    main()
