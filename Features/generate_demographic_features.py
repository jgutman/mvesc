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
sys.path.append('../ETL/')
from mvesc_utility_functions import *


################ Functions ################
def get_outcome_student_lookup(cursor, table='wrk_tracking_students', schema='clean'):
    """ Get the student lookups in the outcome table
    param: sql.cursor cursor: cursor of sql from pgconnection
    param: str table: table name to pull the lookups
    return list lookups: student lookups in a list
    rtype: list [int]
    """
    sql_get_lookups = """select student_lookup from {schema}.{table} limit 200;""".format(schema=schema, table=table)
    cursor.execute(sql_get_lookups)
    lookups = cursor.fetchall()
    lookups = [int(lp[0]) for lp in lookups]
    return lookups
	
def get_column_for_lookups(cursor, lookups, table, column):
    """ Get a new column of values for certain lookups
    To Be Completed later
    """
    return None

def get_columns_table2df(conn, table, schema='clean', columns='all', nrows=-1):

    if columns=='all':
        sqlcmd = """select * from {schema}.{table}""".format(schema=schema, table=table)
    elif len(columns)>0:
        sqlcmd = 'select '
        for col in columns:
            sqlcmd = sqlcmd + col + ','
        sqlcmd = sqlcmd[:-1] + " from {schema}.{table}".format(schema=schema, table=table)
    else:
        print("Demographics: `columns`: wrong columns names!")
        return None
    print(sqlcmd)

    if nrows==-1:
        sqlcmd = sqlcmd + ';'
    elif nrows>0:
        sqlcmd = sqlcmd + " limit {nrows};".format(nrows=nrows)
    else:
        print("Demographics: `nrows`: wrong number of rows!")
        return None
    print(sqlcmd)
    df = pd.read_sql(sqlcmd, conn)
    print("Type: ", type(df))
    print("DF:\n", df)
    return df


################ main ################
if __name__=='__main__':
    # options of script
    parser = OptionParser()
    parser.add_option('-r', '--replace', dest = 'replace_table',\
    help = 'whether to replace existing table or not; default `False`')

    (options, args) = parser.parse_args()
    
    # default parameters or parsed
    replace_table = True
    if options.replace_table:
        if options.replace_table.lower() == 'false':
            replace_table = False

    table_name = "demographics"
    schema = 'model'
    sql_drop_demo_table = "drop table if exists {schema}.{table};".format(schema=schema, table=table_name) 
    # operations to create the table
    with postgres_pgconnection_generator() as connection:
        with connection.cursor() as cursor:
            student_lookups = get_outcome_student_lookup(cursor)
            columns = ['student_lookup', 'ethnicity', 'gender']
#            demographics = get_columns_table2df(connection, table="all_snapshots", columns=columns,nrows=10)
#            print("demo:\n", demographics)
            
            if replace_table:
                cursor.execute(sql_drop_demo_table)
                connection.commit()
                df = pd.DataFrame(np.array([student_lookups]).transpose(), columns=['student_lookup'], dtype=np.int)
                print("dataframe.head():\n", df.head())
                engine = postgres_engine_generator()
                df.to_sql(table_name, engine, schema=schema, index=False, if_exists='fail')    
            print("Demographics created!")

            # column ethnicity
            column = 'ethnicity'
            sql_add_column = """alter table {schema}.{table} 
	    add column {column} varchar(64) default null;""".format(schema=schema, table=table_name, column=column)
            cursor.execute(sql_add_column)
            
            sql_join_cmd = """"""
            connection.commit()

            # column gender
            column = 'gender'
            sql_add_column = """alter table {schema}.{table}
            add column {column} varchar(6) default null;""".format(schema=schema, table=table_name, column=column)
            cursor.execute(sql_add_column)
            connection.commit()

            print("Demographics Done!")


 
