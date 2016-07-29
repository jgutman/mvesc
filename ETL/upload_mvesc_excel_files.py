""" Script to process and upload excel files to postgres
- will be updated regularly
- each section marked by '#++++++' is for one excel file
- procedure is commented briefly in script and more in ETL_README (coming after Jul 8)
""" 
import pandas as pd
import os
import re
import json
from sqlalchemy import create_engine
from csv2postgres_mvesc import postgresql_engine_generator_mvesc

#++++++ Functions only for the Excel files ++++++#
def combine_colnames(col1, col2):
    """combine the colnames from 2 rows: !! Only works in this specific case
    :param str col1: first column-name
    :param str col2: second column-name
    :return str new_col: combined new column name
    :return str
    """
    new_col = "pct_same_"
    schoolyear = col2[2:4] + col2[7:9]
    if "district" in col1.lower():
        dist_school = "district_"
    else:
        dist_school = "school_"
    
    if "less" in col1.lower():
        more_less = "less_"
    else:
        more_less = "more_"
    new_col = new_col+dist_school+more_less+'a_year_'+schoolyear  
    return new_col


def df2postgres(df, table_name, nrows=-1, if_exists='fail', schema='raw'):
    """ dump dataframe object to postgres database
    
    :param pandas.DataFrame df: dataframe
    :param int nrows: number of rows to write to table;
    :return str table_name: table name of the sql table
    :rtype str
    """
    # create a postgresql engine to wirte to postgres
    engine = postgresql_engine_generator_mvesc()
    
    #write the data frame to postgres
    if nrows==-1:
        df.to_sql(table_name, engine, schema=schema, index=False, if_exists=if_exists)
    else:
        df.iloc[:nrows, :].to_sql(table_name, engine, schema=schema, index=False, if_exists=if_exists)
    return table_name

def add_file2table_jsonfile(excelfile, table_name, jsonfile='file_to_table_name.json'):
    """ Add file:table to json OR return None to avoid conflict
    
    step 1: check whether file and table exist in json file;
    step 2: if exist, return table_name; 
    if not exist, add file:table to json, then return table_name
    
    :param str excelfile: excel file with sheet name 
    :param str table_name: table name
    :param str jsonfile: json file name, default: 'file_to_table_name.json'
    :return str table_name
    :rtype str
    """
    # load json, keys, values
    with open(jsonfile, 'r') as f:
        file_table_names = json.load(f)
    existing_keys = list(file_table_names.keys())
    existing_values = list(file_table_names.values())
    
    # check datafile in json
    if excelfile in existing_keys:
        print("""File "{}" already in json with table name "{}" """.format(excelfile, file_table_names[excelfile]))
        return(file_table_names[excelfile])
    else:
        if table_name in existing_values:
            print("""Table "{}" already in json for a file """.format(table_name))
            return(None)
        else:
            file_table_names[excelfile] = table_name
            with open(jsonfile, 'w') as f:
                json.dump(file_table_names, f, ensure_ascii=True, sort_keys=True, indent=4)
            print("""file:table "{}":"{}" added to json file """.format(excelfile, file_table_names[excelfile]))
            return table_name
    return(None)

#++++++ ~/PartnerData/IRNSandWithdrawalCodes/IRN_DORP_GRAD_RATE1415.xls ++++++#
# -1. produce a `.csv` file with correct column names
# -2. call terminal command to use `csv2postgres_mvesc.py` in python
irn_file = "/mnt/data/mvesc/PartnerData/IRNSandWithdrawalCodes/IRN_DORP_GRAD_RATE1415.xls"
print('\n--- processing: ', irn_file)
irn_df = pd.read_excel(irn_file, sheetname=0)
raw_irn_newoldcol_dict = {old:'_'.join(old.lower().split(' '))\
 .replace('graduation', 'grad').replace('-_class_of_', 'class').replace('class_of_', 'class')\
 .replace('percent', 'pct').replace('of_', '')\
 .replace('(','').replace(')','')\
 for old in irn_df.columns}
raw_irn_newoldcol_dict['Percent of 4 Year Graduation Cohort (Class of 2014) Earning 3 or More Dual Enrollment Credits']\
= 'pct_4year_grad_class2014_earning_3_or_more_credits'
raw_irn_newoldcol_dict['Percent of 4 Year Graduation Cohort (Class of 2014) Earning Industry Recognized Credentials']\
= 'pct_4_year_grad_class2014_earning_industry_recog_credentials'
raw_irn_newoldcol_dict['Phone #'] = 'phone'

new_irn_df = irn_df.rename(columns=raw_irn_newoldcol_dict)
new_irn_csv_name = irn_file.split('.')[0]+'.csv'
new_irn_df.to_csv(new_irn_csv_name, index=False)
print('Excel file column names corrected and saved as ', new_irn_csv_name)
print(os.popen("/home/jgutman/env/bin/python csv2postgres_mvesc.py -f\
/mnt/data/mvesc/PartnerData/IRNSandWithdrawalCodes/IRN_DORP_GRAD_RATE1415.csv -s public").read())
print(os.popen("/home/jgutman/env/bin/python csv2postgres_mvesc.py -f\
/mnt/data/mvesc/PartnerData/IRNSandWithdrawalCodes/IRN_DORP_GRAD_RATE1415.csv -s raw").read())


#++++++ ~/PartnerData/IRNSandWithdrawalCodes/IRN_DORP_GRAD_RATE1415.xls ++++++#
# -1. read Excel parser 
# -2. upload sheets one by one
filepath = '/mnt/data/mvesc/PartnerData/MVESC_DistrictRatings.xlsx'
excel_name = "DistrictRating"
schema1='raw'
schema2='public'
print('\n--- processing: ', filepath)
xl = pd.ExcelFile(filepath)
for sheet_name in xl.sheet_names:
    table_name = excel_name + sheet_name[-4:]
    tab_name_json = add_file2table_jsonfile(excel_name+'->'+sheet_name, table_name)
    if tab_name_json==None:
        print("""File "{}":"{}": table name mapping conflict! Uploading suspended! """.format(excel_name+'->'+sheet_name, table_name))
        continue 
    df = xl.parse(sheet_name)
    names = list(df.columns)
    newnames = ['_'.join(re.split('[, _\-#\(\)]+', name)).replace("%", 'pct').lower() for name in names ]
    def check_name_long(names, length=63):
        long_names = filter(lambda x: len(x)>length, names)
        return list(long_names)
    #print("Long column names:\n", check_name_long(newnames))
    newnames = [name[:63] for name in newnames]
    newnames_dict={names[i]:newnames[i] for i in range(len(names))}
    df = df.rename(columns=newnames_dict)
    table_name = df2postgres(df, table_name, nrows=-1, if_exists='replace', schema=schema1)
    table_name = df2postgres(df, table_name, nrows=-1, if_exists='replace', schema=schema2)
    print("sheet-table uploaded to mvesc: ", table_name)


#++++++ ~/PartnerData/MVESC_Mobility.xlsx ++++++#
# -1. read Excel parser 
# -2. upload sheets one by one
filepath='/mnt/data/mvesc/PartnerData/MVESC_Mobility.xlsx'
table_name = "Mobility_2010_2015"
schema1 = 'raw'
schema2 = 'public'
print('\n--- processing: ', filepath)
tab_name_json = add_file2table_jsonfile(filepath.split('/')[-1], table_name)
if tab_name_json==None:
    print("""File "{}":"{}": table name mapping conflict! Uploading suspended! """.format(filepath.split('/')[-1], table_name))
else:
    df_Mobility = pd.read_excel(filepath, skiprows=1)
    df_Mobility2 = pd.read_excel(filepath)
    first3cols = ['district_code', 'district', 'metrics']
    col1=df_Mobility.columns[3:] # only columns which need to be combined
    col2=df_Mobility2.columns[3:]

    new_colnames = first3cols + [combine_colnames(col1[i], col2[i]) for i in range(len(col1)) ]
    new_colnames_dict = {df_Mobility.columns[i]:new_colnames[i] for i in range(len(new_colnames))}
    df_Mobility=df_Mobility.rename(columns=new_colnames_dict)
    df_Mobility=df_Mobility.drop('metrics', axis=1)
    table_name = df2postgres(df_Mobility, table_name, nrows=-1, if_exists='replace', schema=schema1)
    table_name = df2postgres(df_Mobility, table_name, nrows=-1, if_exists='replace', schema=schema2)
    print("table uploaded to mvesc: ", table_name)


#++++++ ~/PartnerData/IRNSandWithdrawalCodes/JVSD_Contact_Information_20160531.xlsx ++++++#
# -1. read Excel file 
# -2. upload the table
schema1 = 'raw'
schema2 = 'public'
jvsd_fn = '/mnt/data/mvesc/PartnerData/IRNSandWithdrawalCodes/JVSD_Contact_Information_20160531.xlsx'
table_name = 'JVSD_Contact'
print('\n--- processing: ', jvsd_fn)
jvs_df = pd.read_excel(jvsd_fn, sheetname=0)
newcol_dict = {col:col.lower() for col in jvs_df.columns}
jvs_df = jvs_df.rename(columns=newcol_dict)
tab_name_json = add_file2table_jsonfile(jvsd_fn.split('/')[-1], table_name)
if tab_name_json==None:
    print("""File "{}":"{}": table name mapping conflict! Uploading suspended! """.format(filepath.split('/')[-1], table_name))
else:
    table_name = df2postgres(jvs_df, table_name, nrows=-1, if_exists='replace', schema=schema1)
    table_name = df2postgres(jvs_df, table_name, nrows=-1, if_exists='replace', schema=schema2)
    print("table uploaded to mvesc: ", table_name)

