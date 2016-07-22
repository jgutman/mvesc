""" Generate consecutive absences columns (not generating features year)
 Generate New Columns in clean.absence: 
 - absence_starting_date, 
 - absence_consec_count, 
 - tardy_starting_date, 
 - tardy_consec_count
 
 Procedures:
 - obtain all distinct lookups from clean.absences;
 - break them into chunks to process chunk by chunk(memory cannot hold all data);
 - generate dataframes with number of consecutive days for a starting date
 - export to postgres and index student_lookups and date
 - join and update to clean.all_absences
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
import random
import datetime
import warnings
warnings.filterwarnings("ignore")



def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i+n]

def read_absences_lookups(conn, lookups = None):
    """ Read data of certain lookup-chunk
    """
    sqlcmd = """select * from clean.all_absences 
    where student_lookup in {0} 
    order by student_lookup, date; """.format(str(tuple(lookups)))
    return pd.read_sql_query(sqlcmd, conn)


def consec_agg(df, desc_str='absence'):
    """ Aggreate consective days of a certain type
    :return pd.dataframe sumdf: sumdf with lookups, dates, counts 
    """
    new_date_col, new_cnt_col = desc_str+'_starting_date', desc_str+'_consec_count'
    subdf = df[[desc_str in desc for desc in df.absence_desc]]
    starting_dates=[None] * (subdf.shape[0])
    for i in range(subdf.shape[0]-1):
        row1, row2 = subdf.iloc[[i]], subdf.iloc[[i+1]]
        index = row1.index[0]
        if row1.student_lookup.values[0]==row2.student_lookup.values[0]:
            if (((row2.date.values[0]  - row1.date.values[0]).days == 1) or  
            (row2.weekday.values[0]==1 and row1.weekday.values[0]>4 and 
             (row2.date.values[0]-row1.date.values[0]).days<4)):
                if starting_dates[i]==None:
                    starting_dates[i]=row1.date.values[0]
                    starting_dates[i+1]=row1.date.values[0]
                else:
                    starting_dates[i]=starting_dates[i-1]
                    starting_dates[i+1]=starting_dates[i-1]
    subdf[new_date_col] = starting_dates
    sumdf = subdf.groupby(by=['student_lookup', new_date_col]).count().reset_index()[['student_lookup', new_date_col,'month']]
    sumdf = sumdf.rename(columns={'month':new_cnt_col})
    sumdf = sumdf.merge(subdf[['student_lookup', 'date']], how='left', left_on=['student_lookup', new_date_col], right_on=['student_lookup', 'date'])
    return(sumdf.drop('date', axis=1))


def update_absence(cursor, table='clean.all_absences', col='absence'):
    col_date, dtype_date = col+'_starting_date', 'date'
    col_cnt, dtype_cnt = col+'_consec_count', 'int'
    if col=='absence':
        table_intermed = 'public.intermed_'+col[:3]+'_agg'
    else:
        table_intermed='public.intermed_tdy_agg'
    sql_add_column = """
    alter table {table} drop column if exists {column};
    alter table {table} add column {column} {dtype} default null;
    """.format(table=table, column=col_date, dtype=dtype_date )
    cursor.execute(sql_add_column)
    sql_add_column = """
    alter table {table} drop column if exists {column};
    alter table {table} add column {column} {dtype} default null;
    """.format(table=table, column=col_cnt, dtype=dtype_cnt)
    cursor.execute(sql_add_column)
    
    sql_join_cmd = """
    update only {table} t1
    set {column_date}=t2.{column_date},
        {column_cnt} =t2.{column_cnt}
    from {table_intermed} t2
    where t1.student_lookup=t2.student_lookup 
    and t1.date=t2.{column_date}
    and t1.absence_desc like '%{col}%';
    """.format(table=table, column_date=col_date, column_cnt=col_cnt,
               table_intermed=table_intermed, col=col)
    cursor.execute(sql_join_cmd)
    
    print(""" - updated {table}.({col1}, {col2}) from {tab_int}; """.format(
            table=table, col1=col_date, col2=col_cnt, tab_int=table_intermed))
    
def main():
    chunksize = 100
    schema, table = 'clean', 'all_absences'
    with postgres_pgconnection_generator() as connection:
        connection.autocommit = True
        with connection.cursor() as cursor:
            print('------ Running generate_consec_absence_columns.py -------')
            lookups = list(pd.read_sql_query('select distinct student_lookup from clean.all_absences;', connection).student_lookup)
            random.shuffle(lookups)
            lookups = lookups[:2000]
    #         sql_add_column = """alter table {schema}.{table} drop if exists column {column};
    #         alter table {schema}.{table} add column {column} {dtype} default null;
    #         """.format( schema=schema, table=table, column=new_date_col, dtype=dtype_date)
    #         #cursor.execute(sql_add_column)
    #         sql_add_column = """alter table {schema}.{table} drop if exists column {column};
    #         alter table {schema}.{table} add column {column} {dtype} default null;
    #         """.format( schema=schema, table=table, column=new_cnt_col, dtype=dtype_cnt)
            #cursor.execute(sql_add_column)

            print(' - generating agggated dataframe of absences...')
            final_abs_df = pd.DataFrame()
            final_tdy_df = pd.DataFrame()
            for chunk_lookups in chunks(lookups, chunksize):
                df = read_absences_lookups(connection, lookups=chunk_lookups)
                final_abs_df = final_abs_df.append(consec_agg(df, desc_str='absence'), ignore_index=True)
                final_tdy_df = final_tdy_df.append(consec_agg(df, desc_str='tardy'), ignore_index=True)

            print(' - writing agg-dataframes to public...')
            eng = postgres_engine_generator()
            final_abs_df.to_sql('intermed_abs_agg', eng, index=False, if_exists='replace')
            final_tdy_df.to_sql('intermed_tdy_agg', eng, index=False, if_exists='replace')

            sql_index_intermed="""create index public_intmed_abs_sl on public.intermed_abs_agg (student_lookup);
            create index public_intmed_tdy_sl on public.intermed_tdy_agg (student_lookup);
            create index public_intmed_abs_sl_dt on public.intermed_abs_agg (student_lookup, absence_starting_date);
            create index public_intmed_tdy_sl_dt on public.intermed_tdy_agg (student_lookup, tardy_starting_date);
            """
            cursor.execute(sql_index_intermed)

            print(' - updating clean.absence by joining...')
            update_absence(cursor, table='clean.all_absences', col='absence') # changed from absence_test to absence; run again
            update_absence(cursor, table='clean.all_absences', col='tardy')
            print(' - Done!')
            
if __name__=='__main__':
    main()
