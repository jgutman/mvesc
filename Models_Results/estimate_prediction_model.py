# Initial v0.0 for executing a model estimation procedure
#	"model" = any predictive method, not necessarily "model-based"

###
# Psuedocode Outline #
###

import os, sys
parentdir = os.path.abspath('/home/zzhang/mvesc/ETL')
sys.path.insert(0,parentdir)
from mvesc_utility_functions import *

# (1) Create options file used to generate features
# 	OR Read in an existing human-created options file
#		- get a user-entered text description of this specific run

modelOptions = {'modelClassSelected' : 'logit', 
	'n_folds' : 10,
	'file_save_name' : 'gender_ethnicity_logit.pkl',
	'randomSeed' : 2187,
	'user_description' : """initial skeleton pipeline test"""
	}

# set seed for this program from modelOptions
np.random.seed(modelOptions['randomSeed'])

# (2) Based on options, select the appropriate
#	- labeled outcome column
#	- subset of various feature columns from various tables

with postgres_pgconnection_generator() as connection:
	# get labeled outcomes
	# outcomes_with_student_lookup = read_table_to_df(connection, table_name = 'labels', \
	# 	schema = 'model', nrows = -1)
	outcomes_with_student_lookup = pd.DataFrame({'student_lookup' : range(0,10000),
		'outcome' : np.random.randint(0, 2, 10000)})

	# get demographic features
	features_demographic = read_table_to_df(connection, table_name = 'demographics', \
		schema = 'model', nrows = -1)

# 	join to only keep features that have labeled outcomes
joint_label_features = pd.merge(outcomes_with_student_lookup, features_demographic,\
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
from sklearn.tree import DecisionTreeClassifier
from sklearn.cross_validation import KFold
from sklearn.externals import joblib
from sklearn.metrics import precision_recall_curve
from sklearn.metrics import roc_curve

clfs = {'logit': LogisticRegression(),
	'DT': DecisionTreeClassifier()
	}

# For reference, taken from Rayid's magic loops code
"""
def define_clfs_params:

    clfs = {'RF': RandomForestClassifier(n_estimators=50, n_jobs=-1),
        'ET': ExtraTreesClassifier(n_estimators=10, n_jobs=-1, criterion='entropy'),
        'AB': AdaBoostClassifier(DecisionTreeClassifier(max_depth=1), algorithm="SAMME", n_estimators=200),
        'LR': LogisticRegression(penalty='l1', C=1e5),
        'logit': LogisticRegression(),
        'SVM': svm.SVC(kernel='linear', probability=True, random_state=0),
        'GB': GradientBoostingClassifier(learning_rate=0.05, subsample=0.5, max_depth=6, n_estimators=10),
        'NB': GaussianNB(),
        'DT': DecisionTreeClassifier(),
        'SGD': SGDClassifier(loss="hinge", penalty="l2"),
        'KNN': KNeighborsClassifier(n_neighbors=3) 
            }

    grid = { 
    'RF':{'n_estimators': [1,10,100,1000,10000], 'max_depth': [1,5,10,20,50,100], 'max_features': ['sqrt','log2'],'min_samples_split': [2,5,10]},
    'LR': { 'penalty': ['l1','l2'], 'C': [0.00001,0.0001,0.001,0.01,0.1,1,10]},
    'SGD': { 'loss': ['hinge','log','perceptron'], 'penalty': ['l2','l1','elasticnet']},
    'ET': { 'n_estimators': [1,10,100,1000,10000], 'criterion' : ['gini', 'entropy'] ,'max_depth': [1,5,10,20,50,100], 'max_features': ['sqrt','log2'],'min_samples_split': [2,5,10]},
    'AB': { 'algorithm': ['SAMME', 'SAMME.R'], 'n_estimators': [1,10,100,1000,10000]},
    'GB': {'n_estimators': [1,10,100,1000,10000], 'learning_rate' : [0.001,0.01,0.05,0.1,0.5],'subsample' : [0.1,0.5,1.0], 'max_depth': [1,3,5,10,20,50,100]},
    'NB' : {},
    'DT': {'criterion': ['gini', 'entropy'], 'max_depth': [1,5,10,20,50,100], 'max_features': ['sqrt','log2'],'min_samples_split': [2,5,10]},
    'SVM' :{'C' :[0.00001,0.0001,0.001,0.01,0.1,1,10],'kernel':['linear']},
    'KNN' :{'n_neighbors': [1,5,10,25,50,100],'weights': ['uniform','distance'],'algorithm': ['auto','ball_tree','kd_tree']}
           }
"""


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


# (A) Choose cohort for held out data
# Validation Process #
# we decide to start with temporal model validation
#	- temporal (using recent cohorts as a validation set)
#	- k-fold cross (using all cohorts and all years of features)
#	- cohort-fold cross validation (leave one cohort out)

train = joint_label_features.query['cohort_year != 2015']
test = joint_label_features.query['cohort_year == 2015']
# get subtables for each
train_X = train.drop(['student_lookup', 'outcome'])
test_X = test.drop(['student_lookup', 'outcome'])
train_y = train['outcome']
test_y = test['outcome']

# 	fit the model on training data 
clf = clfs[modelOptions['modelClassSelected']]
estimated_fit = clf.fit(X = train_X, y = train_y)
test_prob_preds = estimated_fit.predict(X = test_X)

# (4) Save the recorded inputs, model, performance, and text description
#	into a results folder
#		according to documentation, use joblib instead?
#		save as a .pkl extension
#		also store thisRandomSeed, option inputs, train/test split indices, and time to completion

# 	store feature importance into the database

saved_outputs = {
	'estimated_fit' : estimated_fit,
	'modelOptions' : modelOptions,
	'pr_curve_data' : precision_recall_curve(y = test_y, probas_pred = test_prob_preds),
	'roc_curve_data' : roc_curve(y_true = test_y, y_score = test_prob_preds)
}

# save outputs
joblib.dump(saved_outputs, '/mnt/data/mvesc/Model_Results/skeleton/' + modelOptions['file_save_name'])