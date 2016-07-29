""" Generate Demographic Features
Procedures:
1. Read from outcome table to get student_lookups;
2. Generate `model.demographics` from `clean.all_snapshots`
"""
import os, sys
import numpy as np
import pandas as pd

pathname = os.path.dirname(sys.argv[0])
full_pathname = os.path.abspath(pathname)
split_pathname = full_pathname.split(sep="mvesc")
base_pathname = os.path.join(split_pathname[0], "mvesc")
parentdir = os.path.join(base_pathname, "ETL")
sys.path.insert(0,parentdir)

from mvesc_utility_functions import *
from feature_utilities import update_column_with_join

def create_temp_gender_table(cursor, schema='clean', table='all_snapshots',
    temp='single_gender'):

    query_rank_gender_by_count = """create temporary table {temp} as
    (select student_lookup, gender, count(gender),
        rank() over (
            partition by student_lookup
            order by count(gender) desc)
    from {schema}.{table}
    group by student_lookup, gender);
    """.format(schema=schema, table=table, temp=temp)

    query_drop_rows = """delete from {temp}
    where rank > 1;""".format(temp=temp)

    cursor.execute(query_rank_gender_by_count)
    cursor.execute(query_drop_rows)

def main():
    schema, table = "model" ,"demographics"
    source_schema, source_table = "clean", "all_snapshots"

    with postgres_pgconnection_generator() as connection:
        with connection.cursor() as cursor:
            # drop and create table
            sql_drop = "drop table if exists {schema}.{table};".format(schema=schema, table=table)

            sql_create="""create table {schema}.{table} as
            ( select distinct student_lookup
              from clean.wrk_tracking_students
              where outcome_category is not null
            );""".format(schema=schema, table=table)

            cursor.execute(sql_drop)
            cursor.execute(sql_create)

            print(""" - Table "{schema}"."{table}" created!""".format(schema=schema, table=table))

            source_schema, source_table = 'clean', 'all_snapshots'

            # add ethnicity - all multiples have already been converted to
            # M for Multiracial in cleaning_all_snapshots.sql
            column_list = ['ethnicity']
            update_column_with_join(cursor, table, column_list, source_table,
                                        source_schema, schema)

            # add gender - if multiple genders select the most frequent
            temp_table = 'single_gender'
            create_temp_gender_table(cursor, schema=source_schema,
                table=source_table, temp=temp_table)
            column_list = ['gender']
            update_column_with_join(cursor, table, column_list, temp_table,
                                        None, schema)

            connection.commit()

if __name__=='__main__':
    main()
