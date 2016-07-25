# Inital v0 of a script to take in options file and generate
#	the corresponding outcomes and features for prediction.
# Generates all possible features we're considering
import generate_demographic_features
import generate_snapshot_features

####
# Pseudo-code Outline
####

# Check if `replace_feature_tables` option is T or F
#	if T, then we re-calculate all features
#	if F, then we only add new columns

# (1) create various vectors of labeled outcomes, based on
#	different possible definitions
#	store this in a `clean.labeled_outcomes` table

# (2) for each category, execute sub-scripts to create
#	columns for various features. Examples: absences, grades, demographics
#		we can have one table in the DB for each category

print("--- working on generating model.demographics table ... ")
generate_demographic_features.main()
print("--- working on generating model.snapshots table ... ")
generate_snapshot_features.generate_raw_snapshot_features(replace=True)

print("--- working on generating model.absence table ... ")
# call function
print("--- working on generating model.mobility table ... ")
# call function
print("--- working on generating model.grades table ... ")
# call function
