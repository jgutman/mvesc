import os, sys
from os.path import isfile, join, abspath, basename

pathname = os.path.dirname(sys.argv[0])
full_pathname = os.path.abspath(pathname)
split_pathname = full_pathname.split(sep="mvesc")
base_pathname = os.path.join(split_pathname[0], "mvesc")
parentdir = os.path.join(base_pathname, "ETL")
sys.path.insert(0,parentdir)
from mvesc_utility_functions import *


def create_feature_table(cursor, table, schema = 'model'):
    """
    The current feature table is dropped and re-created with a single column
    containing unique student lookups numbers, set as an index

    :param pg_cursor cursor:
    :param str table: feature table name 
    :param str schema: schema name for feature table
    """
    sql_drop = "drop table if exists {schema}.{table};"\
        .format(schema=schema, table=table)
    sql_create = """                                                     
    create table {schema}.{table} as                                     
    ( select distinct student_lookup                                     
    from clean.wrk_tracking_students                                   
    where outcome_category is not null                                 
    );""".format(schema=schema, table=table)
    cursor.execute(sql_drop);
    cursor.execute(sql_create);
    #sql_create_index = """                                               
    #create index lookup_index on {schema}.{table}(student_lookup)        
    #""".format(schema=schema, table=table)
    #cursor.execute(sql_create_index)
    print(""" - Table "{schema}"."{table}" created!"""\
          .format(schema=schema, table=table))
 
def sql_add_column(cursor, table, temp_table, new_col_names, schema = 'model'):
    """
    The table `schema.table` is replaced with `schema.table` 
    left joined with temp_table, essentially adding the columns of temp_table
    to the existing feature table.

    :param pg_cursor cursor:
    :param str table: existing feature table name - must have student_lookup
    :param str temp_table: temporary table with new features 
        and a student_lookup column
    :param list new_col_names: list of names of new column to add
    :param str schema: schema name for existing feature table
    """
    add_column_query = """
    alter table {schema}.{table} rename to {table}_temp;
    create table {schema}.{table} as
    select {schema}.{table}_temp.*, {new_col} from {schema}.{table}_temp
    left join {temp_table}
    on {schema}.{table}_temp.student_lookup = {temp_table}.student_lookup;
    drop table {schema}.{table}_temp;
    """.format_map({'schema':schema, 'table':table, 'temp_table':temp_table,
                    'new_col': ", ".join(new_col_names)})
    cursor.execute(add_column_query)
