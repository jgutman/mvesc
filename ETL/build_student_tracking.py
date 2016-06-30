#from mvesc_utility_functions import postgres_pgconnection_generator
import psycopg2 as pg
from contextlib import contextmanager

# Zhe Overall Note:
#   I have not yet checked to ensure the utility functions work
#   While this code repeats duplicate rows, I have not yet error checked to
#       ensure we didn't lose students in the process (perhaps those
#       without a grade or withdrawal code?)
#   This SQL code is not great and may not be the best way to do this.
#   This problem is tricky because students can have multiple observations
#       per year.

# delete this function once Hanna has updated utility functions
# use commented import statement above instead
@contextmanager
def postgres_pgconnection_generator(pass_file="/mnt/data/mvesc/pgpass"):
    """ Generate a psycopg2 connection (to use in a with statement)
    Note: you can only run it on the mvesc server
    :param str pass_file: file with the credential information
    :yield pg.connection generator: connection to database
    """
    with open(pass_file, 'r') as f:
        passinfo = f.read()
    passinfo = passinfo.strip().split(':')
    host_address = passinfo[0]
    port = passinfo[1]
    user_name = passinfo[2]
    name_of_database = passinfo[3]
    user_password = passinfo[4]
    yield pg.connect(host=host_address, database=name_of_database,
        user=user_name, password=user_password)

def build_wide_format(cursor, schema = 'clean', snapshots = 'all_snapshots'):
     get_year_range = """select min(school_year), max(school_year) from """ \
            """{}.{}""".format(schema, snapshots)
     cursor.execute(get_year_range)
     min_year, max_year = cursor.fetchone()
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
    :return: sql query string with a %s placeholder for non-withdrawal value
    :rtype: str
    """
    query_frame = """drop table if exists {}.{}; """.format(schema, table)
    query_frame += """ create table {}.{} as (select * from """ \
        """(select * from ( """.format(schema, table)

    for year in range(year_begin, year_end+1):
        if (year > year_begin):
            query_frame += """ full join """
        query_frame += """(select distinct student_lookup, grade as "{}" """ \
            """from {}.{} where school_year = {} and grade is not null) """ \
            """as grades_{} """.format(year, schema, snapshots, year, year)
        if (year > year_begin):
            query_frame += """ using (student_lookup) """

    query_frame += """) order by student_lookup) as students_grades_only """ \
        """left join (select distinct student_lookup, withdraw_reason from """ \
        """{}.{} where withdraw_reason <> 'did not withdraw' """ \
        """and withdraw_reason is not null) as all_withdraw_reasons """ \
        """using (student_lookup));""".format(schema, snapshots)

    # call query as cursor.execute(sql_gen_tracking_students())
    return query_frame

def main():
    with postgres_pgconnection_generator() as connection:
        with connection.cursor() as cursor:
            # cursor.execute(query)
            build_wide_format(cursor)
        connection.commit()
    print('done!')

if __name__ == "__main__":
    main()
