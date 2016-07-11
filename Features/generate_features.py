# Inital v0 of a script to take in options file and generate
#	ths corresponding outcomes and features for prediction.


####
# Pseudo-code Outline
####

# read in options file

# gather the row of outcomes to predict

# gather features based on the provided options

# place the outcomes + features into (1 or 2) dataframes
#	pass this resulting dataframe back to the user to
#	use for modeling
#	ASSUME: size restrictions on passing data is okay