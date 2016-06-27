import pandas as pd
import numpy as np
import psycopg2 as pg
import itertools
import json


##### these should be in a general utility module
def open_db_connection():
    """
    Opens a connection with the mvesc PSQL database

    :rtype: pg.extensions.connection object connection
    """
    pass_file = "/mnt/data/mvesc/pgpass" # username, db information
    with open(pass_file, 'r') as f:
        passinfo = f.read()
    passinfo = passinfo.strip().split(':')
    with open(pass_file, 'r') as f:
        passinfo = f.read()
    passinfo = passinfo.strip().split(':')
    host_address = passinfo[0]
    user_name = passinfo[2]
    name_of_database = passinfo[3]
    user_password = passinfo[4]
    connection = pg.connect(host=host_address, database=name_of_database,
user=user_name, password=user_password)
    return connection

def get_student_table_names(connection):
    """
    Retrieves the list of names of tables in the database which are indexed by StudentLookup

    :param pg.extensions.connection object connection: sql connection
    :rtype: list of strings
    """

    my_query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
    cursor = connection.cursor()
    cursor.execute(my_query)
    table_names = cursor.fetchall()
    table_names = [t[0] for t in table_names]
    cursor.close()
    #filter out tables not indexed by StudentLookup numbers in a more intellegent manner
    # removing non-student tables
    table_names.remove('all_lookup')
    table_names.remove('DistrictSchoolIDs')
    table_names.remove('DistrictRating1011')
    table_names.remove('DistrictRating1112')
    table_names.remove('DistrictRating1213')
    table_names.remove('DistrictRating1314')
    table_names.remove('DistrictRating1415')

    # removing replicated tables
    table_names.remove('OAAOGT')
    table_names.remove('CurrentMobility')
    table_names.remove('Mobility_2010_2015')

    return table_names


###### specific functions

def student_lookup_query(table_names):
    """
    Writes a SQL query to drop the current all_student_lookup_table and create a new one
    using all the StudentLookup numbers in the given list of tables

    :param list: list of table names
    :retype: string
    """
    my_query = "drop table if exists clean.all_student_lookup; "
    my_query += "create table clean.all_student_lookup as "
    for t in table_names:
        my_query += "select \"StudentLookup\" from \"" + t + "\" union \n "
    my_query = my_query[:-6] + ";"
    return my_query


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
    "Schoolyear" as "year",
    'Ridgewood' as "district"
    from "Ridgewoodgrades2007_2016"
    union all
    select  "StudentLookup",
    "Course" as "course_code",
    "Cname" as "course_name",
    "term",
    cast("Grade" as text) as "grade",
    "Mark" as "mark",
    "Schoolyear" as "year",
    'Riverview' as "district"
    from "RiverViewgrades2006_16"
    union all
    select "StudentLookup",
    "Course" as "course_code",
    "Cname" as "course_name",
    "term",
    cast("Grade" as text) as "grade",
    "Mark" as "mark",
    "Schoolyear" as "year",
    'TriValley' as "district"
    from "TriValleyGrades2006_16"
    union all
    select "StudentLookup",
    "Course" as "course_code",
    "Cname" as "course_name",
    "term",
    cast("Grade" as text) as "grade",
    "Mark" as "mark",
    "Schoolyear" as "year",
    'West Muskingum' as "district"
    from "WestMuskingumgrades2006_16"
    union all
    select "StudentLookup",
    "Course" as "course_code",
    "Cname" as "course_name",
    "term",
    cast("Grade" as text) as "grade",
    "Mark" as "mark",
    "Schoolyear" as "year",
    'Franklin' as "district"
    from "Franklingrades2006_16"
    union all
    select "StudentLookup",
    "Course" as "course_code",
    "Cname" as "course_name",
    "term",
    cast("Grade" as text) as "grade",
    "Mark" as "mark",
    "Schoolyear" as "year",
    'Maysville' as "district"
    from "Maysvillegrades2006_16"
    union all
    select "StudentLookup",
    "Course" as "course_code",
    "Cname" as "course_name",
    "term",
    cast("Grade" as text) as "grade",
    "Mark" as "mark",
    "SchoolYear" as "year",
    'Coshocton' as "district"
    from "CoshoctonGrades2006_16"
    union all
    select "StudentLookup",
    "Course" as "course_code",
    "Cname" as "course_name",
    "term",
    cast("Grade" as text) as "grade",
    "Mark" as "mark",
    "SchoolYear" as "year",
    'Crooksville' as "district"
    from "CrooksvilleGrades2010_16"
    union all
    select "StudentLookup",
    "Course" as "course_code",
    "Cname" as "course_name",
    "term",
    cast("Grade" as text) as "grade",
    "Mark" as "mark",
    "SchoolYear" as "year",
    'East Muskingum' as "district"
    from "EastMuskingumGrades2010_16\"
    """
    return my_query

def all_absences_query():
    """
    Writes a SQL query to drop the current all_absences_table and create a new one

    :rtype: string
    """
    my_query = "drop table if exists clean.all_absences; "
    my_query += "create table clean.all_absences as "
    my_query += """
    select  "StudentLookup",
    "Date" as "date",
    "AbsenceLength" as "absence_length",
    "AbsenceCode" as "absence_code",
    "AbsenceDesc" as "absence_desc",
    "School" as "school"
    from "CCFRRWRVabsence09_16"
    union all
    select  "StudentLookup",
    "Date" as "date",
    "AbsenceLength" as "absence_length",
    "AbsenceCode" as "absence_code",
    "AbsenceDesc" as "absence_desc",
    "School" as "school"
    from "MATVWMAbsences1415"
    union all
    select  "StudentLookup",
    "Date" as "date",
    "AbsenceLength" as "absence_length",
    "AbsenceCode" as "absence_code",
    "AbsenceDesc" as "absence_desc",
    "School" as "school"
    from "MATVWMAbsences1516\""""
    return my_query





###### script to build tables

connection = open_db_connection()
table_names = get_student_table_names(connection)
cursor = connection.cursor()
#cursor.execute(student_lookup_query(table_names))
cursor.execute(all_grades_query())
#cursor.execute(all_absences_query())
cursor.close()
connection.commit()


"""
with open('snapshot_column_names.json', 'r') as f:
    new_cols = json.loads(f.read())
print(new_cols)
"""
