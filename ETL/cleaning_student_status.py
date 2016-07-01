import numpy as np
import pandas as pd
import psycopg2 as pg
import itertools
import json
import mvesc_utility_functions
from contextlib import contextmanager

def get_column_type(cursor, table_name, column_name):
    """
    Returns the data type of the given column in the given table
    :param pg cursor:
    :param string: table name
    :param string: column name'
    """
    my_query = "select data_type from information_schema.columns where "
    my_query += "table_name = (%s) and column_name = (%s) ;"
    cursor.execute(my_query, [table_name, column_name])
    column_type = cursor.fetchall()
    if len(column_type) > 0:
        column_type = column_type[0][0]
    return column_type

@contextmanager
def postgres_pgconnection_generator(pass_file="/mnt/data/mvesc/pgpass"):
    """
    Opens a connection with the mvesc PSQL database
    :rtype: pg.extensions.connection object connection
    """
    with open(pass_file, 'r') as f:
        passinfo = f.read()
    passinfo = passinfo.strip().split(':')
    host_address = passinfo[0]
    user_name = passinfo[2]
    name_of_database = passinfo[3]
    user_password = passinfo[4]
    yield pg.connect(host=host_address, database=name_of_database, \
                     user=user_name, password=user_password)

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
    my_query += "else {0} end; ".format(old_column_name)
    if replace:
        my_query += "alter table {0}.\"{1}\" ".format(schema_name,table_name)
        my_query += "rename column \"{0}\" to \"{1}\"; ".format(old_column_name, new_column_name)
    
    print(my_query)
    print(params)
    
    cursor.execute(my_query,params)

with postgres_pgconnection_generator() as connection:
    with connection.cursor() as cursor:
        clean_column(cursor, "student_status.json", "status_code", "all_snapshots", 
                     "status") 
    connection.commit()

