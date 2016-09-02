#!/bin/bash

source config

########## Generating Outcomes ##########

$PYTHON_PATH Features/generate_outcome.py $CLEAN_SCHEMA $MODEL_SCHEMA $CURRENT_YEAR

########## Generating Features ##########

$PYTHON_PATH Features/generate_features.py $CLEAN_SCHEMA $MODEL_SCHEMA 
