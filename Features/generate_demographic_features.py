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

def main():
    schema, table = "model" ,"demographics2"
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

            sql_create_index = "create index lookup_index on {schema}.{table}(student_lookup)".format(schema=schema, table=table)
            cursor.execute(sql_create_index)

            print(""" - Table "{schema}"."{table}" created!""".format(schema=schema, table=table))

            # Ethnicity
            source_schema, source_table = 'clean', 'all_snapshots'
            column_list = ['ethnicity', 'gender']
            column, dtype='ethnicity', 'varchar(64)'

            (cursor, table, column_list, source_table,
                                        source_schema = None, schema='model')

            update_column_with_join(cursor, table, [], source_schema, source_table, source_column,
                                    schema=schema, table=table, column=column, dtype=dtype)

            # Gender
            source_schema, source_table, source_column = 'clean', 'all_snapshots', 'gender'
            column, dtype='gender', 'varchar(64)'
            update_column_with_join(connection, source_schema, source_table, source_column,
                                    schema=schema, table=table, column=column, dtype=dtype)


            # cleaning due to messy all_snapshots
            sql_cmd = 'update model.demographics set gender=upper(left(trim(gender), 1));'
            cursor.execute(sql_cmd);
            sql_cmd = """
            UPDATE ONLY model.demographics
            SET ethnicity =
            case
            when trim(ethnicity)='*' then 'M' --'Multiracial'
            when trim(ethnicity)='1' then 'I' --'American Indian'
            when trim(ethnicity)='2' then 'A' --'Asian/Pacific Islander'
            when trim(ethnicity)='3' then 'B' --'Black'
            when trim(ethnicity)='4' then 'H' --'Hispanic'
            when trim(ethnicity)='5' then 'W' --'White'
            when trim(ethnicity)='6' then 'M' -- 'Multiracial'
            when trim(ethnicity)='7' then 'O' --'Other'
            when lower(trim(ethnicity))='i' then 'I' --'American Indian'
            when lower(trim(ethnicity))='a' then 'A' --'Asian/Pacific Islander'
            when lower(trim(ethnicity))='b' then 'B' --'Black'
            when lower(trim(ethnicity))='h' then 'H' --'Hispanic'
            when lower(trim(ethnicity))='w' then 'W' --'White'
            when lower(trim(ethnicity))='m' then 'M' --'Multiracial'
            when lower(trim(ethnicity))='p' then 'A' --'Asian/Pacific Islander'
            when lower(trim(ethnicity)) like '%american_ind%' then 'I' -- 'American Indian'
            when lower(trim(ethnicity)) like '%am_indian%' then 'I' -- 'American Indian'
            when lower(trim(ethnicity)) like '%hispanic%' then 'H' -- 'Hispanic'
            when lower(trim(ethnicity)) like '%indian%' then 'I' -- 'Hispanic'
            when lower(trim(ethnicity)) like '%alaskan%' then 'I' -- 'Hispanic'
            when lower(trim(ethnicity)) like '%asian%' then 'A' -- 'Asian/Pacific Islander'
            when lower(trim(ethnicity)) like '%pacific%' then 'A' -- 'Asian/Pacific Islander'
            when lower(trim(ethnicity)) like '%black%' then 'B' -- 'Black'
            when lower(trim(ethnicity)) like '%african%' then 'B' -- 'Black'
            when lower(trim(ethnicity)) like '%multi%' then 'M' -- 'Multiracial'
            when lower(trim(ethnicity)) like '%white%' then 'W' -- 'White'
            else trim(ethnicity)
            end;
            """
            cursor.execute(sql_cmd)
        connection.commit()

if __name__=='__main__':
    main()
