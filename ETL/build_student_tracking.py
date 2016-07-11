#from mvesc_utility_functions import postgres_pgconnection_generator
import psycopg2 as pg
from contextlib import contextmanager
from mvesc_utility_functions import *

'''
Joint note from JG and ZZ:
This python file generates a SQL query to build a table tracking
students over time. Each column represents a year and the grade the 
student was in that year.

With work from JG, we ensure no students are lost in the process of this
(except 34 pre-K students that leave in pre-K that JG removes).
    These are all
    students from Riverview district that seemed to enter and leave district in
    same year, inc. errors, pre-k students, not useful.
   
This SQL code is not great and may not be the best way to do this.
This problem is tricky because students can have multiple observations
per year (multiple grades).
    Left in duplicate records because of grade level errors, we will need to clean
these later. 

As for withdrawals, retained only the most recent withdrawal Date
and reason. Each of 37,914 is in table at least once. (JG)
'''

# get postgres_pgconnection_generator() function from 


def build_wide_format(cursor, schema = 'clean', snapshots = 'all_snapshots'):
    """ Gets the range of school years covered by the data in the snapshots
    table, and generates the appropriate sql query to track all students in
    the snapshots table over that range of years. Executes query to build this
    data table, by default in clean.wrk_tracking_students.
    :param psycopg2.cursor cursor: cursor to execute queries
    :param str schema: name of schema where snapshots table lives
    :param str snapshots: name of table where snapshots table lives
    :return nothing (executes query in database)
    """
    get_year_range = """select min(school_year), max(school_year) from """\
                      """{}.{}""".format(schema, snapshots)
    cursor.execute(get_year_range)
    min_year, max_year = cursor.fetchone()
    min_year = int(min_year) # these should already be integers anyway
    max_year = int(max_year)
    query = sql_gen_tracking_students(min_year, max_year,
                                       schema = schema, snapshots = snapshots)
    cursor.execute(query)

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

    # for each year, get the distinct student lookup and grade pairs
    #   and add that as a column for that year (using full joins)
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

    # after getting grades, get the unique and most recent withdrawal
    #   reason for each student
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
            (select distinct student_lookup, withdraw_reason,
            district_withdraw_date from {}.{}) as latest_reason
    	on latest_withdrawal.student_lookup = latest_reason.student_lookup and
    	latest_withdrawal.last_date = latest_reason.district_withdraw_date)
        as last_withdrawal_only using (student_lookup));
    """.format(schema, snapshots)

    # call query as cursor.execute(sql_gen_tracking_students())
    return query_frame

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
            # cursor.execute(query)
            # print(sql_gen_tracking_students(2006, 2015))
            build_wide_format(cursor)
        connection.commit()
    print('done!')

if __name__ == "__main__":
    main()
