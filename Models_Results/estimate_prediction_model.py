# Initial v0.0 for executing a model estimation procedure
#	"model" = any predictive method, not necessarily "model-based"

###
# Psuedocode Outline #
###

# Create options file used to generate features
# OR Read in an existing human-created options file

# Run generate_features.py and receive a dataframe in return

# Use the resulting dataframe in a predictive technique function
# Steps:
#	- manage held out datasets or cross-validation
#	- record the inputs and parameters used
#	- get a user-entered text description of this specific run
#	- run the prediction technique
#	- record the output model
#	- record the model performance (various metrics) on train & test
#		* precision, recall
#		* AUROC, ROC graphic

# Save the recorded inputs, model, performance