# Initial v0.0 for executing a model estimation procedure
#    "model" = any predictive method, not necessarily "model-based"

import os, sys
pathname = os.path.dirname(sys.argv[0])
full_pathname = os.path.abspath(pathname)
split_pathname = full_pathname.split(sep="mvesc")
base_pathname = os.path.join(split_pathname[0], "mvesc")
parentdir = os.path.join(base_pathname, "ETL")
sys.path.insert(0, parentdir)
from mvesc_utility_functions import *
from save_reports import write_model_report
from write_to_database import summary_to_db, write_scores_to_db, next_id
from optparse import OptionParser

# all model import statements
from sklearn import svm # use svm.SVC kernel = 'linear' or 'rbf'
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, GradientBoostingClassifier, AdaBoostClassifier
from sklearn.linear_model import LogisticRegression, Perceptron, SGDClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB, MultinomialNB, BernoulliNB

#from sklearn.grid_search import ParameterGrid
from sklearn.grid_search import GridSearchCV
from sklearn.cross_validation import *
from sklearn.externals import joblib
from sklearn.metrics import precision_recall_curve, roc_curve, confusion_matrix
from sklearn.preprocessing import Imputer, StandardScaler, RobustScaler

import yaml
import numpy as np
import pandas as pd
import pickle

from my_timer import Timer
from custom_scorers import *

######
# Setup Modeling Options and Functions

# maybe this should be moved to a yaml or json file as well
def define_clfs_params(filename):
    # model_options[model_classes_selected] determines which of these models
    # are actually run, all parameter options in grid run for each selected model

    clfs = {
        'logit': LogisticRegression(),
        'LR_no_penalty': LogisticRegression(C=1e6),
        'DT': DecisionTreeClassifier(),
        'RF': RandomForestClassifier(n_estimators=50, n_jobs=-1),
        'ET': ExtraTreesClassifier(n_estimators=10, n_jobs=-1,
                                   criterion='entropy'),
        'AB': AdaBoostClassifier(DecisionTreeClassifier(max_depth=1),
                                 algorithm="SAMME", n_estimators=200),
        'SVM': svm.SVC(kernel='linear', probability=False),
        'GB': GradientBoostingClassifier(
            learning_rate=0.05, subsample=0.5, max_depth=6, n_estimators=10),
        'NB': GaussianNB(),
        'SGD': SGDClassifier(loss="hinge", penalty="l2"),
        'KNN': KNeighborsClassifier(n_neighbors=3)
    }

    with open(filename, 'r') as f:
        grid = yaml.load(f)

    return clfs, grid

def clf_loop(clfs, params, train_X, train_y,
        criterion, models_to_run, cv_folds):
    """
    Returns a dictionary where the keys are model nicknames (strings)
    and the values are GridSearchCV objects containing attributes like
    model.best_score_ and model.best_estimator_

    :param dict(str:estimator) clfs: clfs as returned by define_clfs_params
    :param dict(str:dict) params: grid of classifier hyperparameter options
        to grid search over as returned by define_clfs_params
    :param pandas.DataFrame train_X: index is student_lookup, columns are all
        features to train over in the model
    :param pandas.Series(int) train_y: index is student_lookup, value is 0 or 1
        for outcome label
    :param string criterion: evaluation criterion for model selection on the
        validation set, to be read in from model_options (e.g. 'f1')
    :param list[string] models_to_run: which models to actually run as read in
        from model_options (e.g. ['logit', 'DT'])
    :param sklearn.KFolds cv_folds: a KFolds generator object over the index
        given in train_X and train_y (a list of lists of student_lookups)
    :rtype dict(string: GridSearchCV)
    """
    best_validated_models = dict()
    validated_model_times = dict()
    for index,clf in enumerate([clfs[x] for x in models_to_run]):
        model_name=models_to_run[index]
        print(model_name)
        parameter_values = params[model_name]
        with Timer(model_name) as t:
            best_validated_models[model_name] = \
                GridSearchCV(clf, parameter_values,
                             scoring=criterion,
                             cv=cv_folds)
            best_validated_models[model_name].fit(train_X, train_y)
            validated_model_times[model_name] = t.time_check()

        model_cv_score = best_validated_models[model_name].best_score_
        print("model: {model}, best {criterion} score: {score}".format(
            model=model_name, criterion=criterion, score=model_cv_score))
    return best_validated_models, validated_model_times

def temporal_cohort_test_split(joint_df, cohort_grade_level_begin,
    cohorts_held_out, cohorts_training):
    """ Splits the given joint_df of features & outcomes and
    returns a train/test dataset
    :param pd.DataFrame joint_df: data frame with a cohort, outcome, and features
    :param list[int] cohorts_held_out: a list of years to split test set on
    :param string or list[int] cohorts_training: either the string 'all' or
        a list of years to include in the training, all years must precede
        the test set years in cohorts_held_out
    :returns two dataframes consisting of rows from joint_df, one for training
        and one to be used for testing
    :rtype pd.DataFrame, pd.DataFrame
    """
    if (cohorts_training=='all'):
        train = joint_df[~joint_df[cohort_grade_level_begin].isin(cohorts_held_out)]
        assert (np.max(train[cohort_grade_level_begin]) < min(cohorts_held_out)), \
            "Training years do not completely precede test years"
    else:
        assert (max(cohorts_training) < min(cohorts_held_out)), \
            "Training years do not completely precede test years"
        train = joint_df[joint_df[cohort_grade_level_begin].\
                         isin(cohorts_training)]
    test = joint_df[joint_df[cohort_grade_level_begin].isin(cohorts_held_out)]
    return train, test

def measure_performance(outcomes, predictions):
    """ Returns a dict of model performance objects
    :param list[int] outcomes:
    :param list[float] predictions:
    """
    performance_objects = {}
    performance_objects['pr_curve'] = precision_recall_curve(outcomes,
                                                             predictions)
    performance_objects['roc_curve'] = roc_curve(outcomes, predictions)
    return performance_objects

def build_outcomes_plus_features(model_options, subset_n=None):
    """
    Returns a pandas dataframe containing the student_lookup, cohort identifier,
    outcome variable, and all numerical or binarized features.
    Reads in the features and outcomes from database according to the
    specification given in model_options dictionary.
    :param dict model_options: all options read in from yaml file

    Assumes:
    model.outcome table contains a column (name in cohort_grade_level_begin)
    with int values identifying each student's cohort year
    e.g. 'cohort_9th' contains the year each student is seen in 9th grade
    and contains an outcome column (name given in outcome_name)
    and all feature and outcomes tables contain student_lookup

    Usage:
    select train, validation, and test based on values in column
    'cohort_grade_level_begin' according to value in 'cohorts_held_out'
    """
    with postgres_pgconnection_generator() as connection:
        outcomes_with_student_lookup = read_table_to_df(connection,
            table_name = 'outcome', schema = 'model', nrows = -1,
            columns = ['student_lookup',
            model_options['outcome_name'],
            model_options['cohort_grade_level_begin']])
        # drop students without student_lookup, outcome, or cohort identifier
        # can use subset=[colnames] to drop based on NAs in certain columns only
        outcomes_with_student_lookup.dropna(inplace=True)
        if subset_n:
            outcomes_with_student_lookup = outcomes_with_student_lookup.sample(n=subset_n)
        joint_label_features = outcomes_with_student_lookup.copy()

        # get all requested input features
        # Assumes:
        # every features table contains 'student_lookup'
        # plus a column for the requested possible features

        model_options['features_included'] = parse_features(
            model_options['features_included'],
            model_options['feature_grade_range'])

        for table, column_names in model_options['features_included'].items():
            for c in column_names:
                try:
                    grade =  int(c.split('_')[-1])
                except:
                    pass # ignoring features not connected to a grade level
                else:
                    assert grade < model_options['prediction_grade_level'], \
                           "feature {} after prediction window".format(c)
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

def parse_features(features_included_raw, feature_grade_range):
    features_included = dict()
    for table, feature_list in features_included_raw.items():
        feature_list_expanded = [feature.replace('*', '{}').format(
                                    '_gr_' + str(i))
                                    for i in feature_grade_range
                                    for feature in feature_list]
        feature_list_expanded = set(feature_list_expanded)
        features_included[table] = list(feature_list_expanded)
    return features_included

def read_in_yaml(filename=os.path.join(base_pathname,
        'Models_Results', 'model_options.yaml')):
    """
    This function contains assertions specific to the model options yaml file.
    Should only be used to read in the model options yaml file and not other
    kinds of yaml files.

    :param string filename: full path of yaml file containing model options
    :returns: a dictionary of model options and their values
    :rtype dict
    """
    with open(filename, 'r') as f:
        model_options = yaml.load(f)

    # Maybe we want to have default values for these options and replace
    # from a new yaml file as necessary
    assert(type(model_options) == dict), "bad formatting in yaml file"
    required_keys = set(('validation_criterion', 'features_included',
                         'cohorts_training','cohorts_held_out', 'file_save_name',
                         'model_classes_selected', 'outcome_name',
                         'cohort_grade_level_begin', 'model_test_holdout',
                         'random_seed'))
    assert (all([key in model_options.keys() for key in required_keys])), \
        "missing model specifications in yaml file"
    assert(type(model_options['features_included']) == dict), \
        "bad formatting in yaml file"
    assert(type(model_options['model_classes_selected']) == list),\
        "bad formatting in yaml file"
    assert(type(model_options['cohorts_held_out']) == list),\
        "bad formatting in yaml file"
    assert(type(model_options['cohorts_training']) == list or
        model_options['cohorts_training'] == 'all'),\
        "bad formatting in yaml file"
    return model_options

def scale_features(train, test, strategy):
    """
    """
    num_values_by_column = {x: len(train[x].unique()) for x in train.columns}
    zero_variance_columns = [k for k,v in num_values_by_column.items()
                             if v == 1]
    train.drop(zero_variance_columns, axis=1, inplace=True)
    test.drop(zero_variance_columns, axis=1, inplace=True)

    if (strategy == 'none'):
        return train, test

    elif(strategy == 'standard' or strategy == 'robust'):

        non_binary_columns = [k for k, v in num_values_by_column.items()
                              if v > 2]
        if (len(non_binary_columns) > 0):
            scaler = StandardScaler() if strategy == 'standard' else RobustScaler()
            train_non_binary = train[non_binary_columns]
            test_non_binary = test[non_binary_columns]
            scaler.fit(train_non_binary)
            train_non_binary = pd.DataFrame(scaler.transform(train_non_binary),
                columns = non_binary_columns, index = train.index)
            test_non_binary = pd.DataFrame(scaler.transform(test_non_binary),
                columns = non_binary_columns, index = test.index)

            train_scaled = train.drop(non_binary_columns, axis=1)
            test_scaled = test.drop(non_binary_columns, axis=1)
            train_scaled = train_scaled.merge(train_non_binary,
                left_index=True, right_index=True)
            test_scaled = test_scaled.merge(test_non_binary,
                left_index=True, right_index=True)
            return train_scaled, test_scaled
        else:
            return train, test

    else:
        print('unknown feature scaling strategy. try "{}", "{}", or "{}"'\
              .format('standard', 'robust', 'none'))
        return train, test

def add_null_dummies_train_test(train, test):
    """
    """
    train_null_columns = train.columns[train.isnull().sum() > 0]
    test_null_columns = test.columns[test.isnull().sum() > 0]
    null_column_set = set(train_null_columns).union(set(test_null_columns))
    null_columns = pd.indexes.base.Index(null_column_set)

    train_nullified = add_null_dummies(train, null_columns)
    test_nullified = add_null_dummies(test, null_columns)
    return train_nullified, test_nullified

def add_null_dummies(data, null_columns):
    data_null_columns = data[null_columns]
    data_null_dummies = data_null_columns.isnull()*1.0
    data_null_dummies.rename(columns=lambda x: x + '_isnull', inplace=True)
    data_plus_dummies = data.merge(data_null_dummies,
        left_index=True, right_index=True)
    return data_plus_dummies

def impute_missing_values(train, test, strategy):
    """
    """
    if (strategy=='none'):
        return train, test

    elif(strategy == 'mean_plus_dummies' or strategy == 'median_plus_dummies'):
         # add feature_isnull columns 0 or 1
        train, test = add_null_dummies_train_test(train, test)
        imputer = Imputer(strategy=strategy.split("_")[0])
        imputer.fit(train) # fit the imputer on the training mean/median
        train = pd.DataFrame(imputer.transform(train), # returns a numpy array
            columns = train.columns, index = train.index) # back to dataframe
        test = pd.DataFrame(imputer.transform(test),
            columns = test.columns, index = test.index)
        return train, test

    else:
        print('unknown imputation strategy. try "{}", "{}", or "{}"'.format(
            'mean_plus_dummies', 'median_plus_dummies', 'none'))
        return train, test

def run_all_models(model_options, clfs, params, save_location):
    # Based on options, draw in data and select the appropriate
    # labeled outcome column (outcome_name)
    # cohort identification column (cohort_grade_level_begin)
    # subset of various feature columns from various tables (features_included)
    
    subset_n = model_options['subset_n']
    outcome_plus_features = build_outcomes_plus_features(model_options, subset_n)
    # no null in the categorical values because we have feature_nan dummies
    # there may be null values in the cohort or outcome label columns
    # just drop these students from the data
    outcome_plus_features.dropna(subset=[model_options['outcome_name'],
        model_options['cohort_grade_level_begin']], inplace=True)
    # imputation should happen after splitting into train and test

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
            model_options['cohorts_held_out'],
            model_options['cohorts_training'])

    else:
        # if not using temporal test set, split randomly
        train, test = train_test_split(outcome_plus_features, test_size=0.20,
            random_state=model_options['random_seed'])

    # get subtables for each for easy reference
    train_X = train.drop([model_options['outcome_name'],
        model_options['cohort_grade_level_begin']],axis=1)
    test_X = test.drop([model_options['outcome_name'],
        model_options['cohort_grade_level_begin']],axis=1)
    train_y = train[model_options['outcome_name']]
    test_y = test[model_options['outcome_name']]

    # do missing value feature imputation here
    train_X, test_X = impute_missing_values(train_X, test_X,
        model_options['missing_impute_strategy'])
    assert (all(train_X.columns == test_X.columns)),\
        "train and test have different columns"

    # do feature scaling here
    train_X, test_X = scale_features(train_X, test_X,
        model_options['feature_scaling'])
    assert (all(train_X.columns == test_X.columns)),\
        "train and test have different columns"

    # From now on, we IGNORE the `test`, `test_X`, `test_y` data
    # until we evaluate the model

    ## (4B) Fit on Training ##
    # if we require cross-validation of parameters, we can either
    #    (a) hold out another cohort in each fold for cross-validation
    #    (b) fold all cohorts together for k-fold parameter estimation

    if model_options['parameter_cross_validation_scheme'] == 'none':
        # no need to further manipulate train dataset
        cohort_kfolds = 2 # hacky way to have GridSearchCV fit to 2 k-folds

    elif model_options['parameter_cross_validation_scheme'] == \
         'leave_cohort_out':
        # choose another validation set amongst the training set to
        # estimate parameters and model selection across cohort folds
        cohort_kfolds = LeaveOneLabelOut(train[
                model_options['cohort_grade_level_begin']])

    elif model_options['parameter_cross_validation_scheme'] == \
        'past_cohorts_only':
        cohort_kfolds_plus_future = LeaveOneLabelOut(train[
                model_options['cohort_grade_level_begin']])
        cohort_kfolds = []
        for train_list, test_list in cohort_kfolds:
            test_year = pd.unique(cohort_kfolds.labels[test_list])
            train_years_after_test = cohort_kfolds.labels[train_list] > test_year
            train_indices_after_test = np.where(train_years_after_test)
            train_list = np.delete(train_list, train_indices_after_test)
            fold = (train_list, test_list)
            if len(train_list) > 0:
                cohort_kfolds.append(fold)

    elif model_options['parameter_cross_validation_scheme'] == 'k_fold':
        # ignore cohorts and use random folds to estimate parameter
        cohort_kfolds = LabelKFold(train.index,
                n_folds = model_options['n_folds'])

    else:
        print('unknown cross-validation strategy. try "{}", "{}", or "{}"'\
              .format('leave_cohort_out', 'k_fold', 'none'))

    criterion = parse_criterion_string(
            model_options['validation_criterion'])
    # best_validated_models is a dictionary whose keys are the model
    # nicknames in model_classes_selected and values are objects
    # returned by GridSearchCV
    best_validated_models, validated_model_times = clf_loop(clfs, params, train_X, train_y,
        criterion = criterion,
        models_to_run = model_options['model_classes_selected'],
        cv_folds = cohort_kfolds) # cv_folds is a k-fold generator

    for model_name, model in best_validated_models.items():
        clf = model.best_estimator_
        if hasattr(clf, "predict_proba"):
            test_set_scores = clf.predict_proba(test_X)[:,1]
            train_set_scores = clf.predict_proba(train_X)[:,1]
        else:
            test_set_scores = clf.decision_function(test_X)
            train_set_scores = clf.decision_function(train_X)

        ## (4C) Save Results ##
        # Save the recorded inputs, model, performance, and text description
        # into a results folder
        # according to sklearn documentation, use joblib instead of pickle
        # save as a .pkl extension
        # store option inputs (random_seed, train/test split rules, features)
        # store time to completion [missing]

        count = next_id(model_options['user'])

        saved_outputs = {
            'model_name' : model_name,
            'file_name' : "{filename}_{model}_{user}_{number}"\
            .format(filename = model_options['file_save_name'], 
                    model = model_name, 
                    user = model_options['user'],
                    number = count),
            'estimator' : model,
            'model_options' : model_options, # this also contains cohort_grade_level_begin for train/test split
            'test_y' : test_y,
            'test_set_soft_preds' : test_set_scores,
            'test_set_preds' : model.predict(test_X),
            'train_y' : train_y,
            'train_set_soft_preds' : train_set_scores,
            'train_set_preds' : model.predict(train_X),
            'train_set_balance': {0:sum(train_y==0), 1:sum(train_y==1)},
            'features' : train_X.columns,
            'parameter_grid' : params[model_name],
            'performance_objects' : measure_performance(test_y, test_set_scores),
            'time': validated_model_times[model_name]
        }

        # save outputs
        file_name = model_options['file_save_name'] +'_' + model_name + '.pkl'
        pkl_dir = 'pkls'
        with open(os.path.join(save_location, pkl_dir, file_name), 'wb') as f:
            pickle.dump(saved_outputs, f)

        # write output summary to a database
        #    - (A) write to a database table to store summary
        #    - (B) write to and update an HTML/Markdown file
        #    to create visual tables and graphics for results

        if model_options['write_predictions_to_database']:
            write_scores_to_db(saved_outputs)
        write_model_report(save_location, saved_outputs)
        summary_to_db(saved_outputs)

def main(args=None):
# Create options file used to generate features
# OR Read in an existing human-created options file

# The model options needs to read in what tables to draw features from
# and what columns to draw from each of those tables
# Also needs to read in an option to output all results to a database

    
    parser = OptionParser()
    parser.add_option('-m','--modelpath', dest='model_options_file',
        help="filename for model options; default 'model_options.yaml' ")
    parser.add_option('-g','--gridpath', dest='grid_options_file',
        help="filename for grid options; default 'grid_options_bare.yaml' ")
    parser.add_option('-o', '--outputpath', dest='save_location',
        help="location for saving output reports; default 'Reports/' ")

    (options, args) = parser.parse_args(args)

    ### Parameters to entered from the options or use default####
    model_options_file = os.path.join(base_pathname, 'Models_Results',
            'model_options.yaml')
    grid_options_file = os.path.join(base_pathname, 'Models_Results',
            'grid_options_bare.yaml')
    save_location = os.path.join(base_pathname, 'Reports')
    if options.model_options_file:
        model_options_file = options.model_options_file
    if options.grid_options_file:
        grid_options_file = options.grid_options_file
    if options.save_location:
        save_location = options.save_location

    model_options = read_in_yaml(model_options_file)

    # set seed for this program from model_options
    np.random.seed(model_options['random_seed'])

    # get grid search options for all classifiers
    clfs, params = define_clfs_params(grid_options_file)

    # run the models and generate the markdown reports
    run_all_models(model_options, clfs, params, save_location)

if __name__ == '__main__':
    main()
