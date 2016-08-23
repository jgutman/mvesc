import pandas as pd
import numpy as np
import psycopg2 as pg
import itertools
import json
from mvesc_utility_functions import *
from contextlib import contextmanager

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

def all_generic_query(cursor, list_of_tables_to_consolidate, col_names_mapping_json,
    consolidated_table_name, student_lookup_spelling = "StudentLookup"):
    """
    Generates a SQL query to drop the current version of the
    and create a new one, consolidating several similar tables

    :param pg object cursor:
    :param list list_of_tables_to_consolidate: list of tables to include
    :param str col_names_mapping_json: name of a json file with mapping between
    old and new column names
    :param str consolidated_table_name: name of the resulting consolidated table
    :param str student_lookup_spelling: adjust this default value if student lookup
        is spelled different in the original data
    :rtype: string
    """
    # json file with column name and type matchings
    with open(col_names_mapping_json, 'r') as f:
        new_cols_file = json.load(f)
    new_cols = new_cols_file[u'column_names']
    
    consolidate_query = """
    drop table if exists clean.{consolidated_table};
    create table clean.{consolidated_table} as
    select "{student_lookup_spelling}" as student_lookup,
    """.format_map({'consolidated_table':consolidated_table_name,
                    'student_lookup_spelling':student_lookup_spelling})

    for t in list_of_tables_to_consolidate:
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
                        consolidate_query += """
                        cast(nullif("{old_name}", '') as {type}) as {new_name},
                        """.format_map({'old_name':str(c), \
                                        'type':str(item[u'type']), \
                                        'new_name':str(key)})
                    else:
                        consolidate_query += """
                        cast("{old_name}" as {type}) as {new_name},
                        """.format_map({'old_name':str(c), \
                                        'type':str(item[u'type']),\
                                        'new_name':str(key)})
                    found = 1
                    break
            if found == 0: #column does not exist in current table
                consolidate_query += """
                cast(null as {type}) as {new_name},
                """.format_map({'new_name':str(key), \
                                'type':str(item[u'type'])})
        
        # add the union clause for the next column iteration
        union_clause = """ union select "{student_lookup_spelling}" as student_lookup, """\
                        .format_map({'student_lookup_spelling':student_lookup_spelling})
        consolidate_query += union_clause

    consolidate_query = consolidate_query[:-len(union_clause)]+";"
    return consolidate_query


def all_grades_query(cursor, grades_tables, grades_cols_json):
    """
    Writes a SQL query to drop the current all_grades table 
    and create a new one

    :param pg object cursor:
    :param list grades_tables: list of tables to include
    :param str grades_cols_json: name of a json file with mapping between
    old and new column names 
    :rtype: string
    """
    # json file with column name and type matchings
    with open(grades_cols_json, 'r') as f:
        new_cols_file = json.load(f)
    new_cols = new_cols_file[u'column_names']
    
    grades_query = """
    drop table if exists clean.all_grades;
    create table clean.all_grades as
    select "StudentLookup" as student_lookup,
    """
    for t in grades_tables:
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
                        grades_query += """
                        cast(nullif("{old_name}", '') as {type}) as {new_name},
                        """.format_map({'old_name':str(c), \
                                        'type':str(item[u'type']), \
                                        'new_name':str(key)})
                    else:
                        grades_query += """
                        cast("{old_name}" as {type}) as {new_name},
                        """.format_map({'old_name':str(c), \
                                        'type':str(item[u'type']),\
                                        'new_name':str(key)})
                    found = 1
                    break
            if found == 0: #column does not exist in current table
                grades_query += """
                cast(null as {type}) as {new_name},
                """.format_map({'new_name':str(key), \
                                'type':str(item[u'type'])})
        # grabs the district from the old table name
        # takes the first word split on camel case 
        district = re.findall(r'[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))', t)[0]
        grades_query += """
        '{district}' as district from "{table}"
        """.format_map({'district':district,'table':t})
        union_clause = """ union select "StudentLookup" as student_lookup, """
        grades_query += union_clause
    grades_query = grades_query[:-len(union_clause)]+";"
    return grades_query

def all_absences_query(cursor, absence_tables, absence_cols_json):
    """
    Writes a SQL query to drop the current all_grades table 
    and create a new one

    :param pg object cursor:
    :param list absence_tables: list of tables to include
    :param str absence_cols_json: name of a json file with mapping between
    old and new column names 
    :rtype: string
    """
    # json file with column name and type matchings
    with open(absence_cols_json, 'r') as f:
        new_cols_file = json.load(f)
    new_cols = new_cols_file[u'column_names']
    
    absence_query = """
    drop table if exists clean.all_absences;
    create table clean.all_absences as
    select "StudentLookup" as student_lookup,
    """
    for t in absence_tables:
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
                        absence_query += """
                        cast(nullif("{old_name}", '') 
                        as {type}) as {new_name}, """\
                        .format_map({'old_name':str(c), \
                                        'type':str(item[u'type']), \
                                        'new_name':str(key)})
                    else:
                        absence_query += """
                        cast("{old_name}" as {type}) as {new_name}, """\
                        .format_map({'old_name':str(c), \
                                        'type':str(item[u'type']),\
                                        'new_name':str(key)})
                    found = 1
                    break
            if found == 0: #column does not exist in current table
                absence_query += """
                cast(null as {type}) as {new_name}, """\
                .format_map({'new_name':str(key), \
                                'type':str(item[u'type'])})
        absence_query = absence_query[:-2] #removing last comma
        absence_query += """ from "{table}" """.format_map({'table':t})
        union_clause = """ union select "StudentLookup" as student_lookup, """
        absence_query += union_clause
    absence_query = absence_query[:-len(union_clause)]+";"
    return absence_query

def all_snapshots_query(cursor, snapshot_tables, snapshot_cols_json):
    """
    Writes a SQL query to drop the current all_snapshots table 
    and create a new one

    :param pg object cursor:
    :param list snapshot_tables: list of tables to include
    :param str snapshot_cols_json: name of a json file with mapping between 
    old and new column names
    :rtype: string 
    """
    # json file with column name and type matchings
    with open(snapshot_cols_json, 'r') as f:
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

def main():
    with postgres_pgconnection_generator() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""select table_name from information_schema.tables
            where table_schema='public' and table_name like
            'Districts%' and table_name not like '%dates%'""")
            snapshot_tables = cursor.fetchall()
            snapshot_tables = [a[0] for a in snapshot_tables]
            cursor.execute("""select table_name from information_schema.tables 
            where table_schema='public' and lower(table_name) 
            like '%absence%'""")
            absence_tables = cursor.fetchall()
            absence_tables = [a[0] for a in absence_tables]
            
            cursor.execute("""select table_name from information_schema.tables 
            where table_schema='public' and lower(table_name) like 
            '%grade%'""")
            grades_tables = cursor.fetchall()
            grades_tables = [a[0] for a in grades_tables]
            
            cursor.execute("""select table_name from information_schema.tables 
            where table_schema='public' and lower(table_name) like 
            '%teacher%'""")
            teachers_tables = cursor.fetchall()
            teachers_tables = [a[0] for a in teachers_tables]

            cursor.execute("""select table_name from information_schema.tables 
            where table_schema='public' and lower(table_name) like 
            '%testingaccom%'""")
            accommodations_tables = cursor.fetchall()
            accommodations_tables = [a[0] for a in accommodations_tables]

            table_names = get_specific_table_names(cursor, "StudentLookup")

            # execution of generated sql scripts
            cursor.execute(student_lookup_query(table_names))
            print('student lookup table built')
            cursor.execute(all_grades_query(cursor, grades_tables,
                                            "./json/grade_column_names.json"))
            print('all_grades table built')
            cursor.execute(all_absences_query(cursor, absence_tables,
                                              "./json/absence_column_names.json"))
            print('all_absences table built')
            cursor.execute(all_snapshots_query(cursor, snapshot_tables,
                                               "./json/snapshot_column_names.json"))
            print('all_snapshots table built')
            cursor.execute(all_generic_query(cursor, teachers_tables,
                                            "teachers_column_names.json",
                                            student_lookup_spelling = "studentLookup"))
            print('all_teachers table built')
            cursor.execute(all_generic_query(cursor, accommodations_tables,
                                            "accommodations_column_names.json"))
            print('all_accommodations table built')
        connection.commit()

if __name__ == '__main__':
    main()
