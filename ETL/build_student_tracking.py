import psycopg2 as pg
import numpy as np
import pandas as pd

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

def build_wide_format(connection, student_list):
    cursor = connection.cursor()
    get_year_range = """select min(year), max(year) from clean.all_snapshots"""
    cursor.execute(get_year_range)
    min_year, max_year = cursor.fetchone()

def main():
    connection = postgres_pgconnection_generator()
    all_students = get_all_student_lookups(connection)

if __name__ == "__main__":
    main()
