import psycopg2 as pg
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
import sqlalchemy

def postgres_pgconnection_generator(pass_file="/mnt/data/mvesc/pgpass"):
    """ Generate a psycopg2 connector
    Note: you can only run it on the mvesc server
    :param str pass_file: file with the credential information
    :return connection to the postgres database
    :rtype psycopg2.connection
    """
    with open(pass_file, 'r') as f:
        passinfo = f.read()
    passinfo = passinfo.strip().split(':')
    host_address = passinfo[0]
    port = passinfo[1]
    user_name = passinfo[2]
    name_of_database = passinfo[3]
    user_password = passinfo[4]
    connection = pg.connect(host=host_address, database=name_of_database, user=user_name, password=user_password)
    return connection

def postgres_engine_generator(pass_file="/mnt/data/mvesc/pgpass"):
    """ Generate a sqlalchemy engine to mvesc database
    Note: you can only run it on the mvesc server
    :param str pass_file: file with the credential information
    :return sqlalchemy.engine object engine: object created  by create_engine() in sqlalchemy
    :rtype sqlalchemy.engine
    """
    with open(pass_file, 'r') as f:
        passinfo = f.read()
    passinfo = passinfo.strip().split(':')
    host_address = passinfo[0]
    port = passinfo[1]
    user_name = passinfo[2]
    name_of_database = passinfo[3]
    user_password = passinfo[4]
    sql_eng_str = "postgresql://"+user_name+":"+user_password+"@"+host_address+'/'+name_of_database
    engine = create_engine(sql_eng_str)
    return engine

def get_all_student_lookups(connection, schema = 'clean',
    table = 'all_snapshots'):
    """ Takes a postgres connection, schema, and table, and returns
    a list of all the unique students in the table
    :param psycopg2.connection: connection to the database
    :param str schema: name of the schema from which to draw tables
    :param str table: name of the table from which to draw student_list
    :return list of student lookup numbers
    :rtype list[int]
    """
    cursor = connection.cursor()
    union_lookups_query = """select distinct("StudentLookup") from {}.{}""".format(schema, table)
    union_lookups_query += """ order by "StudentLookup\""""
    cursor.execute(union_lookups_query)
    student_list = cursor.fetchall()
    # change list of tuples into list of ints
    student_list = [i[0] for i in student_list]
    return student_list

def sql_gen_tracking_students(year_begin, year_end, schema = 'clean',
    table = 'wrk_tracking_students'):

    start_string = """ create view {}.{} as
        select * from {}.all_student_lookups """.format(schema, table, schema)

    end_string = """ order by "StudentLookup";
        create table {}.{} as (SELECT * FROM {}.{} LEFT JOIN
	(SELECT DISTINCT "StudentLookup", withdraw_reason FROM {}.all_snapshots
		WHERE withdraw_reason <> 'did not withdraw') AS zzx01 USING ("StudentLookup"));""".format(schema, table, schema, table, schema)

    middle_string = """"""
    for yearNum in range(year_begin, year_end+1):
        print(str(yearNum))
        middle_string = middle_string + """
            left join (select distinct "StudentLookup", grade as "{}"
            from {}.all_snapshots where year = '{}')
	    as zzq{} using ("StudentLookup")""".format(yearNum, schema, yearNum, yearNum)

    return start_string + middle_string + end_string

def build_wide_format(connection, student_list):
    cursor = connection.cursor()
    get_year_range = """select min(year), max(year) from clean.all_snapshots"""
    cursor.execute(get_year_range)
    min_year, max_year = cursor.fetchone()
    #cursor.execute(sql_gen_tracking_students(min_year, max_year))
    min_year = int(min_year)
    max_year = int(max_year)
    print(min_year, type(min_year))
    print(max_year, type(max_year))

def main():
    # connection = postgres_pgconnection_generator()
    connection = postgres_engine_generator().raw_connection()
    all_students = get_all_student_lookups(connection)
    build_wide_format(connection, all_students)
    print(sql_gen_tracking_students(2006, 2015))

if __name__ == "__main__":
    main()
