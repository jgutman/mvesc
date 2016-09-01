#!/bin/bash

export CLEAN_SCHEMA="clean2"
export MODEL_SCHEMA="model2"
export RAW_SCHEMA="raw"
export PYTHON_PATH="/home/jgutman/env/bin/python"
export PASS_FILE='/mnt/data/mvesc/pgpass'
export CURRENT_YEAR=2016
# schema names and pass_file are read into mvesc_utility_functions
# using python os.getenv

########### Uploading directories #########
echo "Uploading csvs in directories/files listed in filelist.txt"

while read p; do
    echo "-- uploading " $p
    $PYTHON_PATH ETL/raw2postgres/csv2postgres_mvesc.py -d $p -s $RAW_SCHEMA
done <ETL/filelist.txt


######### Uploading Excel Files #########

echo "Uploading excel files in excel2postgres_mvesc.py"
$PYTHON_PATH ETL/raw2postgres/excel2postgres_mvesc.py -s $RAW_SCHEMA

# ############ Cleaning Tables ############

$PYTHON_PATH ETL/clean_and_consolidate.py $RAW_SCHEMA $CLEAN_SCHEMA

# ########## Generating Outcomes ##########

$PYTHON_PATH Features/generate_outcome.py $CLEAN_SCHEMA $MODEL_SCHEMA $CURRENT_YEAR

# ########## Generating Features ##########
$PYTHON_PATH Features/generate_features.py $CLEAN_SCHEMA $MODEL_SCHEMA 
