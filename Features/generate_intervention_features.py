""" Generate Intervention Related features
Depends on tables:
- clean.intervention
Depends on code:
- generate_intervention_features.py (1 min to run)
- build_clean_intervention_table.py (in ../ETL/, 3 mins to run)
For Each Grade, generate features:
- extracurr_program*
- post_secondary*, -
- academic_inv*,  
- atheletics*, 
- placement*,  
- spec_instruc*, 
- vocational*, 
- academic_intracurr*,  
- school_program*, 
- titlei*
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



def set_null_as_0(cursor, columns, schema='model', table='intervention'):
    """ Set null data points as 0 (be careful to assume so)
    :param pg.connection.cursor cursor: postgres cursor
    :param str columns: a list of column names 
    :param str schema: schema name
    :param str table: table name
    """
    for column in columns:
        sqlcmd = """
        update {schema}.{table}
        set {column}=0
        where {column} is null or not ({column}>0);""".format(schema=schema, table=table, column=column)
        cursor.execute(sqlcmd)
    return None

def create_temp_intervention(cursor, grade_range, table = 'intervention_1type_temp_table',
    source_schema = 'clean', type_str = 'academic_inv', source_table = 'intervention'):
    """
    """
    # create table with all student_lookups to store features for
    query_join_inv_features = """
    drop table if exists {t};
    create temporary table {t} as
    select * from
        (
            select distinct(student_lookup)
            from {source_schema}.{source_table}
        ) student_inv_list
    """.format(t=table, source_schema=source_schema, source_table=source_table)

    # for each student, get the number of distinct addresses, cities, districts
    # lived in up to the specified max_grade, also store the total number of
    # non-null records going into that count (how long they've been in data)
    # then compute average as (number_addresses - 1) / number_records
    for gr in grade_range:
        sql_join_grade = """
        left join
        (
            select student_lookup, 1 as {type_str}_gr_{gr}
            from {source_schema}.{source_table} 
            where grade={gr} and inv_group like '%{type_str}%'
            group by student_lookup
        ) inv_{type_str}_{gr}
        using(student_lookup)
        """.format(gr=gr, type_str=type_str,
            source_schema=source_schema, source_table=source_table)
        query_join_inv_features += sql_join_grade

    cursor.execute(query_join_inv_features)
    # get column names in temporary table just created and return all in a list
    # remove student_lookup from list of column names returned
    #print(pd.read_sql_query("select * from {t} limit 20".format(t=table), conn))
    cursor.execute("select * from {t}".format(t=table))
    col_names = [i[0] for i in cursor.description]
    return(col_names[1:])
def main():
    source_schema, source_table = 'clean', 'intervention'
    schema, table = 'model', 'intervention' 
    temp_table = 'intervention_1type_temp_table'
    min_grd, max_grd = 3, 12
    all_features_list = ['spec_instruc', 
    'titlei',
    'post_secondary',
    'academic_inv',
    'academic_intracurr',
    'atheletics',
    'extracurr_program',
    'school_program',
    'placement',
    'vocational'] 
    top_feature_list = ['academic_inv',  'atheletics', 'placement']
    features2run = all_features_list
    with postgres_pgconnection_generator() as conn:
        conn.autocommit = True
        with conn.cursor() as cursor:
            create_feature_table(cursor, table, schema=schema, replace=True)
            grades = list(range(min_grd, max_grd+1))
            # academic intervention
            for feature_desc in features2run:
                inv_type = feature_desc
                columns = create_temp_intervention(cursor, grades, table = temp_table,
                                                   source_schema = source_schema, type_str = inv_type, 
                                                   source_table = source_table)
                update_column_with_join(cursor, table, columns, source_table=temp_table)
                set_null_as_0(cursor, columns, schema=schema, table=table)
                #print(pd.read_sql_query("select * from model.{t} limit 20".format(t=table), conn))
            conn.commit()
            print(" - Intervention features generated")

if __name__ == '__main__':
    main()
