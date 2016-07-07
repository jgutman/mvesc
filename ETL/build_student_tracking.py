from mvesc_utility_functions import postgres_pgconnection_generator
#import psycopg2 as pg
#from contextlib import contextmanager

'''
These docstrings need to be updated.
'''

'''
Zhe Overall Note:
   I have not yet checked to ensure the utility functions work
   While this code repeats duplicate rows, I have not yet error checked to
   ensure we didn't lose students in the process (perhaps those
   without a grade or withdrawal code?)

   This SQL code is not great and may not be the best way to do this.
   This problem is tricky because students can have multiple observations
   per year (multiple grades or multiple withdrawals).
'''

'''
Zhe's note is somewhat obsolete now, have tried to deal with some of the issues
he mentions above. We don't lose students in the process, except the 34 students
I chose to remove because they never appear with a grade level. These are all
students from Riverview district that seemed to enter and leave district in
same year, inc. errors, pre-k students, not useful.

Left in duplicate records because of grade level errors, we will need to clean
these later. As for withdrawals, retained only the most recent withdrawal Date
and reason. Each of 37,914 is in table at least once. (JG)
'''

def build_wide_format(cursor, grade_begin, year_begin=0, year_end=3000,
    schema = 'clean', snapshots = 'all_snapshots'):
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
    query_build_wide_table = sql_gen_tracking_students(min_year, max_year,
            schema = schema, snapshots = snapshots)
    query_survival = cohort_survival_analysis(max(min_year, year_begin),
        min(max_year, year_end), grade_begin = grade_begin, schema = schema)
    cursor.execute(query_build_wide_table)
    cursor.execute(query_survival)
    col_names = [desc[0] for desc in cursor.description]
    print(col_names)
    cohort_results = cursor.fetchall()
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
    query_frame = """
    drop table if exists {}.{};
    create table {}.{} as
        (select * from
            (select * from (
    """.format(schema, table, schema, table)

    for year in range(year_begin, year_end+1):
        subquery = """
        (select distinct student_lookup, grade as "{}" from {}.{}
            where school_year = {} and grade is not null) as grades_{}
        """.format(year, schema, snapshots, year, year)
        if year == year_begin:
            query_frame += subquery
        else:
            query_frame += """
            full join {} using (student_lookup)
            """.format(subquery)

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

def cohort_survival_analysis(year_begin, year_end, grade_begin,
    schema = 'clean', table = 'wrk_tracking_students'):
    """
    no docstring yet
    """
    joined_query = ''
    next_grade = grade_begin
    for year in range(year_begin, year_end+1):
        if (year != year_begin):
            next_grade = '%02d' % (int(next_grade)+1)
        if (next_grade == '13'):
            break
        subquery_get_count = """
        (select {next_grade} as grade, {year} as school_year, count(*) from
            (select distinct(student_lookup)
                from {schema}.{table} where "{year_begin}" = '{grade_begin}')
                as grade_{grade_begin}_in_{year_begin}
        """.format(schema=schema, table=table, year_begin=year_begin,
                    grade_begin=grade_begin, year=year, next_grade=next_grade)
        if (year == year_begin):
            joined_query += """ %s )""" % (subquery_get_count)

        else:
            subquery_next_year = """
            where student_lookup in (select distinct(student_lookup)
                from {schema}.{table} where "{year}" = '{next_grade}'))
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
            # print(sql_gen_tracking_students(2006, 2015))
            # print(cohort_survival_analysis(2006, 2015, '04'))
            print(build_wide_format(cursor))
        connection.commit()
    print('done!')

if __name__ == "__main__":
    main()
