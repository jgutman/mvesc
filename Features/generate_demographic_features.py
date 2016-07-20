""" Generate Demographic Features
Procedures:
1. Read from outcome table to get student_lookups;
2. Generate `model.demographics` from `clean.all_snapshots`
"""
import os
from os.path import isfile, join, abspath, basename
from optparse import OptionParser
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
import sqlalchemy
import json

import sys
parentdir = os.path.abspath('/home/xcheng/mvesc/ETL')
sys.path.insert(0,parentdir)
from mvesc_utility_functions import *
def update_column_with_join(conn, source_schema, source_table, source_column, 
                            schema='model', table='demographics', column='ethnicity', dtype='varchar(64)'):
    """ Update column using join to match another table
    :param pg.connection conn: pg connection
    :param str source_schema: schema of source
    :param str source_table: table of source
    :param str source_column: column of source
    :param str schema: schema to update
    :param str table: table to update
    :param str column: column to update
    :param str dtype: data type of new column
    :return None
    """
    with conn.cursor() as cursor:
        sql_add_column = """alter table {schema}.{table} add column {column} {dtype} default null;""".format(
            schema=schema, table=table, column=column, dtype=dtype)
        cursor.execute(sql_add_column); conn.commit()
        sql_join_cmd = """
        update {schema}.{table} t1 
        set {column}=
        ( 
            select {source_column} from {source_schema}.{source_table} t2
            where t2.student_lookup=t1.student_lookup and t2.{source_column} is not null
            order by {source_column} desc limit 1
        );
        """.format(schema=schema, table=table, column=column, 
        source_schema=source_schema, source_table=source_table, source_column=source_column)
        cursor.execute(sql_join_cmd); conn.commit()
        print(""" - updated "{schema}"."{table}"."{col}" from "{s_schema}"."{s_table}"."{s_col}"; """.format(
        col=column, schema=schema, table=table, s_schema=source_schema, s_table=source_table, s_col=source_column))
    return None



if __name__=='__main__':
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
            cursor.execute(sql_drop); connection.commit()
            cursor.execute(sql_create); connection.commit()
            sql_create_index = "create index lookup_index on {schema}.{table}(student_lookup)".format(schema=schema, table=table)
            cursor.execute(sql_create_index)
            connection.commit()
            print(""" - Table "{schema}"."{table}" created!""".format(schema=schema, table=table))

            # Ethnicity
            source_schema, source_table, source_column = 'clean', 'all_snapshots', 'ethnicity'
            column, dtype='ethnicity', 'varchar(64)'
            update_column_with_join(connection, source_schema, source_table, source_column,
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
            cursor.execute(sql_cmd); connection.commit()

