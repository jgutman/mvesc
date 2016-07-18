# Initial v0.0 for executing a model estimation procedure
#    "model" = any predictive method, not necessarily "model-based"

import os, sys
pathname = os.path.dirname(sys.argv[0])
full_pathname = os.path.abspath(pathname)
split_pathname = full_pathname.split(sep="mvesc")
base_pathname = os.path.join(split_pathname[0], "mvesc")
parentdir = os.path.join(base_pathname, "ETL")
sys.path.insert(0,parentdir)
from mvesc_utility_functions import *

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.grid_search import ParameterGrid
from sklearn.grid_search import GridSearchCV
from sklearn.cross_validation import *
from sklearn.externals import joblib
from sklearn.metrics import precision_recall_curve
from sklearn.metrics import roc_curve

import yaml
import numpy as np
import pandas as pd

def df2num(rawdf):
    """ Convert data frame with numeric variables and strings to numeric dataframe

    :param pd.dataframe rawdf: raw data frame
    :returns pd.dataframe df: a data frame with strings converted to dummies, other columns unchanged
    :rtype: pd.dataframe
    Rules:
    - 1. numeric columns unchanged;
    - 2. strings converted to dummies;
    - 3. the most frequent string is taken as reference category and dropped
    - 4. new column name is: "ColumnName_Category"
    (e.g., column 'gender' with 80 'M' and 79 'F'; the dummy column left is 'gender_F')
    """

    numeric_df = rawdf.select_dtypes(include=[np.number])
    str_columns = [col for col in rawdf.columns if col not in numeric_df.columns]
    dummy_col_df = pd.get_dummies(rawdf[str_columns], dummy_na=True)
    numeric_df = numeric_df.join(dummy_col_df)
    most_frequent_values = rawdf[str_columns].mode().loc[0].to_dict()
    reference_cols = ["{}_{}".format(key, value) for
        key, value in most_frequent_values.items()]
    numeric_df.drop(reference_cols, axis=1, inplace=True)
    return numeric_df

######
# Setup Modeling Options and Functions

def define_clfs_params():
    clfs = {'logit': LogisticRegression(),
    'DT': DecisionTreeClassifier()
    }

    grid = {'logit': {},
        'DT': {}
    }
    return clfs, grid


# For reference, taken from Rayid's magic loops code
"""
def define_clfs_params():

    clfs = {'RF': RandomForestClassifier(n_estimators=50, n_jobs=-1),
        'ET': ExtraTreesClassifier(n_estimators=10, n_jobs=-1, criterion='entropy'),
        'AB': AdaBoostClassifier(DecisionTreeClassifier(max_depth=1), algorithm="SAMME", n_estimators=200),
        'LR': LogisticRegression(penalty='l1', C=1e5),
        'logit': LogisticRegression(),
        'SVM': svm.SVC(kernel='linear', probability=True, random_state=0),
        'GB': GradientBoostingClassifier(learning_rate=0.05, subsample=0.5,
        max_depth=6, n_estimators=10),
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
    return clfs, grid
"""

def clf_loop(clfs, params, criterion, models_to_run, cv_folds,
    X_train, y_train):
    best_validated_models = dict()
    for index,clf in enumerate([clfs[x] for x in models_to_run]):
        model_name=models_to_run[index]
        print(model_name)
        parameter_values = params[models_to_run[index]]
        param_grid = ParameterGrid(parameter_values)
        best_validated_models[model_name] = GridSearchCV(clf, param_grid, scoring=criterion, cv=cv_folds)
        best_validated_models[model_name].fit(X_train, y_train)

        model_cv_score = best_validated_models[model_name].best_score_
        print("model: {model} score: {score}".format(
            model=model_name, score=model_cv_score)
    return best_validated_models

def temporal_cohort_test_split(joint_df, cohort_grade_level_begin,
    cohorts_held_out):
    """ Splits the given joint_df of features & outcomes and
    returns a train/test dataset
    :param pd.DataFrame joint_df:
    :param list[int] cohorts_held_out:
    """
    train = joint_df[~joint_df[cohort_grade_level_begin].isin(cohorts_held_out)]
    test = joint_df[joint_df[cohort_grade_level_begin].isin(cohorts_held_out)]
    return train, test

def measure_performance(outcomes, predictions):
    """ Returns a dict of model performance objects
    :param list[int] outcomes:
    :param list[float] predictions:
    """
    performance_objects = {}
    performance_objects['pr_curve'] = precision_recall_curve(y = outcomes,
        probas_pred = predictions)
    performance_objects['roc_curve'] = roc_curve(y_true = outcomes,
        y_score = test_prob_preds)
    return performance_objects

def build_outcomes_plus_features(model_options):
    with postgres_pgconnection_generator() as connection:
        # get labeled outcomes
        # Assumes:
        # model.outcome table contains a column (name given in cohort_grade_level_begin) for each cohort base year we choose
        # e.g. 'cohort_9th' contains the year each student is seen in 9th grade
        # and contains an outcome column (name given in outcome_name)
        # and 'student_lookup' columns
        # Usage:
        # select train, validation, and test based on values in column
        # 'cohort_grade_level_begin' according to value in 'cohorts_held_out'
        outcomes_with_student_lookup = read_table_to_df(connection,
            table_name = 'outcome', schema = 'model', nrows = -1,
            columns = ['student_lookup', model_options['outcome_name'], model_options['cohort_grade_level_begin']])
        # drop students without student_lookup, outcome, or cohort identifier
        # can use subset = [colnames] to drop based on NAs in certain columns only
        outcomes_with_student_lookup.dropna(inplace=True)
        joint_label_features = outcomes_with_student_lookup.copy()

        # get all requested input features
        # Assumes:
        # every features table contains 'student_lookup'
        # plus a column for the requested possible features

        for table, column_names in model_options['features_included'].items():
            features = read_table_to_df(connection, table_name = table,
                schema = 'model', nrows = -1,
                columns=(['student_lookup'] + column_names))
        # join to only keep features that have labeled outcomes
            joint_label_features = pd.merge(joint_label_features, features,
                how = 'left', on = 'student_lookup')

    # build dataframe containing student_lookup, outcome, cohort,
    # and all features as numeric non-categorical values
    joint_label_features.set_index('student_lookup', inplace=True)
    joint_label_features = df2num(joint_label_features)
    return joint_label_features

def read_in_yaml(filename='model_options.yaml'):
    with open(filename, 'r') as f:
        model_options = yaml.load(f)
    assert(type(model_options)==dict)
    assert(type(model_options['features_included']==dict))
    return model_options


def main():
# Create options file used to generate features
# OR Read in an existing human-created options file

# The model options needs to read in what tables to draw features from
# and what columns to draw from each of those tables
# Also needs to read in an option to output all results to a database

    model_options = read_in_yaml()

    # set seed for this program from model_options
    np.random.seed(model_options['random_seed'])

    # Based on options, draw in data and select the appropriate
    # labeled outcome column (outcome_name)
    # cohort identification column (cohort_grade_level_begin)
    # subset of various feature columns from various tables (features_included)

    outcome_plus_features = build_outcomes_plus_features(model_options)

    # Use the gathered DataFrame in a predictive model
    # Steps:
    #   - (A) manage test and validation folds
    #   - (B) run the prediction technique across all validation folds
    #   - (C) record the inputs and parameters used

    # (4A) Choose cohort(s) for test and validation data
    # Validation Process
    # Use temporal split for creating the test set
    # Use cohort-fold cross-validation for parameter search and model selection
    #    - temporal (using recent cohorts as a validation set)
    #    - k-fold cross (using all cohorts and all years of features)
    #    - cohort-fold cross validation (leave one cohort out)

    if model_options['model_test_holdout'] == 'temporal_cohort':
        # if using temporal cohort model performance validation,
        # we choose the cohorts in cohorts_held_out for the test set
        train, test = temporal_cohort_test_split(outcome_plus_features,
            model_options['cohort_grade_level_begin'],
            model_options['cohorts_held_out'])

    else:
        # if not using temporal test set, split randomly
        train, test = train_test_split(outcome_plus_features, test_size=0.20,
            random_state=model_options['random_seed']))

    # get subtables for each for easy reference
    train_X = train.drop([model_options['outcome_name'],
        model_options['cohort_grade_level_begin']],axis=1)
    test_X = test.drop([model_options['outcome_name'],
        model_options['cohort_grade_level_begin']],axis=1)
    train_y = train[model_options['outcome_name']]
    test_y = test[model_options['outcome_name']]

    ####
    # From now on, we IGNORE the `test`, `test_X`, `test_y` data until we evaluate the model
    ####

    ## (4B) Fit on Training ##
    # if we require cross-validation of parameters, we can either
    #    (a) hold out another cohort in each fold for cross-validation
    #    (b) fold all cohorts together for k-fold parameter estimation
    clfs, params = define_clfs_params()

    if model_options['parameter_cross_validation_scheme'] == 'none':
        # no need to further manipulate train dataset
        cohort_kfolds = 2 # hacky way to have GridSearchCV fit to 2 k-folds

    elif model_options['parameter_cross_validation_scheme'] == 'leave_cohort_out':
        # choose another validation set amongst the training set to
        # estimate parameters and model selection across cohort folds
        print('leave_cohort_out')
        cohort_kfolds = LeaveOneLabelOut(train[
                model_options['cohort_grade_level_begin']])

    elif model_options['parameter_cross_validation_scheme'] == 'k_fold':
        # ignore cohorts and use random folds to estimate parameter
        print('k_fold_parameter_estimation')
        cohort_kfolds = LabelKFold(train.index,
            n_folds=model_options[n_folds])

    else:
        print('unknown cross-validation strategy')

    # best_validated_models is a dictionary whose keys are the model
    # nicknames in model_classes_selected and values are objects
    # returned by GridSearchCV
    best_validated_models = clf_loop(clfs, params,
        criterion=model_options['validation_criterion'],
        models_to_run=model_options['model_classes_selected'],
        cv_folds=cohort_kfolds, train_X, train_y)

    test_set_metrics = dict()
    for model_name, model in best_validated_models.items():
        print(model_name)
        clf = model.best_estimator_
        if hasattr(clf, "decision_function"):
            test_set_scores = clf.decision_function(test_X)
        else:
            test_set_scores = clf.predict_proba(test_X)
        test_set_metrics[model_name] = test_set_scores

    ## (4C) Save Results ##
    # Save the recorded inputs, model, performance, and text description
    #    into a results folder
    #        according to sklearn documentation, use joblib instead of pickle
    #            save as a .pkl extension
    #        store option inputs (randomSeed, train/test split rules, features)
    #        store time to completion [missing]

    saved_outputs = {
        'estimated_fit' : estimated_fit,
        'model_options' : model_options, # this also contains cohort_grade_level_begin for train/test split
        'test_y' : test_y,
        'test_prob_preds' : test_prob_preds,
        'performance_objects' : measure_performance(test_y, test_prob_preds),
    }

    # save outputs
    joblib.dump(saved_outputs, os.path.join(
    '/mnt/data/mvesc/Model_Results/skeleton/',
        model_options['file_save_name']))

    # write output summary to a database
    #    - (A) write to a database table to store summary
    #    - (B) write to and update an HTML/Markdown file
    #    to create visual tables and graphics for results

    db_saved_outputs = {
    'train_f1': f1_score(train_y, train_prob_preds),
    'test_f1': f1_score(test_y, test_prob_preds)
    }

    #db_saved_outputs.update(model_options)

    #with postgres_pgconnection_generator() as connection:
    #    with connection.cursor() as cursor:
    #        build_results_table(cursor)
    #        add_row(db_saved_outputs)

if __name__ == '__main__':
    main()
