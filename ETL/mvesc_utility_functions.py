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
from contextlib import contextmanager

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

@contextmanager
def postgres_pgconnection_generator(pass_file="/mnt/data/mvesc/pgpass"):
    """ Generate a psycopg2 connection (to use in a with statement)
    Note: you can only run it on the mvesc server
    :param str pass_file: file with the credential information
    :yield pg.connection generator: connection to database 
    """
    with open(pass_file, 'r') as f:
        passinfo = f.read()
    passinfo = passinfo.strip().split(':')
    host_address = passinfo[0]
    port = passinfo[1]
    user_name = passinfo[2]
    name_of_database = passinfo[3]
    user_password = passinfo[4]
    yield pg.connect(host=host_address, database=name_of_database, user=user_name, password=user_password)



############ Reterive Database Information ############
def get_all_table_names(cursor, schema='public'):
    """ Get all the table names as a list from a `schema` in mvesc
    
    :param pg cursor object cursor: cursor for psql database
    :param str schema: schema name in the database
    :return list all_table_names: all table names in a `schema` in mvesc database
    """
    sqlcmd = "SELECT table_name FROM information_schema.tables WHERE table_schema = (%s)"
    cursor.execute(sqlcmd, [schema])
    all_table_names = [t[0] for t in cursor.fetchall()]
    return all_table_names

def get_specific_table_names(cursor, column_name):
    """
    Retrieves the list of names of tables in the database which have StudentLookups
    :param pg object cursor: cursor in psql database                       
    :param string column_name: column that should be in each of the returned tables
    :rtype: list of strings                                       
    """
    table_names = get_all_table_names(cursor)
    to_remove = []
    for t in table_names:
        if column_name not in get_column_names(cursor,t):
            to_remove.append(t)
    for t in to_remove:
        table_names.remove(t)
    return table_names

def get_column_names(cursor, table, schema='public'):
    """Get column names of a ntable  in a schema
    
    :param pg cursor object cursor: cursor for psql database
    :param string table: table name in the database
    :param str schema: schema name in database
    :rtype: list 
    """
    cursor.execute("SELECT column_name FROM information_schema.columns \
    WHERE table_name = (%s) and table_schema=(%s)", [table, schema])
    columns = cursor.fetchall()
    return [c[0] for c in columns]

def read_table_to_df(connection, table_name, schema='public', nrows=20):
    """ Read the first n rows of a table
    
    :param pg connection object connection: connection to psql database
    :param str table_name: Name of table to read in
    :param int nrows: number of rows to read in; default 20; -1 means all rows
    :return: a pandas.dataframe object with n-rows
    :rtype: pandas.dataframe
    """
    if nrows == -1:
        sqlcmd = "SELECT * FROM %s.\"%s\";" % (schema, table_name)
    else:
        sqlcmd = "SELECT * FROM %s.\"%s\" LIMIT %s;" % (schema, table_name, str(int(nrows)))
    df = pd.read_sql(sqlcmd, connection)
    return df

def get_column_type(cursor, table_name, column_name):
    """
    Returns the data type of the given column in the given table
    :param pg cursor:
    :param string: table name
    :param string: column name
    """
    my_query = "select data_type from information_schema.columns where table_name = (%s) and column_name =(%s);"
    cursor.execute(my_query, [table_name, column_name])
    column_type = cursor.fetchall()
    if len(column_type) > 0:
        column_type = column_type[0][0]
    return column_type

def clean_column(cursor, values, old_column_name, table_name, \
                 new_column_name=None, schema_name='clean', replace = 1):
    """
    Cleans the given column by replacing values according to the given json file, which 
    should be in the form:
    {
    "desired_name":["existing_name1", "existing_name2", ...],
    "desired_name":["existing_name1", "existing_name2", ...],
    ...
    }

    By default, replaces the current column with the cleaned values.
    If replace=0, should provide a distinct new_column_name to avoid duplicates.
    In the json all values should be lowercase.

    :param pg object cursor: cursor in psql database
    :param string values: name of a json file
    :param string old_column_name:
    :param string new_column_name:
    :param string table_name:
    :param string schema_name:
    :param bool replace: if yes, replaces the old_column_name and re-names it, if no makes a new column called new_column_name
    """
    col_type = get_column_type(cursor, table_name, old_column_name)

    if new_column_name is None:
        new_column_name = old_column_name

    my_query = "alter table {0}.\"{1}\" ".format(schema_name,table_name)
    if replace:
        my_query += "alter column \"{0}\" ".format(old_column_name)
        my_query += "type {} using case ".format(col_type)
    else:
        my_query += "add column \"{0}\" {1}; ".format(new_column_name, col_type)
        my_query += "alter table {0}.\"{1}\" ".format(schema_name,table_name)
        my_query += "alter column \"{0}\" ".format(new_column_name)
        my_query += "type {} using case ".format(col_type)

    params = {}

    with open(values, 'r') as f:
        json_dict = json.load(f)

    count = 0;
    for new_name, old_name_list in json_dict.items():
        my_query += "when "
        or_clause = "or \n"
        for old_name in old_name_list:
            my_query += "lower({0}) like %(item{1})s ".format(old_column_name,count)
            my_query += or_clause
            params['item{0}'.format(count)] = str(old_name)
            count +=1
        my_query = my_query[:-len(or_clause)]
        my_query += "then  %(item{0})s \n".format(count)
        params['item{0}'.format(count)] = str(new_name)
        count += 1
    my_query = my_query[:-20]
    my_query += "else {0} end; ".format(old_column_name)
    if replace:
        my_query += "alter table {0}.\"{1}\" ".format(schema_name,table_name)
        my_query += "rename column \"{0}\" to \"{1}\"; ".format(old_column_name, new_column_name)
    cursor.execute(my_query,params)

with postgres_pgconnection_generator() as connection:
    with connection.cursor() as cursor:
        clean_column(cursor, "student_status.json", "status_code", "all_snapshots",
                     "status", replace=0)
    connection.commit()

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
