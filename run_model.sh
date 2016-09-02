#!/bin/bash

source config

# depends on run_ETL and run_Features 

############## Running Models ##############

mkdir -p $OUTPUT_PATH

while read p; do
    echo "-- uploading " $p
if [ ${MODEL_OPTIONS: -5} == ".yaml" ]; then
    $PYTHON_PATH Models_Results/estimate_prediction_model.py -m $MODEL_OPTIONS -g $GRID_OPTIONS -s $MODEL_SCHEMA -p $OUTPUT_PATH
elif [ -d "${MODEL_OPTIONS}" ]; then
    for OPTIONS_FILE in $MODEL_OPTIONS; do
	$PYTHON_PATH Models_Results/estimate_prediction_model.py -m $OPTIONS_FILE -g $GRID_OPTIONS -s $MODEL_SCHEMA -p $OUTPUT_PATH
    done
else
    echo "MODEL_OPTIONS not a directory or a yaml file"
fi


