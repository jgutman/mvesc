# Initial v0.0 for executing a model estimation procedure
#	"model" = any predictive method, not necessarily "model-based"

import os, sys
parentdir = os.path.abspath('/home/zzhang/mvesc/ETL')
sys.path.insert(0,parentdir)
from mvesc_utility_functions import *

######
# (1) Create options file used to generate features
# 	OR Read in an existing human-created options file

modelOptions = {'model_class_selected' : 'logit',
	'model_performance_estimate_scheme' : 'temporal_cohort',
	'parameter_cross_validation_scheme' : 'none',
	'n_folds' : 10,
	'file_save_name' : 'gender_ethnicity_logit.pkl',
	'randomSeed' : 2187,
	'user_description' : """initial skeleton pipeline test""",
	'cohort_chosen' : 'cohort_9th',
	'cohorts_held_out' : [2015]
	}
# 	set seed for this program from modelOptions
np.random.seed(modelOptions['randomSeed'])

######
# (2) Based on options, draw in data and select the appropriate
#	- labeled outcome column
#	- subset of various feature columns from various tables

with postgres_pgconnection_generator() as connection:
	# get labeled outcomes
	# Assumes:
	#	labels table contains a column for each cohort base year we choose
	#		e.g. 'cohort_9th' contains the years each student is seen in 9th grade
	#	and contains a 'outcome' and 'student_lookup' columns
	# Usage: 
	#	we use the various 'cohort_Nth' columns to choose train and test groups
	outcomes_with_student_lookup = read_table_to_df(connection, table_name = 'labels', \
		schema = 'model', nrows = -1)

	# get demographic features
	# Assumes:
	#	demographics table contains 'student_lookup' plus a column for each possible 
	#	feature
	features_demographic = read_table_to_df(connection, table_name = 'demographics', \
		schema = 'model', nrows = -1)

# 	join to only keep features that have labeled outcomes
joint_label_features = pd.merge(outcomes_with_student_lookup, features_demographic,\
		how = 'left', on = ['student_lookup'])

def df2num(rawdf):
    """ Convert data frame with numeric variables and strings to numeric dataframe
    
    :param pd.dataframe rawdf: raw data frame
    :returns pd.dataframe df: a data frame with strings converted to dummies, other columns unchanged
    :rtype: pd.dataframe
    Rules:
    - 1. numeric columns unchanged;
    - 2. strings converted to dummeis;
    - 3. the most frequenct string is taken as reference
    - 4. new column name is: "ColumnName_Category"
    (e.g., column 'gender' with 80 'M' and 79 'F'; the dummy column left is 'gender_F')

    """
    numeric_types = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
    numeric_df = rawdf.select_dtypes(include=numeric_types)
    str_columns = list(filter(lambda x: x not in numeric_df.columns, rawdf.columns))
    for col in str_columns:
        dummy_col_df = pd.get_dummies(rawdf[col])
        col_names = dummy_col_df.columns
        col_names = {cat:col+'_'+cat for cat in col_names }
        dummy_col_df = dummy_col_df.rename(columns=col_names)
        most_class_col = dummy_col_df.sum().idxmax()
        dummy_col_df = dummy_col_df.drop([most_class_col], axis=1)
        numeric_df = numeric_df.join(dummy_col_df)
    return numeric_df

######
# (3) Setup Modeling Options and Functions

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.cross_validation import KFold
from sklearn.externals import joblib
from sklearn.metrics import precision_recall_curve
from sklearn.metrics import roc_curve
from sklearn.metrics import confusion_matrix
from sklearn.metrics import f1_score
import save_reports

clfs = {'logit': LogisticRegression(),
	'DT': DecisionTreeClassifier()
	}

grid = {'logit': {},
	'DT': {}
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

def temporal_cohort_train_split(joint_df, cohort_chosen, cohorts_held_out):
	""" Splits the given joint_df of features & outcomes and
	returns a train/test dataset
	:param DataFrame joint_df:
	:param list cohorts_held_out:
	"""
	train = joint_df[~joint_df[cohort_chosen].isin(cohorts_held_out)]
	test = joint_df[joint_df[cohort_chosen].isin(cohorts_held_out)]

	return train, test

def measure_performance(outcomes, predictions):
        """ Returns a dict of model performance objects

        :param array outcomes:
        :param array predictions:
        """
        performance_objects = {}
        performance_objects['pr_curve'] = precision_recall_curve(y = outcomes, 
                                                        probas_pred = predictions)
        performance_objects['roc_curve'] = roc_curve(y_true = outcomes, 
                                                     y_score = test_prob_preds)
        performance_objects['confusion_matrix'] = confusion_matrix(outcomes, test_prob_preds)
        return performance_objects

#### END FUNCTIONS ####


######
# (4) Use the gathered DataFrame(s) in a predictive technique function
# Steps:
#	- (A) manage held out datasets or cross-validation
#	- (B) run the prediction technique
#	- (C) record the inputs and parameters used

# (4A) Choose cohort for held out data
# Validation Process #
# we decide to start with temporal model validation
#	- temporal (using recent cohorts as a validation set)
#	- k-fold cross (using all cohorts and all years of features)
#	- cohort-fold cross validation (leave one cohort out)

if modelOptions['model_performance_estimate_scheme'] == 'temporal_cohort':
    # if using temporal cohort model performance validation,
    # e choose the most recent cohort(s) for held out
    train, test = temporal_cohort_train_split(joint_label_features, 
                                              modelOptions['cohort_chosen'],
                                              modelOptions['years_held_out'])
    # get subtables for each for easy reference
    train_X = train.drop(['student_lookup', 'outcome'])
    test_X = test.drop(['student_lookup', 'outcome'])
    train_y = train['outcome']
    test_y = test['outcome']
	 
else:
	# if not using, we could use built in k-fold validation to estimate performance_objects

####
# From now on, we IGNORE the `test`, `test_X`, `test_y` data until we evaluate the model
####

## (4B) Fit on Training ##
# (to)
# if we require cross-validation of parameters, we can either
#	(a) hold out another cohort in our training data, or
#	(b) fold all cohorts together for parameter estimation
if modelOptions['parameter_cross_validation_scheme'] == 'none':
	# no need to further manipulate train dataset

	clf = clfs[modelOptions['modelClassSelected']]
	# 	assume the following functions work for our clfs
	#	this may need more abstraction for model choice and parameter selection
	estimated_fit = clf.fit(X = train_X, y = train_y) 
	test_prob_preds = estimated_fit.predict(X = test_X)
        train_prob_preds = estimated_fit.predict(X = train_X)

elif modelOptions['parameter_cross_validation_scheme'] == 'leave_cohort_out':
	# choose another hold out set amongst the training set to estimate parameters
	# manipulate 
	print('leave_cohort_out')
elif modelOptions['parameter_cross_validation_scheme'] == 'k_fold':
	# ignore cohorts and use random folds to estimate parameter
	print('k_fold_parameter_estimation')


## (4C) Save Results ##
# Save the recorded inputs, model, performance, and text description
#	into a results folder
#		according to sklearn documentation, use joblib instead of pickle
#			save as a .pkl extension
#		store option inputs (randomSeed, train/test split rules, features)
#		store time to completion [missing]

saved_outputs = {
	'estimated_fit' : estimated_fit,
	'modelOptions' : modelOptions, # this also contains cohort_chosen for train/test split
	'test_y' : test_y,
	'test_prob_preds' : test_prob_preds,
	'performance_objects' : measure_performance(test_y, test_prob_preds),
}

# save outputs
joblib.dump(saved_outputs, '/mnt/data/mvesc/Model_Results/skeleton/' + modelOptions['file_save_name']) 

# write output summary to a database
#	- (A) write to a database table to store summary
#	- (B) write to and update an HTML/Markdown/Notebook file which processes
#		to create visual tables and graphics for results


db_saved_outputs = {
    'train_f1': f1_score(test_y,test_prob_preds),
    'test_f1': f1_score(train_y,train_prob_preds)
}
db_saved_outputs.update(model_options)

with postgres_pgconnection_generator() as connection:
    with connection.cursor() as cursor:
        build_results_table(cursor)
        add_row(db_saved_outputs)



