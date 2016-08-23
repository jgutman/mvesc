# Inital v0 of a script to take in options file and generate
#	the corresponding outcomes and features for prediction.
# Generates all possible features we're considering

# use this to get the 'execute_sql_script' function
import os, sys
pathname = os.path.dirname(sys.argv[0])
full_pathname = os.path.abspath(pathname)
split_pathname = full_pathname.split(sep="mvesc")
base_pathname = os.path.join(split_pathname[0], "mvesc")
parentdir = os.path.join(base_pathname, "ETL")
sys.path.insert(0,parentdir)
from mvesc_utility_functions import execute_sql_script

import generate_demographic_features
import generate_snapshot_features
import generate_mobility_features
import generate_consec_absence_columns
import generate_absence_features
import generate_gpa
import generate_normalized_oaa_pandas
import generate_intervention_features
####
# Pseudo-code Outline
####

# Check if `replace_feature_tables` option is T or F
#	if T, then we re-calculate all features
#	if F, then we only add new columns

# This option doesn't seem to be in use?

# (1) create various vectors of labeled outcomes, based on
#	different possible definitions
#	store this in a `clean.labeled_outcomes` table

# (2) for each category, execute sub-scripts to create
#	columns for various features. Examples: absences, grades, demographics
#		we can have one table in the DB for each category

print("--- working on generating model.demographics table ... ")
generate_demographic_features.main()
print("--- working on generating model.snapshots table ... ")
generate_snapshot_features.main()
print("--- working on generating model.absence table ... ")
generate_absence_features.main()
print("--- working on generating model.mobility table ... ")
generate_mobility_features.main()
print("--- working on generating model.grades table ... ")
generate_gpa.main()
print("--- working on generating model.oaa_normalized table ... ")
generate_normalized_oaa_pandas.main() # a bit slow due to for loop and writing to postgres from pandas
print("--- working on generating model.intervention table ... ")
generate_intervention_features.main()

# use feature utilities to execute the sql file
print("--- adding a new outcome to the model.outcome table based on ogt, absences, gpa")
execute_sql_script('add_new_outcome_on_ogt.sql')
