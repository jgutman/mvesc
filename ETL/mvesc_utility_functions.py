"""
Utility Functions for MVESC

Team Ohio, DSSG 2016
"""
"""
Top functions:
1. `postgres_engine_generator()`: returns a `sqlalchemy` engine, similar to function 2;
2. `postgres_pgconnection_generator()`: returns a `psycopg2` connection, similar to function 1;
3. `get_all_table_names(schema='public')`: returns all table names as a list from a schema
4. `get_column_names(table, schema='public')`: returns all column names as a list from a schema
5. `read_table_to_df(table, schema='public', nrows=20)`: returns a pd.dataframe of first nrows;
"""
import numpy as np
import pandas as pd
import psycopg2 as pg
import re
from sqlalchemy import create_engine
import sqlalchemy
import sys
import os
import json


############ ETL Functions ############
def postgres_engine_generator(pass_file="/mnt/data/mvesc/pgpass"):
    """ Generate a sqlalchemy engine to mvesc database
    Note: you can only run it on the mvesc server
    :param str pass_file: file with the credential information
    :return sqlalchemy.engine object engine: object created  by create_engine() in sqlalchemy
    :rtype sqlalchemy.engine
    """
    with open(pass_file, 'r') as f:
        passinfo = f.read()
    passinfo = passinfo.strip().split(':')
    host_address = passinfo[0]
    port = passinfo[1]
    user_name = passinfo[2]
    name_of_database = passinfo[3]
    user_password = passinfo[4]
    sql_eng_str = "postgresql://"+user_name+":"+user_password+"@"+host_address+'/'+name_of_database
    engine = create_engine(sql_eng_str)
    return engine

def postgres_pgconnection_generator(pass_file="/mnt/data/mvesc/pgpass"):
    """ Generate a psycopg2 connector
    Note: you can only run it on the mvesc server
    :param str pass_file: file with the credential information
    :return ps.engine object engine: object created  by create_engine() in sqlalchemy
    :rtype sqlalchemy.engine
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



############ Reterive Database Information ############
def get_all_table_names(schema='public'):
    """ Get all the table names as a list from a `schema` in mvesc
    
    :param str schema: schema name in the database
    :return list all_table_names: all table names in a `schema` in mvesc database
    """
    sqlcmd = "SELECT table_name FROM information_schema.tables WHERE table_schema = '%s'" % schema
    engine = postgres_engine_generator()
    conn = engine.raw_connection()
    all_table_names = list(pd.read_sql(sqlcmd, conn).table_name)
    conn.close()
    return all_table_names

def get_column_names(table, schema='public'):
    """Get column names of a table  in a schema
    
    :param pg.extensions.connection object connection: sql connection
    :param string table: table name in the database
    :rtype: list 
    """
    connection = postgres_pgconnection_generator()
    columns = pd.read_sql("SELECT column_name FROM information_schema.columns \
    WHERE table_name = '%s' and table_schema='%s'" % (table, schema), connection)
    return list(columns.iloc[:, 0])

def read_table_to_df(table_name, schema='public', nrows=20):
    """ Read the first n rows of a table
    
    :param str table_name: Name of table to read in
    :param int nrows: number of rows to read in; default 20; -1 means all rows
    :return: a pandas.dataframe object with n-rows
    :rtype: pandas.dataframe
    """
    connection = postgres_pgconnection_generator()
    sqlcmd = "SELECT * FROM %s.\"%s\" LIMIT %s;" % (schema, table_name, str(int(nrows)))
    if nrows == -1:
        sqlcmd = "SELECT * FROM %s.\"%s\";" % (schema, table_name)
    df = pd.read_sql(sqlcmd, connection)
    return df

############ Upload file or directory to postgres (not useful in most cases)############### 
def read_csv_noheader(filepath):
    """ Read a csv file with no header

    :param str filepath: file path name
    :return pandas.DataFrame with header 'col1', 'col2', ...
    :rtype pandas.DataFrame
    """
    df = pd.read_csv(filepath, header=None, low_memory=False) # read csv data with no header
    colnames = {i:'col'+str(i) for i in df.columns} # rename column names of col0, col1, col2, ...
    df = df.rename(columns=colnames)
    return df

def csv2postgres_file(filepath, header=False, nrows=-1, if_exists='fail', schema="raw"):
    """ Upload csv file to postgres database

    :param str filepath: file path name
    :param bool header: True means there is header;
    :return str table_name: table name of the sql table processed
    :rtype str
    """
    # read the data frame with or without header
    if header:
        df = pd.read_csv(filepath, low_memory=False)
    else:
        df = read_csv_noheader(filepath) # header: col0, col1, col2

    # postgres engine for connection and operations
    engine = postgres_engine_generator()

    # get existing table names in the DB and schema
    sqlcmd_table_names = "SELECT table_name FROM information_schema.tables WHERE table_schema = '%s'" % schema
    conn = engine.raw_connection()
    all_table_names = list(pd.read_sql(sqlcmd_table_names, conn).table_name)
    conn.close()

    #write the data frame to postgres
    file_name = filepath.split('/')[-1]
    file_table_names = json.load(open('file_to_table_name.json','r')) # load json of mapping from filenames to table names
    table_name = file_table_names[file_name] # get the table name

    # check existing tables in sql first to avoid errors
    if table_name not in all_table_names or if_exists=='replace':
        if nrows==-1: # upload all rows
            df.to_sql(table_name, engine, schema=schema, index=False, if_exists=if_exists)
        else: # upload the first n rows
            df.iloc[:nrows, :].to_sql(table_name, engine, schema=schema, index=False, if_exists=if_exists)
    else:
        print("Table already in mvesc:", table_name)
    return table_name


def csv2postgres_dir(directory, header=False, nrows=-1, if_exists='fail', schema='raw'):
    """ Upload a directory of csv files to postgres database

    :param str filepath: file path name
    :param bool header: True means there is header;
    :return str table_names: table names of the sql tables processed
    :rtype str
    """
    data_dir = directory
    if data_dir[-1]!='/':
        data_dir = data_dir + '/'
    data_file_names = os.listdir(data_dir) # get all filenames in a directory
    # full path name of filenames
    fnames = [data_dir + fn for fn in data_file_names]
    table_names = []
    for filepath in fnames:
        print("working on ", filepath)
        tab_name = csv2postgres_file(filepath, header=header, nrows=nrows, if_exists=if_exists, schema=schema)
        table_names.append(tab_name)
    return table_names
