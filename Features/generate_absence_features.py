""" Generate Absence related features
Depends on tables:
- clean.all_snapshots
- clean.all_absences

Depends on code:
- generate_absence_features.py (1 min to run)
- generate_consec_absence_columns.py (30 mins to run)


For Each Grade, generate features:
- absence
- absence_unexecused
- tardy
- tardy_unexecused
- medical
- absence_consec
- tardy_consec

Note: 97% daily absence data are after 2009,
which means Grade 5+ can have outcome category;
So features for Grade 3~5 are very sparse, and not suggested to use

"""


import os, sys
pathname = os.path.dirname(sys.argv[0])
full_pathname = os.path.abspath(pathname)
split_pathname = full_pathname.split(sep="mvesc")
base_pathname = os.path.join(split_pathname[0], "mvesc")
parentdir = os.path.join(base_pathname, "ETL")
sys.path.insert(0,parentdir)
from mvesc_utility_functions import *
import numpy as np
import pandas as pd
from feature_utilities import *

def set_null_as_0(cursor, column, schema='clean', table='absence'):
    """ Set null data points as 0 (be careful to assume so)

    :param pg.connection.cursor cursor: postgres cursor
    :param str column: column name
    :param str schema: schema name
    :param str table: table name
    """
    sqlcmd = """
    update {schema}.{table}
    set {column}=0
    where {column} is null;""".format(schema=schema, table=table, column=column)
    cursor.execute(sqlcmd)
    return None


def create_simple_temp_table(cursor, temp_table, source_table, source_column,
                             new_column, grade, source_schema='clean'):
    """
    Create simple temp table using `create table as select *`
    :param pg.cursor curosr: postgres pg.cursor
    :param str temp_table: name of temp table to create
    :param str source_table: name of source table to create temp table
    :param str source_column: name of source column in source_table
    :param str new_column: new column name in temp table
    :param int grade: the grade to subset
    :param str source_scheam: name of source schema, default 'clean'
    :return: None
    """
    sql_tmp_table = """
    drop table if exists {tmp};
    create temporary table {tmp} as
        select student_lookup, max({sc}) as {nc} from {ss}.{st}
        where grade={grd}
        group by student_lookup;
    """.format(tmp=temp_table, sc=source_column, nc=new_column, ss=source_schema, st=source_table, grd=grade)
    cursor.execute(sql_tmp_table)
    sql_index = "create index lookup_index on {t}(student_lookup)".format(t=temp_table)
    cursor.execute(sql_tmp_table)
    return None

def create_absence_type_temp_table(cursor, temp_table, source_table,
                                   new_column, type_str, grade, source_schema='clean'):
    """
    Create temp table for only certain type of absences
    :param pg.cursor curosr: postgres pg.cursor
    :param str temp_table: name of temp table to create
    :param str source_table: name of source table to create temp table
    :param str new_column: new column name in temp table
    :param int grade: the grade to subset
    :param str source_scheam: name of source schema, default 'clean'
    :return: None
    """
    sql_create_agg_temp = """
    drop table if exists {tmp};
    create temporary table {tmp} as
    select student_lookup, count(*) as {nc} from {ss}.{st}
    where grade={grd} and absence_desc like '%{type_str}%'
    group by student_lookup;
    """.format(tmp=temp_table, nc=new_column, ss=source_schema, st=source_table, type_str=type_str, grd=grade)
    cursor.execute(sql_create_agg_temp)
    sql_create_temp_index = """create index {tmp}_ind on {tmp}(student_lookup);""".format(tmp=temp_table);
    cursor.execute(sql_create_temp_index)
    return None

def create_consec_absence_temp_table(cursor, temp_table, source_table, source_column,
                                     new_column, grade, source_schema='clean'):
    """
    Create temp table for only consecutive absences
    :param pg.cursor curosr: postgres pg.cursor
    :param str temp_table: name of temp table to create
    :param str source_table: name of source table to create temp table
    :param str source_column: name of source column in source_table
    :param str new_column: new column name in temp table
    :param int grade: the grade to subset
    :param str source_scheam: name of source schema, default 'clean'
    :return: None
    """
    sql_create_agg_temp = """
    drop table if exists {tmp};
    create temporary table {tmp} as
    select student_lookup, sum({sc}) as {nc} from {ss}.{st}
    where grade={grd}
    group by student_lookup;
    """.format(tmp=temp_table, sc=source_column, ss=source_schema, st=source_table,
               nc=new_column, grd=grade)
    cursor.execute(sql_create_agg_temp)
    sql_create_temp_index = """create index {tmp}_index on {tmp}(student_lookup);""".format(tmp=temp_table);
    cursor.execute(sql_create_temp_index)
    return None

def create_feature_table(cursor, table, schema = 'model', replace = False):
    """ The current feature table is dropped and re-created with a single column
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
        create index {schema}_{table}_lookup_index on {schema}.{table}(student_lookup)
        """.format(schema=schema, table=table)
        cursor.execute(sql_create_index)
        print(""" - Table {schema}.{table} created!"""\
        .format(schema=schema, table=table))

def update_column_with_join(cursor, table, column, source_table,
                            source_column = None, source_schema = 'clean',
                            schema='model', dtype='varchar(64)', grade=9):
    """Update column using join to match another table

    :param pg.cursor cursor: pg cursor
    :param str source_schema: schema of source - None default for temp tables
    :param str source_table: table of source
    :param str source_column: column of source - defaults to column
    :param str schema: schema to update
    :param str table: table to update
    :param str column: column to update
    :param int grade: grade level to subset to
    :return None:
    """
    if not source_column:
        source_column = column
    if not source_schema:
        source_schema_and_table = source_table
    else:
        source_schema_and_table = source_schema+'.'+source_table
    dtype = get_column_type(cursor, source_table, source_column)
    sql_add_column = """
    alter table {schema}.{table} add column {column} {dtype} default 0;
    """.format( schema=schema, table=table, column=column, dtype=dtype )
    cursor.execute(sql_add_column);
    sql_join_cmd = """
    update {schema}.{table} t1
    set {column}=
    (select {source_column} from {source_schema_and_table} t2
    where t2.student_lookup=t1.student_lookup and t2.{source_column} is not null
    and t2.grade={grade}
    order by {source_column} desc limit 1);
    """.format(schema=schema, table=table, column=column,
               source_schema_and_table=source_schema_and_table,
               source_column=source_column, grade=grade)
    cursor.execute(sql_join_cmd)
    print(""" - updated {schema}.{table}.{col} from {s_schema_and_table}.{s_col} for grade {grade}; """.format(
            col=column, schema=schema, table=table,
            s_schema_and_table=source_schema_and_table,
            s_col=source_column, grade=grade))

def update_join_type_cnt(cursor, table, column, source_table,
                            source_column = None, source_schema = 'clean',
                            schema='model', dtype='varchar(64)', type_str = 'tardy', grade=9):
    """Update column using join to match another table

    :param pg.cursor cursor: pg cursor
    :param str source_schema: schema of source - None default for temp tables
    :param str source_table: table of source
    :param str source_column: column of source - defaults to column
    :param str schema: schema to update
    :param str table: table to update
    :param str column: column to update
    :param int grade: grade level to subset to
    :return None:
    """
    tab_temp = 'temp_table'
    if not source_column:
        source_column = column
    if not source_schema:
        source_schema_and_table = source_table
    else:
        source_schema_and_table = source_schema+'.'+source_table
    sql_drop_temp = """drop table if exists {table};""".format(table=tab_temp)
    cursor.execute(sql_drop_temp)
    sql_create_agg_temp = """
    create temporary table {temp_table} as
    select t1.student_lookup, count(*) from {schema}.{table} t1, {source_schema}.{source_table} t2
    where t1.student_lookup=t2.student_lookup and grade={grade} and absence_desc like '%{type_str}%'
    group by t1.student_lookup;""".format(temp_table=tab_temp, schema=schema, table=table, type_str=type_str,
                                          source_schema=source_schema, source_table=source_table, grade=grade)
    cursor.execute(sql_create_agg_temp)
    sql_create_temp_index = """create index tdy_cnt_index on {0}(student_lookup);""".format(tab_temp);
    cursor.execute(sql_create_temp_index)

    dtype = get_column_type(cursor, tab_temp, 'count')
    sql_add_column = """
    alter table {schema}.{table} add column {column} {dtype} default 0;
    """.format( schema=schema, table=table, column=column, dtype=dtype )
    cursor.execute(sql_add_column);
    sql_join_cmd = """
    update {schema}.{table} t1
    set {column}=
    (select count from {tab_temp} t2
    where t2.student_lookup=t1.student_lookup and t2.count is not null
    order by count desc limit 1);
    """.format(schema=schema, table=table, column=column, tab_temp=tab_temp)
    cursor.execute(sql_join_cmd)
    print(""" - updated {schema}.{table}.{col} from {s_schema_and_table}.{s_col} for grade {grade}; """.format(
            col=column, schema=schema, table=table,
            s_schema_and_table=source_schema_and_table,
            s_col=source_column, grade=grade))

def update_consec(cursor, table, column, source_table,
                            source_column = None, source_schema = 'clean',
                            schema='model', type_str = 'absence', grade=9):
    """ Update column using consec aggreated data

    :param pg.cursor cursor: pg cursor
    :param str source_schema: schema of source - None default for temp tables
    :param str source_table: table of source
    :param str source_column: column of source - defaults to column
    :param str schema: schema to update
    :param str table: table to update
    :param str column: column to update
    :param int grade: grade level to subset to
    :return None:
    """
    tab_temp = 'temp_table'
    source_column = type_str+'_conseq_count'
    sql_drop_temp = """drop table if exists {table};""".format(table=tab_temp)
    cursor.execute(sql_drop_temp)
    sql_create_agg_temp = """
    create temporary table {temp_table} as
    select t1.student_lookup, sum(t2.{source_column}) as csum from {schema}.{table} t1, {source_schema}.{source_table} t2
    where t1.student_lookup=t2.student_lookup and grade={grade} and absence_desc like '%{type_str}%'
    group by t1.student_lookup;""".format(temp_table=tab_temp, schema=schema, table=table, type_str=type_str,
        source_column=source_column, source_schema=source_schema, source_table=source_table, grade=grade)
    cursor.execute(sql_create_agg_temp)
    sql_create_temp_index = """create index consec_agg_index on {0}(student_lookup);""".format(tab_temp);
    cursor.execute(sql_create_temp_index)

    dtype = get_column_type(cursor, source_table, source_column)
    sql_add_column = """
    alter table {schema}.{table} add column {column} {dtype} default 0;
    """.format(schema=schema, table=table, column=column, dtype=dtype )
    cursor.execute(sql_add_column);
    sql_join_cmd = """
    update only {schema}.{table} t1
    set {column}=
    ( select csum from {tmp_tab} t2
      where t2.student_lookup=t1.student_lookup
      limit 1
    );""".format(schema=schema, table=table, column=column, tmp_tab=tab_temp)
    cursor.execute(sql_join_cmd)
    print(""" - updated {schema}.{table}.{col} from {s_schema}.{s_table}.{s_col} for grade {grade}; """.format(
            col=column, schema=schema, table=table,
            s_schema=source_schema, s_table=source_table,
            s_col=source_column, grade=grade))



>>>>>>> master
def main():
    schema, table = "model" ,"absence"
    source_schema = "clean"
    tab_snapshots, tab_absence = "all_snapshots", "all_absences"
    gr_min, gr_max = 3, 11
    with postgres_pgconnection_generator() as connection:
        connection.autocommit = True
        with connection.cursor() as cursor:
            create_feature_table(cursor, table, schema = 'model', replace = True)

            # days_absent columns
            source_table, source_column, new_col_name = tab_snapshots, 'days_absent', 'absence'
            for grd in range(gr_min, gr_max+1):
                temp_table = column = new_col_name+'_gr_'+str(grd)
                create_simple_temp_table(cursor, temp_table, source_table, source_column, column, grade=grd)
                update_column_with_join(cursor, table, [column], source_table=temp_table, schema=schema)

                set_null_as_0(cursor, column, schema=schema, table=table)

            # days_absent_unexecused
            source_table, source_column = tab_snapshots, 'days_absent_unexcused'
            new_col_name = 'absence_unexcused'

            for grd in range(gr_min, gr_max+1):
                temp_table = column = new_col_name+'_gr_'+str(grd)
                create_simple_temp_table(cursor, temp_table, source_table, source_column, column, grade=grd)
                update_column_with_join(cursor, table, [column], source_table=temp_table, schema=schema)
                set_null_as_0(cursor, column, schema=schema, table=table)


            # tardy
            source_table, new_col_name = tab_absence, 'tardy'
            for grd in range(gr_min, gr_max+1):
                temp_table = column = new_col_name + '_gr_' + str(grd)
                create_absence_type_temp_table(cursor, temp_table, source_table, column,
                                               type_str=new_col_name, grade=grd, source_schema='clean')
                update_column_with_join(cursor, table, [column], source_table=temp_table, schema=schema)
                set_null_as_0(cursor, column, schema=schema, table=table)

            # tardy_unexecused
            source_table, new_col_name = tab_absence, 'tardy_unexcused'
            for grd in range(gr_min, gr_max+1):
                temp_table = column = new_col_name + '_gr_' + str(grd)
                create_absence_type_temp_table(cursor, temp_table, source_table, column,
                                               type_str=new_col_name, grade=grd, source_schema='clean')
                update_column_with_join(cursor, table, [column], source_table=temp_table, schema=schema)
                set_null_as_0(cursor, column, schema=schema, table=table)

            # med
            source_table, new_col_name = tab_absence, 'medical'
            for grd in range(gr_min, gr_max+1):
                temp_table = column = new_col_name + '_gr_' + str(grd)
                create_absence_type_temp_table(cursor, temp_table, source_table, column,
                                               type_str='med', grade=grd, source_schema='clean')
                update_column_with_join(cursor, table, [column], source_table=temp_table, schema=schema)
                set_null_as_0(cursor, column, schema=schema, table=table)

            # consecutive absence days
            source_table, new_col_name = tab_absence, 'absence'
            source_column = new_col_name + '_consec_count'
            for grd in range(gr_min, gr_max+1):
                temp_table = column = new_col_name + '_consec_gr_' + str(grd)
                create_consec_absence_temp_table(cursor, temp_table, source_table, source_column,
                                                 column, grade=grd, source_schema='clean')
                update_column_with_join(cursor, table, [column], source_table=temp_table, schema=schema)
                set_null_as_0(cursor, column, schema=schema, table=table)

            # consecutive tardy days
            source_table, new_col_name = tab_absence, 'tardy'
            source_column = new_col_name + '_consec_count'
            for grd in range(gr_min, gr_max+1):
                temp_table = column = new_col_name + '_consec_gr_' + str(grd)
                create_consec_absence_temp_table(cursor, temp_table, source_table, source_column,
                                                 column, grade=grd, source_schema='clean')
                update_column_with_join(cursor, table, [column], source_table=temp_table, schema=schema)
                set_null_as_0(cursor, column, schema=schema, table=table)

            connection.commit()

if __name__ =='__main__':
        main()
