# Inital v0 of a script to take in options file and generate
#	the corresponding outcomes and features for prediction.
# Generates all possible features we're considering


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