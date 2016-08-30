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
import os

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

def execute_sql_script(sql_script, pass_file="/mnt/data/mvesc/pgpass"):
    """ Executes the given sql script
    Note: you can only run it on the mvesc server
    :param str sql_script: filename of an sql script
    :param str pass_file: file with the credential information
    """
    with open(pass_file, 'r') as f:
        passinfo = f.read()
    passinfo = passinfo.strip().split(':')
    host_address = passinfo[0]
    port = passinfo[1]
    user_name = passinfo[2]
    name_of_database = passinfo[3]
    user_password = passinfo[4]
    conn_info = "postgresql://"+user_name+":"+user_password+"@"+host_address+'/'+name_of_database
    os.system("psql -d {0} -f {1}".format(conn_info,sql_script))


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
def get_all_table_names(cursor, schema): # defaulted to public
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
    Retrieves the list of names of tables in the database which contain a
    column with the given name

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

def read_table_to_df(connection, table_name, columns=['*'], schema='public', nrows=20):
    """ Read the first n rows of a table

    :param pg connection object connection: connection to psql database
    :param str table_name: Name of table to read in
    :param int nrows: number of rows to read in; default 20; -1 means all rows
    :return: a pandas.dataframe object with n-rows
    :rtype: pandas.dataframe
    """
    sqlcmd = """SELECT {columns} FROM "{schema}"."{table}" """.format (columns=",".join(columns), schema=schema, table=table_name)
    if nrows==-1:
        sqlcmd = sqlcmd + ';'
    else:
        sqlcmd = sqlcmd + " limit {nrows};".format(nrows=str(nrows))
    df = pd.read_sql(sqlcmd, connection)
    return df

def get_column_type(cursor, table_name, column_name):
    """
    Returns the data type of the given column in the given table
    :param pg cursor:
    :param string: table name
    :param string: column name
    """
    column_type_query = "select data_type from information_schema.columns where table_name = (%s) and column_name =(%s);"
    cursor.execute(column_type_query, [table_name, column_name])
    column_type = cursor.fetchall()
    if len(column_type) > 0:
        column_type = column_type[0][0]
    return column_type

def clean_column(cursor, values, old_column_name, table_name,
                 new_column_name=None, schema_name='clean',
                 replace = 1, exact = 1):
    """
    Cleans the given column by replacing values according to the given
    json file, which should be in the form:
    {
    "desired_name":["existing_name1", "existing_name2", ...],
    "desired_name":["existing_name1", "existing_name2", ...],
    ...
    }

    Any existing name not in the json file is left unchanged.
    By default, replaces the current column with the cleaned values.
    If replace=False, should provide a distinct new_column_name to avoid duplicates.
    In the json all values should be lowercase.

    :param pg object cursor: cursor in psql database
    :param string values: name of a json file
    :param string old_column_name:
    :param string new_column_name:
    :param string table_name:
    :param string schema_name:
    :param bool replace: if yes, replaces the old_column_name and re-names it, if no makes a new column called new_column_name
    :param bool exact: if yes, pattern matching will require exact matches to values in json
         if no, will append % to each side, allowing wildcards on each side
    """
    col_type = get_column_type(cursor, table_name, old_column_name)
    if not col_type:
        print("old column does not exist")
        return
    if not new_column_name:
        new_column_name = old_column_name

    clean_col_query = """alter table {0}."{1}" """.format(schema_name, table_name)
    if replace:
        clean_col_query += """alter column "{old}" type {type} using case """\
            .format(old=old_column_name, type=col_type)
    else:
        clean_col_query += """
        add column "{new_name}" {type};
        alter table {schema}."{table}"
        alter column "{new_name}" type {type} using case
        """.format(new_name=new_column_name, type=col_type,
                    schema=schema_name, table=table_name)

    params = {} # dictionary to hold parameters for cursor.execute()
    with open(values, 'r') as f:
        json_dict = json.load(f)

    count = 0; # to identify parameters for cursor.execute()
    for new_name, old_name_list in json_dict.items():
        clean_col_query += "when "
        or_clause = "or "
        for old_name in old_name_list:
            clean_col_query += """
            lower({old}) like %(item{n})s
            """.format(old=old_column_name, n=count)
            clean_col_query += or_clause
            if exact:
                params['item{0}'.format(count)] = '{}'.format(old_name)
            else:
                params['item{0}'.format(count)] = '%{}%'.format(old_name)
            count +=1
        clean_col_query = clean_col_query[:-len(or_clause)]
        clean_col_query += "then  %(item{0})s \n".format(count)
        params['item{0}'.format(count)] = str(new_name)
        count += 1
    clean_col_query += "else {0} end; ".format(old_column_name)

    if replace and old_column_name != new_column_name:
        clean_col_query += """
        alter table {schema}.{table} rename column "{old}" to "{new}"
        """.format(schema=schema_name, table=table_name,
                    old=old_column_name, new=new_column_name)
    cursor.execute(clean_col_query, params)

############ Functions to explore model/feature results ###########
def barplot_df(dfbar, figname=None, save=False, savedir='./',
               name_column='feature', value_column='importance',
               xlabel='Importance', ylabel='Feature', title='', fontsize=16, figsize=(8, 6),
               style='ggplot', kind='barh', dpi=500):
    """
    Bar Plot of a data frame: the reason to have this is to save time to make better plots

    :param pd.dataframe df: data frame has at least 1 column of labels and 1 column of numeric values
    :param str figname: figure name; None means default name
    :param bool save: whether to save the fig
    :param str savedir: directory to save the fig
    :param str name_column: column name of the label
    :param str value_column: column name of the values
    :param str xlabel, ylabel, title:
    :param int fontsize: fontsize for labels and titles
    :param tuple int figsize: figure size
    :param str style: plot style, 'ggplot', 'fivethirtyeight', etc
    :param str kind: bar plot kind, `bar`, `barh`
    :param int dpi: resolution, the larger the better
    :return str fn: figure name; if save==False, return None
    """
    plt.style.use(style)
    df = dfbar[[value_column]]
    df.index = dfbar[name_column]
    df = df.sort_values(by=[value_column], ascending=False)
    ax = df.iloc[::-1,:].plot(kind=kind, title=title, figsize=figsize, fontsize=fontsize, legend=False)
    plt.ylabel(ylabel, fontsize=fontsize)
    plt.xlabel(xlabel, fontsize=fontsize)
    plt.tight_layout()
    if save==True:
        if figname==None:
            fn = os.path.join(savedir, 'feature_importance.png')
        else:
            fn = str(figname)
        plt.savefig(fn, dpi=dpi)
        return(fn)
    else:
        return(None)


def read_model_topN_feature_importance(filename, topN=10, schema='model', table='feature_scores'):
    """
    Read top N feature importance from features scores table
    :param str filename: filename in the filename column
    :param int topN: top N features to read
    :param str schema: schema name
    :param str table: table name
    :return df
    :rtype pd.DataFrame
    """
    with postgres_pgconnection_generator() as conn:
        conn.autocommit =True
        sqlcmd="""
        select * from {s}.{t}
        where filename like '%{f}%'
        order by importance desc
        limit {topN};
        """.format(s=schema, t=table, f=filename, topN=topN)
        df = pd.read_sql_query(sqlcmd, conn)
    return df


def barplot_feature_importance(filename, topN=10, schema='model', table='feature_scores',
                               figname=None, save=False, savedir='./',
                               name_column='feature', value_column='importance',
                               xlabel='Importance', ylabel='Feature', title='',
                               fontsize=16, figsize=(8, 6),
                               style='ggplot', kind='barh', dpi=500):
    """
    Barplot feature importance for a specific filename in table `model.feature_scores`

    :param str filename: filename in the filename column
    :param int topN: top N features to read
    :param str schema: schema name
    :param str table: table name
    :param str figname: figure name; None means default name
    :param bool save: whether to save the fig
    :param str savedir: directory to save the fig
    :param str name_column: column name of the label
    :param str value_column: column name of the values
    :param str xlabel, ylabel, title:
    :param int fontsize: fontsize for labels and titles
    :param tuple int figsize: figure size
    :param str style: plot style, 'ggplot', 'fivethirtyeight', etc
    :param str kind: bar plot kind, `bar`, `barh`
    :param int dpi: resolution, the larger the better
    :return str saved_figname: if save=True, return figure name; if save==False, return None
    :rtype str
    """
    df = read_model_topN_feature_importance(filename, topN=topN, schema=schema, table=table)
    saved_figname = barplot_df(df, figname=figname, save=save, savedir=savedir,
               name_column=name_column, value_column=value_column,
               xlabel=xlabel, ylabel=ylabel, title=title,
               fontsize=fontsize, figsize=figsize,
               style=style, kind=kind, dpi=dpi)
    return(saved_figname)

############ Functions to data frame processing ###################
def df2num(rawdf, drop_reference = True, dummify = True,
        drop_entirely_null = True):
    """ Convert data frame with numeric variables and strings
    to numeric dataframe, and drops reference category optionally

    :param pd.dataframe rawdf: raw data frame
    :param boolean drop_reference: whether to drop the most frequent category
    :param boolean dummify: whether to dummify string variables or leave as is
    :param boolean drop_entirely_null: whether to remove features that are
        null for everybody in the dataset

    :returns pd.dataframe df: a data frame with strings converted to dummies,
        null columns removed, and other columns unchanged
    :rtype: pd.dataframe
    Rules:
    - 1. numeric columns unchanged;
    - 2. strings converted to dummies;
    - 3. the most frequent string is taken as reference
    - 4. new column name is: "ColumnName_Category"
        (e.g., column 'gender' with 80 'M' and 79 'F' and 10 NULL;
        the dummy column is 'gender_F', or 'gender_isnull')
    """
    if drop_entirely_null:
        rawdf.dropna(axis='columns', how='all', inplace=True)
    if not dummify:
        return rawdf
    numeric_df = rawdf.select_dtypes(include=[np.number])
    str_columns = [col for col in rawdf.columns if col not in numeric_df.columns]
    if len(str_columns) > 0:
        dummy_col_df = pd.get_dummies(rawdf[str_columns], dummy_na=True)
        numeric_df = numeric_df.join(dummy_col_df)
        if drop_reference:
            most_frequent_values = rawdf[str_columns].mode().loc[0].to_dict()
            reference_cols = ["{}_{}".format(key, value) for key, value in
                most_frequent_values.items()]
            numeric_df.drop(reference_cols, axis=1, inplace=True)
    return numeric_df

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
    file_table_names = json.load(open('./json/file_to_table_name.json','r')) # load json of mapping from filenames to table names
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

# copied directly from excel2postgres python file
def df2postgres(df, table_name, nrows=-1, if_exists='fail', schema='raw'):
    """ dump dataframe object to postgres database

    :param pandas.DataFrame df: dataframe
    :param int nrows: number of rows to write to table;
    :return str table_name: table name of the sql table
    :rtype str
    """
    # create a postgresql engine to wirte to postgres
    engine = postgres_engine_generator()

    #write the data frame to postgres
    if nrows==-1:
        df.to_sql(table_name, engine, schema=schema, index=False, if_exists=if_exists)
    else:
        df.iloc[:nrows, :].to_sql(table_name, engine, schema=schema, index=False, if_exists=if_exists)
    return table_name
