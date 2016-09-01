#!/bin/bash

CLEAN_SCHEMA="clean2"
MODEL_SCHEMA="model2"
RAW_SCHEMA="raw"
PYTHON_PATH="/home/jgutman/env/bin/python"
PASS_FILE='/mnt/data/mvesc/pgpass'
CURRENT_YEAR=2016


########### Uploading directories #########
echo "Uploading csvs in directories/files listed in filelist.txt"

while read p; do
    echo "-- uploading " $p
    $PYTHON_PATH ETL/raw2postgres/csv2postgres_mvesc.py -d $p -s $RAW_SCHEMA
done <ETL/filelist.txt


######### Uploading Excel Files #########

echo "Uploading exvel files in excel2postgres_mvesc.py"
$PYTHON_PATH ETL/raw2postgres/excel2postgres_mvesc.py

# ############ Cleaning Tables ############

# $PYTHON_PATH ETL/clean_and_consolidate.py $RAW_SCHEMA $CLEAN_SCHEMA

# ########## Generating Outcomes ##########

# $PYTHON_PATH Features/generate_outcome.py $CLEAN_SCHEMA $MODEL_SCHEMA $CURRENT_YEAR

# ########## Generating Features ##########
# $PYTHON_PATH Features/generate_features.py $CLEAN_SCHEMA $MODEL_SCHEMA $CURRENT_YEAR
