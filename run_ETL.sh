#!/bin/bash

source config

# remember that any database backup files must be added manually

########### Uploading directories #########
# echo "Uploading csvs in directories/files listed in filelist.txt"

while read p; do
    echo "-- uploading " $p
    if [ ${p: -4} == ".txt" ]; then
	$PYTHON_PATH ETL/raw2postgres/csv2postgres_mvesc.py -f $p -s $RAW_SCHEMA
    elif [ ${p: -4} == ".csv" ]; then
	$PYTHON_PATH ETL/raw2postgres/csv2postgres_mvesc.py -f $p -s $RAW_SCHEMA
    else
	$PYTHON_PATH ETL/raw2postgres/csv2postgres_mvesc.py -d $p -s $RAW_SCHEMA
    fi
done <ETL/filelist.txt


# ######### Uploading Excel Files #########

echo "Uploading excel files in excel2postgres_mvesc.py"
$PYTHON_PATH ETL/raw2postgres/excel2postgres_mvesc.py -s $RAW_SCHEMA

############ Cleaning Tables ############

$PYTHON_PATH ETL/clean_and_consolidate.py $RAW_SCHEMA $CLEAN_SCHEMA
