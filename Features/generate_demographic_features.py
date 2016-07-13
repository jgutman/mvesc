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
    sql_get_lookups = """select student_lookup from {schema}.{table} limit 1000;""".format(schema=schema, table=table)
    cursor.execute(sql_get_lookups)
    lookups = cursor.fetchall()
    lookups = [int(lp[0]) for lp in lookups]
    lookups = list(set(lookups))
    return lookups

def update_column_with_join(conn, source_schema, source_table, source_column, 
			schema='model', table='demographics', column='ethnicity', dtype='varchar(64)'):
    with conn.cursor() as cursor:
        sql_add_column = """alter table {schema}.{table} 
        add column {column} {dtype} default null;""".format(schema=schema, table=table, column=column, dtype=dtype)
        cursor.execute(sql_add_column); conn.commit();
        sql_join_cmd = """
        update {schema}.{table} t1 
        set {column}=
        ( 
            select {source_column} from {source_schema}.{source_table} t2
            where t2.student_lookup=t1.student_lookup
            order by {source_column} desc limit 1
        )
        where exists
        ( 
            select {source_column} from {source_schema}.{source_table} t2
            where t2.student_lookup=t1.student_lookup 
        );
        """.format(schema=schema, table=table, column=column, 
	source_schema=source_schema, source_table=source_table, source_column=source_column)
        cursor.execute(sql_join_cmd); conn.commit()
        print("""- updated "{schema}"."{table}"."{col}" from "{s_schema}"."{s_table}"."{s_col}"; """.format(
        col=column, schema=schema, table=table, s_schema=source_schema, s_table=source_table, s_col=source_column))
    return None
	

def get_columns_table2df(conn, table, schema='clean', columns='all', nrows=-1):
    """not useful not now"""
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
    
    table = "demographics"
    schema = 'model'
    sql_drop_demo_table = "drop table if exists {schema}.{table};".format(schema=schema, table=table) 
    # operations to create the table
    with postgres_pgconnection_generator() as connection:
        with connection.cursor() as cursor:
            student_lookups = get_outcome_student_lookup(cursor)
            columns = ['student_lookup', 'ethnicity', 'gender']
            
            if replace_table:
                cursor.execute(sql_drop_demo_table)
                connection.commit()
                df = pd.DataFrame(np.array([student_lookups]).transpose(), columns=['student_lookup'], dtype=np.int)
                #print("dataframe.head():\n", df.head())
                engine = postgres_engine_generator()
                df.to_sql(table, engine, schema=schema, index=False, if_exists='fail')    
            print("- Demographics created!")

            # Ethnicity
            source_schema, source_table, source_column = 'clean', 'all_snapshots', 'ethnicity'
            column, dtype='ethnicity', 'varchar(64)'
            update_column_with_join(connection, source_schema, source_table, source_column,               
                        schema=schema, table=table, column=column, dtype=dtype)
            # Gender
            source_schema, source_table, source_column = 'clean', 'all_snapshots', 'gender'
            column, dtype='gender', 'varchar(6)'
            update_column_with_join(connection, source_schema, source_table, source_column,
                        schema=schema, table=table, column=column, dtype=dtype)


            print(""""- {schema}"."{table}" finished!\n""".format(schema=schema, table=table))

''' backup code for review; will be deleted later
            column = 'gender'
            sql_add_column = """alter table {schema}.{table}
            add column {column} varchar(6) default null;""".format(schema=schema, table=table_name, column=column)
            cursor.execute(sql_add_column); connection.commit();
            sql_join_cmd = """
		update model.demographics t1 
		set gender=
		( 
			select gender from clean.all_snapshots t2
	  		where t2.student_lookup=t1.student_lookup 
  			order by gender desc limit 1
  		)
		where exists
		( 
			select gender from clean.all_snapshots t2
  			where t2.student_lookup=t1.student_lookup 
		);
            """
            cursor.execute(sql_join_cmd)
            connection.commit()

            print("Demographics Done!")

'''
 
