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
import os, sys
pathname = os.path.dirname(sys.argv[0])
full_pathname = os.path.abspath(pathname)
split_pathname = full_pathname.split(sep="mvesc")
base_pathname = os.path.join(split_pathname[0], "mvesc")
parentdir = os.path.join(base_pathname, "ETL")
sys.path.insert(0,parentdir)
from mvesc_utility_functions import *

from os.path import isfile, join, abspath, basename
from optparse import OptionParser
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
import sqlalchemy
import json


def fetch_or_add_file2table_jsonfile(datafile, jsonfile='../json/file_to_table_name.json'):
    """ Fetch table name from json file OR Add file:table to json
    
    step 1: check whether file and table exist in json file;
    step 2: if exist, return table_name; 
    if not exist, add file:table to json, then return table_name
    
    :param str datafile: datafile name, either absolute or relative path
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
    if '/' in datafile:
        datafile = datafile.split('/')[-1]
    if datafile in existing_keys:
        print("""File "{}" already in json with table name "{}" """.format(datafile, file_table_names[datafile]))
        return(file_table_names[datafile])
    else:
        table_name = datafile.split('.')[0]
        if table_name in existing_values:
            print("""Table "{}" already in json for a file """.format(table_name))
            return(None)
        else:
            file_table_names[datafile] = table_name
            with open(jsonfile, 'w') as f:
                json.dump(file_table_names, f, ensure_ascii=True, sort_keys=True, indent=4)
            print("""file:table "{}":"{}" added to json file """.format(datafile, file_table_names[datafile]))
            return table_name
    return(None)



def main():
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
        # create schema if not present
    with postgres_pgconnection_generator() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
            create schema if not exists {}
            """.format(schema))
            connection.commit()
        
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
        print("Preparing file %s to upload to psql" %
              options.filename_to_upload)
        table_name = csv2postgres_file(options.filename_to_upload,
                                       header=header, nrows=nrows, 
                                       if_exists=if_exists, 
                                       schema=schema)
        print("Table uploaded:", table_name)
    elif options.dir_to_upload:
        directory = options.dir_to_upload
        if directory[-1]!='/':
            directory = directory+'/'
        print("\nPreparing dir %s to upload to psql" % options.dir_to_upload)
        table_names = csv2postgres_dir(directory, header=header, nrows=nrows, if_exists=if_exists, schema=schema)
        print("\nTables uploaded:\n",table_names, "\n")
    else:
        print("No files specified to upload...quiting\n")

if __name__ == '__main__':
    main()
