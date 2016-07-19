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
    cursor.execute("""
    select count(*) from information_schema.tables
    where table_schema = '{schema}' and table_name = '{table}'
    """.format_map({'schema':schema,'table':table}))
    table_exists = cursor.fetchall()[0][0]
    if not table_exists:
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

def update_column_with_join(cursor, table, column, source_table, 
                            source_column = None, source_schema = None,
                            schema='model'):
    """ 
    Update column using join to match another table                 
    :param pg.cursor cursor: pg cursor
    :param str source_schema: schema of source - None default for temp tables
    :param str source_table: table of source
    :param str source_column: column of source - defaults to column
    :param str schema: schema to update
    :param str table: table to update
    :param str column: column to update                    
    :return None:                      
    """
    if not source_column:
        source_column = column
    dtype = get_column_type(cursor, source_table, source_column)
    if not source_schema:
        source_schema_and_table = source_table
    else:
        source_schema_and_table = source_schema+'.'+source_table
    sql_add_column = """
    alter table {schema}.{table} add column {column} 
    {dtype} default null;
    """.format( schema=schema, table=table, column=column, dtype=dtype)
    cursor.execute(sql_add_column);
    sql_join_cmd = """
    update {schema}.{table} t1
    set {column}=
    (select {source_column} from {source_schema_and_table} t2
    where t2.student_lookup=t1.student_lookup and t2.{source_column} is not null
    order by {source_column} desc limit 1);
    """.format(schema=schema, table=table, column=column,
               source_schema_and_table=source_schema_and_table, 
               source_column=source_column)
    cursor.execute(sql_join_cmd)
    print(""" - updated {schema}.{table}.{col} 
    from {s_schema_and_table}.{s_col}; """\
          .format(col=column, schema=schema, table=table, 
                 s_schema_and_table=source_schema_and_table, 
                  s_col=source_column))
