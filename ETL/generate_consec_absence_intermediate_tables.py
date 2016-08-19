""" Generate 2 intermediate tables in public schema 
for consecutive absence and tardy
(not updating any table or generating features;
 it may take ~30 minutes to run)

 Generate 2 tables in public schema: 
 - intermed_abs_agg, 
 - intermed_tdy_agg, 
 
 Procedures:
 - obtain all distinct lookups from clean.absences;
 - break them into chunks to process chunk by chunk(memory cannot hold all data);
 - generate dataframes with number of consecutive days for a starting date
 - export to postgres and index student_lookups and date
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
    """Yield successive n-sized chunks from l.
    
    :param list l: a list to generate iterator
    :param int n: the number of elements to return per iteration
    :return list: a subset of list with n elements or less
    :rtype list
    """
    for i in range(0, len(l), n):
        yield l[i:i+n]

def read_absences_lookups(conn, lookups = None, table='all_absences', schema='clean'):
    """ Read data of certain lookup-chunk

    :param pg.connection conn: postgres connector
    :param list lookups: lookups to query from the database
    :param str table: table name
    :param str schema: schema name
    :return pd.dataframe: data frame of all rows for the student_lookups
    :rtype pd.dataframe
    """
    sqlcmd = """select * from {schema}."{table}" 
    where student_lookup in {lookups} 
    order by student_lookup, date; """.format(schema=schema, table=table, lookups=str(tuple(lookups)))
    return pd.read_sql_query(sqlcmd, conn)


def consecutive_aggregate(df, desc_str='absence'):
    """ Aggreate consective days of a certain type of absence
    
    :param pd.dataframe df: data frame of absence data
    :param str desc_str: description string of what types of absence to aggregate
    :return pd.dataframe sumdf: sumdf with lookups, dates, counts 
    :rtype pd.dataframe
    """
    new_date_col, new_cnt_col = desc_str+'_starting_date', desc_str+'_consec_count'
    subdf = df[[desc_str in desc for desc in df.absence_desc]] # subset rows of relevant absence
    starting_dates=[None] * (subdf.shape[0])
    for i in range(subdf.shape[0]-1):
        row1, row2 = subdf.iloc[[i]], subdf.iloc[[i+1]] # get consecutive rows
        if row1.student_lookup.values[0]==row2.student_lookup.values[0]: #PythonSucksSubseting#
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


def main():
    chunksize = 200
    schema, table = 'clean', 'all_absences'
    with postgres_pgconnection_generator() as connection:
        connection.autocommit = True
        with connection.cursor() as cursor:
            print('------ Running generate_consec_absence_columns.py -------')
            lookups = list(pd.read_sql_query('select distinct student_lookup from clean.all_absences;', connection).student_lookup)
            random.shuffle(lookups) # shuffle lookup list so that we have roughly uniform workload for each chunk of students
            lookups_len = len(lookups)

            print(' - generating agggated dataframe of absences...')
            final_abs_df = pd.DataFrame()
            final_tdy_df = pd.DataFrame()
            processed_len = 0.0
            for chunk_lookups in chunks(lookups, chunksize):
                df = read_absences_lookups(connection, lookups=chunk_lookups)
                final_abs_df = final_abs_df.append(consecutive_aggregate(df, desc_str='absence'), ignore_index=True)
                final_tdy_df = final_tdy_df.append(consecutive_aggregate(df, desc_str='tardy'), ignore_index=True)
                processed_len = processed_len + len(chunk_lookups)
                print("   {:2.2%} students processed; still processing...".format(1.*processed_len/len(lookups)), end="\r")

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
            print(' - Done: generated consec tables for absence(intermed_abs_agg) and tardy(intermed_tdy_agg) in public;')


if __name__=='__main__':
    main()
