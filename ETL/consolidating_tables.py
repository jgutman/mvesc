import sys, os
pathname = os.path.dirname(sys.argv[0])
full_pathname = os.path.abspath(pathname)
split_pathname = full_pathname.split(sep="mvesc")
base_pathname = os.path.join(split_pathname[0], "mvesc")
parentdir = os.path.join(base_pathname, "ETL")
sys.path.insert(0,parentdir)

import pandas as pd
import numpy as np
import psycopg2 as pg
import itertools
import json
from mvesc_utility_functions import *
from contextlib import contextmanager

def student_lookup_query(table_names, clean_schema, raw_schema):
    """
    Writes a SQL query to drop the current all_student_lookups table 
    and create a new one using all the StudentLookup numbers in the 
    given list of tables

    :param list table_names: list of table names
    :param str clean_schema: schema to write tables to
    :param str raw_schema: schema to read tables from
    :rtype: string
    """

    my_query = "drop table if exists {}.all_student_lookups; ".format(
        clean_schema)
    my_query += "create table {}.all_student_lookups as ".format(clean_schema)
    for t in table_names:
        my_query += "select \"StudentLookup\" as student_lookup from "
        my_query += """ "{raw_schema}"."{table}" """.format(
            raw_schema=raw_schema, table=t)
        union_clause = " union \n"
        my_query += union_clause 
    my_query = my_query[:-len(union_clause)] + ";"
    return my_query

def consolidate_query(cursor, list_of_tables_to_consolidate, 
                      col_names_mapping_json, 
                      clean_schema, raw_schema,
                      consolidated_table_name, 
                      student_lookup_spelling = "StudentLookup"):
    """
    Generates a SQL query to drop the current version of the given table
    and create a new one, consolidating several similar tables

    :param pg object cursor:
    :param list list_of_tables_to_consolidate: list of tables to include
    :param str col_names_mapping_json: name of a json file with mapping between
    old and new column names, excluding student_lookup
    :param str consolidated_table_name: name of the resulting table
    :param str clean_schema:
    :param str raw_schema:
    :param str student_lookup_spelling: adjust this default value if 
        student lookup is spelled different in the original data
    :rtype: string
    """
    # json file with column name and type matchings
    with open(col_names_mapping_json, 'r') as f:
        new_cols_file = json.load(f)
    new_cols = new_cols_file[u'column_names']
    
    consolidate_query = """
    drop table if exists {clean_schema}.{consolidated_table};
    create table {clean_schema}.{consolidated_table} as
    select "{student_lookup_spelling}" as student_lookup,
    """.format_map({'clean_schema':clean_schema,
                    'consolidated_table':consolidated_table_name,
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
                        cast(nullif("{old_name}", '') as {type})
                        as {new_name},""".format_map(
                            {'old_name':str(c),'type':str(item[u'type']), \
                             'new_name':str(key)})
                    else:
                        consolidate_query += """
                        cast("{old_name}" as {type}) as {new_name}, """\
                            .format_map({'old_name':str(c), \
                                        'type':str(item[u'type']),\
                                        'new_name':str(key)})
                    found = 1
                    break
            if found == 0: #column does not exist in current table
                consolidate_query += """
                cast(null as {type}) as {new_name}, """\
                    .format_map({'new_name':str(key), \
                                'type':str(item[u'type'])})
        consolidate_query = consolidate_query[:-2]
        consolidate_query += """ from "{raw_schema}"."{table}" 
        """.format_map({'table':t,'raw_schema':raw_schema})

        # add the union clause for the next column iteration
        union_clause = """ union select "{student_lookup_spelling}" 
        as student_lookup, """.format_map(
            {'student_lookup_spelling':student_lookup_spelling})
        consolidate_query += union_clause

    consolidate_query = consolidate_query[:-len(union_clause)]+";"
    return consolidate_query


def all_grades_query(cursor, grades_tables, grades_cols_json, clean_schema, 
                     raw_schema):
    """
    Writes a SQL query to drop the current all_grades table 
    and create a new one

    :param pg object cursor:
    :param list grades_tables: list of tables to include
    :param str grades_cols_json: name of a json file with mapping between
    old and new column names 
    :param str clean_schema:
    :param str raw_schema: 
    :rtype: string
    """
    # json file with column name and type matchings
    with open(grades_cols_json, 'r') as f:
        new_cols_file = json.load(f)
    new_cols = new_cols_file[u'column_names']
    
    grades_query = """
    drop table if exists {schema}.all_grades;
    create table {schema}.all_grades as
    select "StudentLookup" as student_lookup,
    """.format(schema=clean_schema)
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
        '{district}' as district from "{raw_schema}"."{table}"
        """.format_map({'district':district,'table':t,'raw_schema':raw_schema})
        union_clause = """ union select "StudentLookup" as student_lookup, """
        grades_query += union_clause
    grades_query = grades_query[:-len(union_clause)]+";"
    return grades_query

def all_snapshots_query(cursor, snapshot_tables, snapshot_cols_json, 
                        clean_schema, raw_schema):
    """
    Writes a SQL query to drop the current all_snapshots table 
    and create a new one

    :param pg object cursor:
    :param list snapshot_tables: list of tables to include
    :param str snapshot_cols_json: name of a json file with mapping between 
    old and new column names
    :param str schema: clean schema name
    :rtype: string 
    """
    # json file with column name and type matchings
    with open(snapshot_cols_json, 'r') as f:
        new_cols_file = json.load(f)
    new_cols = new_cols_file[u'column_names']
    
    snapshot_query = """
    drop table if exists {schema}.all_snapshots;
    create table {schema}.all_snapshots as
    select "StudentLookup" as student_lookup,
    """.format(schema=clean_schema)
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
        cast(20{year} as int) as school_year from "{raw_schema}"."{table}"
        """.format_map({'year':t[9:11], 'table':t, 'raw_schema':raw_schema})
        union_clause = """ union select "StudentLookup" as student_lookup, """
        snapshot_query += union_clause
    snapshot_query = snapshot_query[:-len(union_clause)]+";"
    return snapshot_query

def main(argv):
    raw_schema = argv[0]
    clean_schema = argv[1]

    with postgres_pgconnection_generator() as connection:
        with connection.cursor() as cursor:
            
            cursor.execute("""select table_name from information_schema.tables
            where table_schema='{raw_schema}' and table_name like
            'Districts%' and table_name not like '%dates%'
            """.format(raw_schema=raw_schema))
            snapshot_tables = cursor.fetchall()
            snapshot_tables = [a[0] for a in snapshot_tables]

            cursor.execute("""select table_name from information_schema.tables 
            where table_schema='{raw_schema}' and lower(table_name) 
            like '%absence%'""".format(raw_schema=raw_schema))
            absence_tables = cursor.fetchall()
            absence_tables = [a[0] for a in absence_tables]
            
            cursor.execute("""select table_name from information_schema.tables 
            where table_schema='{raw_schema}' and lower(table_name) like 
            '%grade%'""".format(raw_schema=raw_schema))
            grades_tables = cursor.fetchall()
            grades_tables = [a[0] for a in grades_tables]
            
            cursor.execute("""select table_name from information_schema.tables 
            where table_schema='{raw_schema}' and lower(table_name) like 
            '%teacher%'""".format(raw_schema=raw_schema))
            teachers_tables = cursor.fetchall()
            teachers_tables = [a[0] for a in teachers_tables]

            cursor.execute("""select table_name from information_schema.tables 
            where table_schema='{raw_schema}' and lower(table_name) like 
            '%testingaccom%'""".format(raw_schema=raw_schema))
            accommodations_tables = cursor.fetchall()
            accommodations_tables = [a[0] for a in accommodations_tables]

            table_names = get_specific_table_names(cursor, "StudentLookup")
                                
            # execution of generated sql scripts
            cursor.execute(student_lookup_query(table_names, clean_schema,
                                                raw_schema))
            print('student lookup table built')
            # using specialized query to get district from table name
            cursor.execute(all_grades_query(cursor, grades_tables,
                                            os.path.join(base_pathname,'ETL',
                                            "json/grade_column_names.json"),
                                            clean_schema, raw_schema))
            print('all_grades table built')
            # using specialized query to get year from table name
            cursor.execute(all_snapshots_query(cursor, snapshot_tables,
                                            os.path.join(base_pathname,'ETL',
                                         "json/snapshot_column_names.json"),
                                               clean_schema, raw_schema))
            print('all_snapshots table built')
            cursor.execute(consolidate_query(cursor, teachers_tables,
                                            os.path.join(base_pathname,'ETL',
                                         "json/teachers_column_names.json"),
                                        clean_schema, raw_schema,
                                        "all_teachers",
                                         student_lookup_spelling = \
                                             "studentLookup"))
            print('all_teachers table built')
            cursor.execute(consolidate_query(cursor, absence_tables,
                                            os.path.join(base_pathname,'ETL',
                                            "json/absence_column_names.json"),
                                            clean_schema, raw_schema,
                                            "all_absences"))
            print('all_absences table built')
            cursor.execute(consolidate_query(cursor, accommodations_tables,
                                            os.path.join(base_pathname, 'ETL',
                                     "json/accommodations_column_names.json"),
                                     clean_schema, raw_schema,
                                     "all_accommodations"))
            print('all_accommodations table built')
        connection.commit()

if __name__ == '__main__':
    main()
