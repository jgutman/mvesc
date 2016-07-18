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
        create index lookup_index on {schema}.{table}(student_lookup)        
        """.format(schema=schema, table=table)
        cursor.execute(sql_create_index)
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
    drop tab le {schema}.{table}_temp;
    """.format_map({'schema':schema, 'table':table, 'temp_table':temp_table,
                    'new_col': ", ".join(new_col_names)})
    cursor.execute(add_column_query)

def update_column_with_join(cursor, table, column, source_table, 
                            source_column = None, source_schema = None,
                            schema='model'):
    """ 
    Update column using join to match another table                 
    :param pg.cursor cursor: pg cursor
    :param str source_schema: schema of source
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
    print(""" - updated "{schema}"."{table}"."{col}" 
    from {s_schema_and_table}."{s_col}"; """\
          .format(col=column, schema=schema, table=table, 
                 s_schema_and_table=source_schema_and_table, 
                  s_col=source_column))
