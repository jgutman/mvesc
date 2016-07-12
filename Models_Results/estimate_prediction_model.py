# Initial v0.0 for executing a model estimation procedure
#	"model" = any predictive method, not necessarily "model-based"

###
# Psuedocode Outline #
###

# (1) Create options file used to generate features
# 	OR Read in an existing human-created options file
#		- get a user-entered text description of this specific run

# (2) Based on options, select the appropriate
#	- labeled outcome column
#	- subset of various feature columns from various tables
# and combine into one DataFrame.

# (3) Use the gathered DataFrame in a predictive technique function
# Steps:
#	- manage held out datasets or cross-validation
#	- record the inputs and parameters used
#	- run the prediction technique
#	- record the output model
#	- record the model performance (various metrics) on train & test
#		* precision, recall
#		* AUROC, ROC graphic

# (4) Save the recorded inputs, model, performance, and text description
#	into a results folder