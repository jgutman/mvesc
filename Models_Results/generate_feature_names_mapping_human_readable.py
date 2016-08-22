import os, sys
pathname = os.path.dirname(sys.argv[0])
full_pathname = os.path.abspath(pathname)
split_pathname = full_pathname.split(sep="mvesc")
base_pathname = os.path.join(split_pathname[0], "mvesc")
parentdir = os.path.join(base_pathname, "ETL")
sys.path.insert(0, parentdir)
from mvesc_utility_functions import *
import pandas as pd
import os
import re
import json


def main():
    json_filename = 'feature_name_mapping_to_human_readable.json'
    with postgres_pgconnection_generator() as conn:
        with conn.cursor() as cursor:
            sql_all_table_names = """
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema='model';
            """
            #table_names = pd.read_sql_query(sql_all_table_names, conn)
            # copied feature table names to the list below
            table_names = ['demographics', 'snapshots', 'absence', 'mobility', 'grades', 'oaa_normalized', 'intervention']
            sql_colnames = """
            select table_name, column_name, udt_name from information_schema.columns 
            where table_schema='model' and table_name in ({tables})
            """.format(tables = "\'" + "\', \'".join(table_names) + "\'")
            tables_columns_dtypes = pd.read_sql_query(sql_colnames, conn)

    colnames_grade = set(filter(lambda x: '_gr_' in x, tables_columns_dtypes.column_name))
    colnames_others = set(filter(lambda x: not ('_gr_' in x), tables_columns_dtypes.column_name))
    all_tokens = []
    for nm in colnames_grade:
        all_tokens = all_tokens + nm.split('_')
    all_tokens = set(all_tokens)
    token_mapping = {
     'avg': 'average number of',
     'change':'changes',
     'consec':'consecutive',
     'ed':'education',
     'extracurr': 'extracurricular',
     'instruc':'instruction',
     'intracurr':'intracurricular', 
     'inv':'intervention',
     'iss':'in-school-suspension',
     'n':'number of', 
     'normalized':'Z-score',
     'num':'number of',
     'oss':'out-of-school-suspension',
    'percent':'percentage',
     'pf':'pass_or_fail',
     'pl':'performance level',
     'titlei':'titleI',
     'to':'',
     'withdraw':'withdrawal',
     'wkd':'on weekday'}
    wkd_mapping = {'weekday 1':'Monday',
                   'weekday 2':'Tuesday',
                   'weekday 3':'Wednesday',
                   'weekday 4':'Thursday',
                   'weekday 5':'Friday',
                  }
    mapping = {}
    # names make sense themselves
    for nm in colnames_others:
        mapping[nm] = nm
    for nm in colnames_grade:
        tokens = nm.split('_')
        new_nm = ''
        for t in tokens:
            if t=='gr':
                if 'to' in tokens:
                    new_nm = new_nm + 'upto grade '
                else:
                    new_nm = new_nm + 'in grade '
            elif t in token_mapping:
                new_nm = new_nm + token_mapping[t] + ' '
            else:
                new_nm = new_nm + t + ' '
        mapping[nm] = new_nm

    # clean up double space and weekdays
    for key in mapping:
        mapping[key] = mapping[key].replace('  ', ' ').strip()
        if 'weekday' in mapping[key]:
            ind = mapping[key].find('weekday')
            wkdn = mapping[key][ind:ind+9]
            mapping[key] = mapping[key].replace(wkdn, wkd_mapping[wkdn])
        if 'in in' in mapping[key]:
            mapping[key] = mapping[key].replace('in in', 'between')
            mapping[key] = mapping[key] + ' and previous school year'

    with open(json_filename, 'w') as f:
        json.dump(mapping, f, ensure_ascii=True, sort_keys=True, indent=4)
        
    print('Json file \'{0}\' saved to current directory.'.format(json_filename))


if __name__ == '__main__':
    main()

