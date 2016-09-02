import os, sys

pathname = os.path.dirname(sys.argv[0])
full_pathname = os.path.abspath(pathname)
split_pathname = full_pathname.split(sep="mvesc")
base_pathname = os.path.join(split_pathname[0], "mvesc")
parentdir = os.path.join(base_pathname, "ETL")
sys.path.insert(0,parentdir)
from mvesc_utility_functions import *

def create_feature_table(cursor, table, schema, replace = False):
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
        create index {schema}_{table}_index on {schema}.{table}(student_lookup)
        """.format(schema=schema, table=table)
        cursor.execute(sql_create_index)
        print(""" - Table {schema}.{table} created!"""\
        .format(schema=schema, table=table))

def update_column_with_join(cursor, table, schema, column_list, source_table,
                            source_schema = None):
    """
    Update column using join to match another table
    :param pg.cursor cursor: pg cursor
    :param str table: table to update
    :param str column_list: list of column in source_table to add to table
    :param str source_table: table containing columns to add
    :param str source_schema: schema of source - None default for temp tables
    :param str schema: schema to update
    :return None:
    """
    # setting defaults
    if not source_schema:
        source_schema_and_table = source_table
    else:
        source_schema_and_table = source_schema+'.'+source_table

    # joining columns
    sql_join_cmd = """
    alter table {schema}.{table} rename to {table}_temp;
    create table {schema}.{table} as
    select t1.*, {source_cols} from {schema}.{table}_temp t1
    left join {source_schema_and_table} t2
    on t1.student_lookup = t2.student_lookup;
    drop table {schema}.{table}_temp;
    """.format_map({'schema':schema, 'table':table,'source_table':source_table,
               'source_schema_and_table':source_schema_and_table,
                    'source_cols':", ".join(column_list)})
    cursor.execute(sql_join_cmd)
    print(""" - updated {source_cols} in {schema}.{table}
    from {s_schema_and_table}; """\
          .format(source_cols=", ".join(column_list), schema=schema,
                  table=table, s_schema_and_table=source_schema_and_table))
