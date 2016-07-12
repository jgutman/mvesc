# Initial v0.0 for executing a model estimation procedure
#	"model" = any predictive method, not necessarily "model-based"

###
# Psuedocode Outline #
###

# (1) Create options file used to generate features
# 	OR Read in an existing human-created options file
#		- get a user-entered text description of this specific run

modelOptions = {'modelClassSelected' : 'logistic',\
	'n_folds' = 10,
	}

# (2) Based on options, select the appropriate
#	- labeled outcome column
#	- subset of various feature columns from various tables
# and combine into one DataFrame.

# get labeled outcomes
outcomes_with_student_lookup = read_table_to_df(postgres_pgconnection_generator(), 'labels', \
	schema = 'model', nrows = -1)

# get demographic features
#	use table named 'demographics'
features_demographic = read_table_to_df(postgres_pgconnection_generator(), 'demographics', \
	schema = 'model', nrows = -1)
#	TODO: write a function to read in only specific columns

# 	join to only keep features that have labeled outcomes
joint_label_features = merge(outcomes_with_student_lookup, features_demographic,\
		how = 'left', on = ['student_lookup'])

# (3) Use the gathered DataFrame(s) in a predictive technique function
# Steps:
#	- manage held out datasets or cross-validation
#	- record the inputs and parameters used
#	- run the prediction technique
#	- record the output model
#	- record the model performance (various metrics) on train & test
#		* precision, recall
#		* AUROC, ROC graphic

from sklearn.linear_model import LogisticRegression
from sklearn.cross_validation import KFold
from sklearn.externals import joblib

def measure_performance(outcomes, predictions):
	""" 

	:param array outcomes:
	:param array predictions:
	"""
	performance_objects = {}
	performance_objects['pr_curve'] = sklearn.metrics.precision_recall_curve()
	performance_objects['roc_curve'] = sklearn.metrics.roc_curve()
	performance_objects['auc_score'] = sklearn.metrics.roc_auc_score()

	return performance_objects

def initialize_model(modelClassSelected):
	if (modelClassSelected == 'logistic'):
		modelClass = LogisticRegression()

	return modelClass

# 	save the random seed used
thisRandomSeed = np.randint(1000)
set.seed(thisRandomSeed)
# 	initialize model class
modelClass = initialize_model(model)

kf = KFold(n = joint_label_features.shape[0], n_folds = modelOptions.n_folds)
#	for each fold, apply measure_performance() and record
folds_performance_all = list()
for k, (train, test) in enumerate(kf):
	# run model
	fold_fitted_model = logit.fit(X = train[-'student_lookup'], y = train['student_lookup'])
	# save measure_performance() results
	folds_performance_all.append(...)

# (4) Save the recorded inputs, model, performance, and text description
#	into a results folder
#		according to documentation, use joblib instead?
#		save as a .pkl extension
joblib.dump(folds_performance_all, 'results/' + label_type_folder + user_file_name)
#		also store thisRandomSeed, option inputs, train/test split indices, and time to completion