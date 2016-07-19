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


# functions
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
        create index {schema}_{table}_lookup_index on {schema}.{table}(student_lookup)
        """.format(schema=schema, table=table)
        cursor.execute(sql_create_index)
        print(""" - Table {schema}.{table} created!"""\
        .format(schema=schema, table=table))

def update_column_with_join(cursor, table, column, source_table, 
                            source_column = None, source_schema = 'clean',
                            schema='model', dtype='varchar(64)', grade=9):
    """ 
    Update column using join to match another table                 
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
    alter table {schema}.{table} add column {column} {dtype} default null;
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
    
def append_grade(col='col', grade=9):
    """ Append grade level to column name
        eg. 'absence' for grade 9: 'absence_gr_09'
    :param str col: column name
    :param int grade: grade level in integer
    :return str newname: the colname in the feature table; if error, return None
    :rtype str or None
    """
    grd = str(grade)
    lenGrade = len(grd)
    if len(grd)==1:
        return col+'_gr_'+'0'+grd
    elif len(grd)==2:
        return col+'_gr_'+grd
    else:
        return None

def main():
    schema, table = "model" ,"absence"
    source_schema = "clean"
    tab_snapshots, tab_absence = "all_snapshots", "all_absences"
    gr_min, gr_max = 4, 11
    with postgres_pgconnection_generator() as connection:
        connection.autocommit = True
        with connection.cursor() as cursor:
            create_feature_table(cursor, table, schema = 'model', replace = True)
            
            # days_absent columns
            source_table, source_column = tab_snapshots, 'days_absent'
            for grd in range(gr_min, gr_max+1):
                column = append_grade(source_column, grd)
                update_column_with_join(cursor, table, column=column, source_table=source_table, 
                                source_column = source_column, source_schema = 'clean',
                                schema='model', grade=grd)
           
            # days_absent_unexecused
            source_table, source_column = tab_snapshots, 'days_absent_unexcused'
            for grd in range(gr_min, gr_max+1):
                column = append_grade(source_column, grd)
                update_column_with_join(cursor, table, column=column, source_table=source_table, 
                                source_column = source_column, source_schema = 'clean',
                                schema='model', grade=grd)
                
            # discipline_incidents
            source_table, source_column = tab_snapshots, 'discipline_incidents'
            for grd in range(gr_min, gr_max+1):
                column = append_grade(source_column, grd)
                update_column_with_join(cursor, table, column=column, source_table=source_table, 
                                source_column = source_column, source_schema = 'clean',
                                schema='model', grade=grd)
                
            # tardy_unexecused will be added later; need to find grade levels  
            
            connection.commit()
        
if __name__ =='__main__':
        main()

