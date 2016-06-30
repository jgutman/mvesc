import mvesc_utility_functions

# Zhe Overall Note:
#   I have not yet checked to ensure the utility functions work
#   While this code repeats duplicate rows, I have not yet error checked to
#       ensure we didn't lose students in the process (perhaps those
#       without a grade or withdrawal code?)
#   This SQL code is not great and may not be the best way to do this.
#   This problem is tricky because students can have multiple observations
#       per year.

# Zhe: I commented out Jackie's older code
# def get_all_student_lookups(connection, schema = 'clean',
#     table = 'all_snapshots'):
#     """ Takes a postgres connection, schema, and table, and returns
#     a list of all the unique students in the table
#     :param psycopg2.connection: connection to the database
#     :param str schema: name of the schema from which to draw tables
#     :param str table: name of the table from which to draw student_list
#     :return list of student lookup numbers
#     :rtype list[int]
#     """
#     cursor = connection.cursor()
#     union_lookups_query = """select distinct("StudentLookup") from {}.{}""".format(schema, table)
#     union_lookups_query += """ order by "StudentLookup\""""
#     cursor.execute(union_lookups_query)
#     student_list = cursor.fetchall()
#     # change list of tuples into list of ints
#     student_list = [i[0] for i in student_list]
#     return student_list
# def build_wide_format(connection, student_list):
#     cursor = connection.cursor()
#     get_year_range = """select min(year), max(year) from clean.all_snapshots"""
#     cursor.execute(get_year_range)
#     min_year, max_year = cursor.fetchone()


def sql_gen_tracking_students(year_begin, year_end):
    """ Generates sql code to create a table that tracks a student's
    grade over time. First, it gets all the unique StudentLookup numbers
    from the all_student_lookup numbers. (This can be changed to the list
        of unique lookup numbers in the snapshots table)
    From this set, it repeatedly performs left joins for all the 
    students we observe in a given year, from year_begin to year_end. 
    The for loop adds a left join command looping across the appropriate 
    years. Each left join searches the all_snapshots table, filtered by
    the appropriate year and only keeping distinct rows for each student 
        (this avoids repeated grades).
    After all the years are joined together, we left join the students

    :param int year_begin: the first year we'd like to start tracking with
    :param int year_end: the last year to track a student to
    """
    # create a view temporarily for convenience
    #   improve: skip the view and instead make this into a sub-query
    start_string = """ create view clean.wrk_tracking_students as 
        select * from clean.all_student_lookups """

    # end by ordering by StudentLookup
    end_string = """ order by "StudentLookup"; """

    # create table with withdrawal info string
    #   merge the view just made, with tracking info for the students
    #   with each student's distinct withdrawal reason
    #       note: (each student may have multiple withdrawal reasons)
    #               leading to mutiple rows
    #       note: we do not merge the withdrawl code 'did not withdraw'
    #           because this would result in multiple rows per student
    #           since some students may have 'did not withdraw' in year 1
    #           but in year 3 have 'graduated'.
    #           This reduces the number of duplicate rows we have
    withdraw_table_string = """
            create table clean.wrk_track_students as
            (SELECT * FROM clean.wrk_tracking_students LEFT JOIN
            (SELECT DISTINCT "StudentLookup", withdraw_reason FROM clean.all_snapshots 
            WHERE withdraw_reason <> 'did not withdraw') AS zzx01 USING ("StudentLookup"));"""
    
    # for loop to perform left joins for each year we have data for
    middle_string = """"""
    for yearNum in range(year_begin, year_end+1):
        # left join all the unique student-grade combinations in a given year
        #   note: some students have multiple grades per year, resulting in
        #       a duplicate row for a student
        middle_string = middle_string + """
            left join (select distinct "StudentLookup", grade as "{}"
            from clean.all_snapshots where year = '{}')
	    as zzq{} using ("StudentLookup")""".format(yearNum, yearNum, yearNum)
    
    # concatenate all these strings together with .format()
    return "{}{}{}{}".format(start_string, middle_string, end_string, withdraw_table_string)


def main():
    connection = postgres_pgconnection_generator()
    # all_students = get_all_student_lookups(connection)
    # hard code year_begin = 2006 and year_end = 2015
    sql_code_to_gen_tracking = sql_gen_tracking_students(2006, 2015)

    # get cursor
    cur = conn.cursor()
    # execute sql command
    cur.execute(sql_code_to_gen_tracking)
    # commit sql command, close cursor & connection
    connection.commit()
    connection.close()
    cur.close()


if __name__ == "__main__":
    main()
