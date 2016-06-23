"""
MVESC Project

Upload raw csv data into postgres database
Team Ohio, DSSG 2016
"""

"""
How to use this script

1. update the json file "file_to_table_name.json" with the 
   format of "data_file_name: corresponding_table_name";
   only file:table_name in the json file will be uploaded.
2. specify file/directory to upload with options;
   Usage example:
   upload a file: 
	python csv2postgres_mvesc.py -f /mnt/data/PartnerData/OAAGAT.txt
   upload a directory:
	python csv2postgres_mvesc.py -d /mnt/data/PartnerData 
   check help message for more options: 
	python csv2postgres_mvesc.py -h
"""



import os
from os.path import isfile, join, abspath, basename
from optparse import OptionParser
import sys
import numpy as np
import pandas as pd
import psycopg2 as pg
import re
from sqlalchemy import create_engine
import sqlalchemy


# functions to read and dump csv to sql server
def postgresql_engine_generator_mvesc():
    """ generate a string to create postgres engine
    Note: you can only run it on the mvesc-AWS-server
    :param None: None
    :return str sql_eng_str: string for function create_engine() in sqlalchemy
    :rtype str
    """
    pass_file = "/mnt/data/mvesc/pgpass" # file of credential information
    with open(pass_file, 'r') as f:
        passinfo = f.read()
    passinfo = passinfo.strip().split(':')
    host_address = passinfo[0]
    port = passinfo[1]
    user_name = passinfo[2]
    name_of_database = passinfo[3]
    user_password = passinfo[4]
    sql_eng_str = "postgresql://"+user_name+":"+user_password+"@"+host_address+'/'+name_of_database
    return sql_eng_str

def read_csv_noheader(filepath):
    """ read a csv file with no header
    
    :param str filepath: file path name
    :return pandas.DataFrame with header 'col1', 'col2', ...
    :rtype pandas.DataFrame
    """
    df = pd.read_csv(filepath, header=None, low_memory=False) # read csv data with no header
    colnames = {i:'col'+str(i) for i in df.columns} # rename column names of col0, col1, col2, ... 
    df = df.rename(columns=colnames)
    return df

def csv2postgres_file(filepath, header=False, nrows=-1, if_exists='fail', schema="raw"):
    """ upload csv file to postgres database
    
    :param str filepath: file path name
    :param bool header: True means there is header;
    :return str table_name: table name of the sql table
    :rtype str
    """
    # read the data frame with or without header
    if header:
        df = pd.read_csv(filepath, low_memory=False)
    else:
        df = read_csv_noheader(filepath) # header: col0, col1, col2
    
    # create a postgresql engine to wirte to postgres
    from sqlalchemy import create_engine
    import json
    sqlalchemy_eng = postgresql_engine_generator_mvesc() # a string with info to create engine
    engine = create_engine(sqlalchemy_eng)
    
    # get existing table names in the DB and schema 
    sqlcmd_table_names = "SELECT table_name FROM information_schema.tables WHERE table_schema = '%s'" % schema
    conn = engine.raw_connection()
    all_table_names = list(pd.read_sql(sqlcmd_table_names, conn).table_name)
    conn.close()
 
    #write the data frame to postgres
    file_name = filepath.split('/')[-1]
    file_table_names = json.load(open('file_to_table_name.json','r')) # load json of mapping from filenames to table names
    #table_name = filepath.split('/')[-1].split('.')[0] # table name is filename without .txt or other extension
    table_name = file_table_names[file_name] # get the table name
    
    # check existing tables in sql first to avoid errors
    if table_name not in all_table_names or if_exists=='replace':
        if nrows==-1: # upload all rows
            df.to_sql(table_name, engine, schema=schema, index=False, if_exists=if_exists)
        else: # upload the first n rows
            df.iloc[:nrows, :].to_sql(table_name, engine, schema=schema, index=False, if_exists=if_exists)
    else:
        print "Table already in mvesc: ", table_name
    return table_name


def csv2postgres_dir(directory, header=False, nrows=-1, if_exists='fail', schema='raw'):
    """ upload a directory of csv files to postgres database
    
    :param str filepath: file path name
    :param bool header: True means there is header;
    :return str table_names: table names of the sql tables
    :rtype str
    """
    data_dir = directory
    data_file_names = os.listdir(data_dir) # get all filenames in a directory
    # full path name of filenames
    fnames = [data_dir + fn for fn in data_file_names]
    table_names = []
    for filepath in fnames:
        print("working on ", filepath)
        tab_name = csv2postgres_file(filepath, header=header, nrows=nrows, if_exists=if_exists, schema=schema)
        table_names.append(tab_name)
    return table_names
    

if __name__ == '__main__':
	# options of this script
	parser = OptionParser()
	parser.add_option('-f','--file', dest='filename_to_upload',
                      help='abs path of one file; just upload this one')
	parser.add_option('-d','--dir', dest='dir_to_upload',
                      help='abs path of a dir; upload everything in this dir')
	parser.add_option('-s','--schema', dest='schema_to_upload',
                      help='schema to upload to in the database; default: \'raw\'')
	parser.add_option('-r','--header', dest='header_TrueFalse',
                      help='whether there is header or not:True, False; default: True')
	parser.add_option('-n','--nrows', dest='nrows',
                      help='number of rows to upload; default: all rows' )
	parser.add_option('-e', '--ifexists', dest='if_exists', 
		      help='option if the table exists in the schema: \'fail\' or \'replace\'; default: \'fail\'')
      
	(options, args) = parser.parse_args()

    ### Parameters to entered from the options or use default####
	schema = 'raw'
	if options.schema_to_upload:
		schema = options.schema_to_upload

	header = True
	if options.header_TrueFalse:
		if options.header_TrueFalse.lower()=='false':
			header = False

	nrows=-1
	if options.nrows:
		nrows = int(options.nrows)

	if_exists = 'fail'
	if options.if_exists:
		if_exists = options.if_exists
	
	if options.filename_to_upload:
		print "Preparing file %s to upload to postgresql" % options.filename_to_upload
		table_name = csv2postgres_file(options.filename_to_upload, header=header, nrows=nrows, if_exists=if_exists, schema=schema)
		print "Table uploaded: ", table_name, '\n'
	elif options.dir_to_upload:
		directory = options.dir_to_upload
		if directory[-1]!='/':
			directory = directory+'/'
		print "Preparing dir %s to upload to postgresql" % options.dir_to_upload
		table_names = csv2postgres_dir(directory, header=header, nrows=nrows, if_exists=if_exists, schema=schema)
		print "Tables uploaded:", table_names, '\n'
	else:
		print 'No files specified to upload...quiting\n'                    
