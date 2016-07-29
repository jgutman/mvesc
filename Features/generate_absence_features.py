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
