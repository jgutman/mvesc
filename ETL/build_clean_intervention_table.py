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
    # Parameters to read and clean the tables
    schema = 'public'
    public_tables = ['INV_06_16_CO_M', 'INV_06_16_FR_M', 'INV_06_16_MA_M', 'INV_06_16_RV_M', 'INV_06_16_RW_M', 
                     'INV_06_16_TV_M', 'INV_06_16_WM_M', 'INV_10_16_CEVSD_M', 'INV_10_16_EM_M']
    new_column_names = ['student_lookup', 'status', 'grade', 'gender', 'hmrm', 
                        'membership_code', 'description', 'school_year', 'district']
    grade_converter = {'06':6, '05':5, '04':4, '03':3, '02':2, '01':1,
                       'KG':0, 'PS':-1, '12':12, '11':11, '09':9,'10':10,
                       '07':7, '08':8, '23':23, 'UG':None, 'GR':None, '13':13}
    codes_converter = {231101:231001, 231105:231005}
    dict_group2abbrev = {'Post-secondary Enrollment Options Program':'post_secondary',
               'Academic Intervention':'academic_inv',
               'Specialized Instructions':'spec_instruc',
               'Placement Options':'placement',
               'Disadvantaged Pupil Programs (DPPF)':'DPPF',
               'Title I':'titlei', 'Vocational Programs':'vocational',
               'Extracurricular/Intracurricular Programs and Services':'extracurr_program',
               'Academic Intracurricular Descriptions (Vocational)':'academic_intracurr',
               'School Related Service Program':'school_program',
               'Interscholastic Athletics':'atheletics',
               'Other':'other',
               'Dropout':'dropout'}

    table_df = {}

    print(" - Reading intervention tables of different districts...")
    with postgres_pgconnection_generator() as conn:
        with conn.cursor() as cursor:
            for tab in public_tables:
                nrows = -1
                table_df[tab] = read_table_to_df(conn, tab, schema=schema, nrows=nrows)
            table_df['INV_06_16_CO_M']['District'] = 'Coshocton' # add missed `district` column in table for CO
            codes_df = read_table_to_df(conn, 'INV_MembershipCodes', schema=schema, nrows=nrows) 

            
    dict_code2group = {codes_df.membership_code[i]:codes_df.membership_group[i] for i in range(codes_df.shape[0])}
    df = pd.DataFrame()
    for t in table_df:
        new_col_dict = {table_df[t].columns[i]:new_column_names[i] for i in range(len(new_column_names))}
        table_df[t] = table_df[t].rename(columns=new_col_dict)
        df = df.append(table_df[t])

    df = df.drop('hmrm', axis=1)
    df.reset_index(drop=True, inplace=True)

    print(" - Integrating and cleaning table...")
    # update and clean columns
    new_grades = [None]*df.shape[0]
    inv_groups = ['']*df.shape[0]
    for i in range(df.shape[0]):
        if df.membership_code[i] in codes_converter:
            df.ix[i, 'membership_code'] = codes_converter[df.membership_code[i]]
        if df.grade[i] in grade_converter:
            new_grades[i] = grade_converter[df.grade[i]]
        if df.membership_code[i] in dict_code2group:
            inv_groups[i]=(dict_group2abbrev[dict_code2group[df.membership_code[i]]]).lower()

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
    df['inv_group'] = inv_groups

    print(" - Saving intervention data frame to postgres... ")
    df2postgres(df, 'intervention', nrows=-1, if_exists='replace', schema='clean')
    with postgres_pgconnection_generator() as connection:
        connection.autocommit = True
        with connection.cursor() as cursor:
            sql_index = 'create index {t}_lookup on clean.{t} (student_lookup)'.format(t='intervention')
            cursor.execute(sql_index)


if __name__ == "__main__":
    main()

