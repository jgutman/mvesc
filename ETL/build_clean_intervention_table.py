import os, sys
from os.path import isfile, join, abspath, basename
from optparse import OptionParser
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
import sqlalchemy
import json

pathname = os.path.dirname(sys.argv[0])
full_pathname = os.path.abspath(pathname)
split_pathname = full_pathname.split(sep="mvesc")
base_pathname = os.path.join(split_pathname[0], "mvesc")
parentdir = os.path.join(base_pathname, "ETL")
sys.path.insert(0,parentdir)
from mvesc_utility_functions import *

def main():
    schema = 'public'
    public_tables = ['INV_06_16_CO_M', 'INV_06_16_FR_M', 'INV_06_16_MA_M', 'INV_06_16_RV_M', 'INV_06_16_RW_M', 
                     'INV_06_16_TV_M', 'INV_06_16_WM_M', 'INV_10_16_CEVSD_M', 'INV_10_16_EM_M']
    new_column_names = ['student_lookup', 'status', 'grade', 'gender', 'hmrm', 
                        'membership_code', 'description', 'school_year', 'district']
    
    table_df = {}
    
    print(" - Reading intervention tables of different districts...")
    with postgres_pgconnection_generator() as conn:
        with conn.cursor() as cursor:
            for tab in public_tables:
                nrows = 1000000
                sql_read_table = """select * from {s}."{t}" limit {n};""".format(s=schema, t=tab, n=nrows)
                table_df[tab] = pd.read_sql_query(sql_read_table, conn)
            table_df['INV_06_16_CO_M']['District'] = 'Coshocton' # add missed `district` column in table for CO
            codes_df = pd.read_sql_query("select * from public.\"INV_MembershipCodes\";", conn)
            outcome = pd.read_sql_query("select * from model.outcome;", conn)
    
    df = pd.DataFrame()
    for t in table_df:
        new_col_dict = {table_df[t].columns[i]:new_column_names[i] for i in range(len(new_column_names))}
        table_df[t] = table_df[t].rename(columns=new_col_dict)
        df = df.append(table_df[t])
    df = df.drop('hmrm', axis=1)
    df.reset_index(drop=True, inplace=True)
    
    print(" - Integrating and cleaning table...")
    # update and clean columns
    grade_converter = {'06':6, '05':5, '04':4, '03':3, '02':2, '01':1, 
                       'KG':0, 'PS':-1, '12':12, '11':11, '09':9,'10':10, 
                       '07':7, '08':8, '23':23, 'UG':None, 'GR':None, '13':13}
    codes_converter = {231101:231001, 231105:231005}
    new_grades = [None]*df.shape[0]
    for i in range(df.shape[0]):
        if df.membership_code[i] in codes_converter:
            df.ix[i, 'membership_code'] = codes_converter[df.membership_code[i]]
        if df.grade[i] in grade_converter:
            new_grades[i] = grade_converter[df.grade[i]]

    df.drop(['grade'], axis=1, inplace=True)
    def int_nonNone(x):
        """ Convert float to int and others None
        """
        if x==None or isinstance(x, str):
            return None
        else:
            return int(x)
    new_grades = list(map(int_nonNone, new_grades))
    df['grade'] = new_grades
    
    print(" - Saving data to postgres... ")
    df2postgres(df, 'intervention', nrows=-1, if_exists='replace', schema='clean')

if __name__ == "__main__":
    main()

