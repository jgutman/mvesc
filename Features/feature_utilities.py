import os, sys
from os.path import isfile, join, abspath, basename

pathname = os.path.dirname(sys.argv[0])
full_pathname = os.path.abspath(pathname)
split_pathname = full_pathname.split(sep="mvesc")
base_pathname = os.path.join(split_pathname[0], "mvesc")
parentdir = os.path.join(base_pathname, "ETL")
sys.path.insert(0,parentdir)
from mvesc_utility_functions import *


def create_feature_table(cursor, table, schema = 'model', replace = False):
    """
    The current feature table is dropped and re-created with a single column
    containing unique student lookups numbers, set as an index

    :param pg_cursor cursor:
    :param str table: feature table name 
    :param str schema: schema name for feature table
    :param bool replace: if true the table will be replaced, 
        if false an existing table will not be altered
    """
    cursor.execute("""
    select count(*) from information_schema.tables
    where table_schema = '{schema}' and table_name = '{table}'
    """.format_map({'schema':schema,'table':table}))
    table_exists = cursor.fetchall()[0][0]
    if (not table_exists) or replace:
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
        sql_create_index = """                                               
        create index student_lookup_index on {schema}.{table}(student_lookup)
        """.format(schema=schema, table=table)
        cursor.execute(sql_create_index)
        print(""" - Table {schema}.{table} created!"""\
        .format(schema=schema, table=table))

def update_column_with_join(cursor, table, column_list, source_table, 
                            source_column_list = None, source_schema = None,
                            schema='model'):
    """ 
    Update column using join to match another table                 
    :param pg.cursor cursor: pg cursor
    :param str table: table to update
    :param str column_list: list of column to update
    :param str source_table: table of source
    :param str source_column_list: list of source columns - column_list default 
        if not None then must be the same length as column_list
    :param str source_schema: schema of source - None default for temp tables
    :param str schema: schema to update - 'model' default
    :return None:                      
    """
    # setting defaults
    if not source_column_list:
        source_column_list = column_list
    if not source_schema:
        source_schema_and_table = source_table
    else:
        source_schema_and_table = source_schema+'.'+source_table
    
    # making columns
    for ind,c in enumerate(column_list):
        dtype = get_column_type(cursor, source_table, source_column_list[ind])
        
        sql_add_column = """
        alter table {schema}.{table} add column {column} 
        {dtype} default null;
        """.format( schema=schema, table=table, column=c, dtype=dtype)
        cursor.execute(sql_add_column);

    # joining columns
    sql_join_cmd = """
    alter table {schema}.{table} rename to {table}_temp;
    create table {schema}.{table} as
    select {schema}.{table}_temp.*, {source_cols} from {schema}.{table}_temp t1
    left join {source_schema_and_table} t2
    on {schema}.{table}_temp.student_lookup = {temp_table}.student_lookup;
    drop table {schema}.{table}_temp;
    """.format(schema=schema, table=table, column=column,
               source_schema_and_table=source_schema_and_table, 
               source_column=source_column)
    cursor.execute(sql_join_cmd)
    print(""" - updated {schema}.{table}.{col} 
    from {s_schema_and_table}.{s_col}; """\
          .format(col=column, schema=schema, table=table, 
                 s_schema_and_table=source_schema_and_table, 
                  s_col=source_column))
