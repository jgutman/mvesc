import pandas as pd
import numpy as np
import psycopg2 as pg
import itertools
import json
from contextlib import contextmanager

##### these are in the general utility module, will be updated when its merged
@contextmanager
def open_db_connection(pass_file):
    """
    Opens a connection with the mvesc PSQL database

    :rtype: pg.extensions.connection object connection
    """
    with open(pass_file, 'r') as f:
        passinfo = f.read()
    passinfo = passinfo.strip().split(':')
    host_address = passinfo[0]
    user_name = passinfo[2]
    name_of_database = passinfo[3]
    user_password = passinfo[4]
    yield pg.connect(host=host_address, database=name_of_database, \
                     user=user_name, password=user_password)


def get_column_type(cursor, table_name, column_name):
    """
    Returns the data type of the given column in the given table

    :param pg cursor:
    :param string: table name
    :param string: column name'
    """
    my_query = "select data_type from information_schema.columns where "
    my_query += "table_name = (%s) and column_name =(%s) ;"
    cursor.execute(my_query, [table_name, column_name])
    column_type = cursor.fetchall()[0][0]
    return column_type


def get_column_names(cursor, table, schema="public"):
    """
    Get column names of a table

    :param pg object cursor: cursor in psql database 
    :param string table: table name in the database
    :rtype: list
    """ 
    my_query = "SELECT column_name FROM information_schema.columns WHERE"
    my_query += " table_schema = (%s) and table_name = (%s)"
    cursor.execute(my_query, [schema, table])
    raw_col_names = cursor.fetchall()
    return list([x[0] for x in raw_col_names])

def get_student_table_names(cursor):
    """
    Retrieves the list of names of tables in the database which are 
    indexed by StudentLookup

    :param pg object cursor: cursor in psql database
    :rtype: list of strings
    """

    my_query = "SELECT table_name FROM information_schema.tables "
    my_query += "WHERE table_schema = 'public'"
    cursor.execute(my_query)
    table_names = cursor.fetchall()
    table_names = [t[0] for t in table_names]
    to_remove = []
    for t in table_names:
        if "StudentLookup" not in get_column_names(cursor,t):
            to_remove.append(t)
    for t in to_remove:
        table_names.remove(t)
    return table_names


###### specific functions

def student_lookup_query(table_names):
    """
    Writes a SQL query to drop the current all_student_lookups table 
    and create a new one using all the StudentLookup numbers in the 
    given list of tables

    :param list table_names: list of table names
    :retype: string
    """

    my_query = "drop table if exists clean.all_student_lookups; "
    my_query += "create table clean.all_student_lookups as "
    for t in table_names:
        my_query += "select \"StudentLookup\" as student_lookup from "
        my_query += "\"" + t + "\""
        union_clause = " union \n"
        my_query += union_clause
    my_query = my_query[:-len(union_clause)] + ";"
    return my_query

# the all_grades and all_absences queries could be updated into the form of the all_snapshots query


def all_grades_query():
    """
    Writes a SQL query to drop the current all_grades_table and create a new one

    :rtype: string
    """

    my_query = "drop table if exists clean.all_grades; "
    my_query += "create table clean.all_grades as "
    my_query += """
    select  "StudentLookup",
    "Course" as "course_code",
    "Cname" as "course_name",
    "term",
    cast("Grade" as text) as "grade",
    "Mark" as "mark",
    "Schoolyear" as "school_year",
    'Ridgewood' as "district"
    from "Ridgewoodgrades2007_2016"
    union all
    select  "StudentLookup",
    "Course" as "course_code",
    "Cname" as "course_name",
    "term",
    cast("Grade" as text) as "grade",
    "Mark" as "mark",
    "Schoolyear" as "school_year",
    'Riverview' as "district"
    from "RiverViewgrades2006_16"
    union all
    select  "StudentLookup",
    "Course" as "course_code",
    "Cname" as "course_name",
    "term",
    cast("Grade" as text) as "grade",
    "Mark" as "mark",
    "Schoolyear" as "school_year",
    'TriValley' as "district"
    from "TriValleyGrades2006_16"
    union all
    select "StudentLookup",
    "Course" as "course_code",
    "Cname" as "course_name",
    "term",
    cast("Grade" as text) as "grade",
    "Mark" as "mark",
    "Schoolyear" as "school_year",
    'West Muskingum' as "district"
    from "WestMuskingumgrades2006_16"
    union all
    select  "StudentLookup",
    "Course" as "course_code",
    "Cname" as "course_name",
    "term",
    cast("Grade" as text) as "grade",
    "Mark" as "mark",
    "Schoolyear" as "school_year",
    'Franklin' as "district"
    from "Franklingrades2006_16"
    union all
    select  "StudentLookup",
    "Course" as "course_code",
    "Cname" as "course_name",
    "term",
    cast("Grade" as text) as "grade",
    "Mark" as "mark",
    "Schoolyear" as "school_year",
    'Maysville' as "district"
    from "Maysvillegrades2006_16"
    union all
    select  "StudentLookup",
    "Course" as "course_code",
    "Cname" as "course_name",
    "term",
    cast("Grade" as text) as "grade",
    "Mark" as "mark",
    "SchoolYear" as "school_year",
    'Coshocton' as "district"
    from "CoshoctonGrades2006_16"
    union all
    select  "StudentLookup",
    "Course" as "course_code",
    "Cname" as "course_name",
    "term",
    cast("Grade" as text) as "grade",
    "Mark" as "mark",
    "SchoolYear" as "school_year",
    'Crooksville' as "district"
    from "CrooksvilleGrades2010_16"
    union all
    select  "StudentLookup",
    "Course" as "course_code",
    "Cname" as "course_name",
    "term",
    cast("Grade" as text) as "grade",
    "Mark" as "mark",
    "SchoolYear" as "school_year",
    'East Muskingum' as "district"
    from "EastMuskingumGrades2010_16\"
    """
    return my_query

def all_absences_query():
    """
    Writes a SQL query to drop the current all_absences_table 
    and create a new one

    :rtype: string
    """
    my_query = "drop table if exists clean.all_absences; "
    my_query += "create table clean.all_absences as "
    my_query += """
    select  "StudentLookup" as student_lookup,
    "Date" as "date",
    "AbsenceLength" as "absence_length",
    "AbsenceCode" as "absence_code",
    "AbsenceDesc" as "absence_desc",
    "School" as "school"
    from "CCFRRWRVabsence09_16"
    union all
    select  "StudentLookup" as student_lookup,
    "Date" as "date",
    "AbsenceLength" as "absence_length",
    "AbsenceCode" as "absence_code",
    "AbsenceDesc" as "absence_desc",
    "School" as "school"
    from "MATVWMAbsences1415"
    union all
    select  "StudentLookup" as student_lookup,
    "Date" as "date",
    "AbsenceLength" as "absence_length",
    "AbsenceCode" as "absence_code",
    "AbsenceDesc" as "absence_desc",
    "School" as "school"
    from "MATVWMAbsences1516\""""
    return my_query


def all_snapshots_query(cursor, snapshot_tables):
    """
    Writes a SQL query to drop the current all_snapshots table 
    and create a new one

    :param list snapshot_tables: list of tables to include
    :param pg object cursor: 
    :rtype: string
    """
    # json file with column name and type matchings
    with open('snapshot_column_names.json', 'r') as f:
        new_cols_file = json.load(f)
    new_cols = new_cols_file[u'column_names']
    
    snapshot_query = """
    drop table if exists clean.all_snapshots;
    create table clean.all_snapshots as
    select "StudentLookup" as student_lookup,
    """
    for t in snapshot_tables:
        old_cols = get_column_names(cursor,t)
        #for each new column name
        for key in sorted(new_cols.keys()):
            #item contains column type and list of matching old column names
            item = new_cols[key] 
            found = 0 
            #loop through old column names that match the current new one
            for c in item[u'name']:
                #check if each matching column name exists in the current table
                if c in old_cols:
                    #for text, must convert empty string to null before casting
                    if get_column_type(cursor, t, c) == "character varying":
                        snapshot_query += """
                        cast(nullif("{old_name}", '') as {type}) as {new_name},
                        """.format_map({'old_name':str(c), \
                                        'type':str(item[u'type']), \
                                        'new_name':str(key)})
                    else:
                        snapshot_query += """
                        cast("{old_name}" as {type}) as {new_name},
                        """.format_map({'old_name':str(c), \
                                        'type':str(item[u'type']),\
                                        'new_name':str(key)})
                    found = 1
                    break
            if found == 0: #column does not exist in current table
                snapshot_query += """
                cast(null as {type}) as {new_name},
                """.format_map({'new_name':str(key), \
                                'type':str(item[u'type'])})
        snapshot_query += """
        cast(20{year} as int) as school_year from "{table}"
        """.format_map({'year':t[9:11], 'table':t})
        union_clause = """ union select "StudentLookup" as student_lookup, """
        snapshot_query += union_clause
    snapshot_query = snapshot_query[:-len(union_clause)]+";"
    return snapshot_query



###### script to build tables

pass_file = "/mnt/data/mvesc/pgpass" # username, db information
with open_db_connection(pass_file) as connection:
    with connection.cursor() as cursor:
        table_names = get_student_table_names(cursor)
        snapshot_tables = ["Districts{0:02}{1:02}".format(x,x+1) \
                           for x in range(6,16)]
        snapshot_tables += ["Districts{0:02}{1:02}_CREM".format(x,x+1) \
                           for x in range(10,16)]
        #cursor.execute(student_lookup_query(table_names))
        #cursor.execute(all_grades_query())
        #cursor.execute(all_absences_query())
        #cursor.execute(all_snapshots_query(cursor, snapshot_tables))
    connection.commit()
