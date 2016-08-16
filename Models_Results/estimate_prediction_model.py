import os, sys
pathname = os.path.dirname(sys.argv[0])
full_pathname = os.path.abspath(pathname)
split_pathname = full_pathname.split(sep="mvesc")
base_pathname = os.path.join(split_pathname[0], "mvesc")
parentdir = os.path.join(base_pathname, "ETL")
sys.path.insert(0, parentdir)
from mvesc_utility_functions import *
from optparse import OptionParser
import pdb

# all model import statements
from sklearn import svm # use svm.SVC kernel = 'linear' or 'rbf'
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, GradientBoostingClassifier, AdaBoostClassifier
from sklearn.linear_model import LogisticRegression, Perceptron, SGDClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB, MultinomialNB, BernoulliNB

from sklearn.grid_search import GridSearchCV, ParameterGrid
from sklearn.cross_validation import *
from sklearn.externals import joblib
from sklearn.metrics import precision_recall_curve, roc_curve, confusion_matrix
from sklearn.preprocessing import Imputer, StandardScaler, RobustScaler
from sklearn.utils import shuffle, resample

import yaml
import numpy as np
import pandas as pd
import pickle
import random

from my_timer import Timer
from custom_scorers import *
from save_reports import write_model_report
from write_to_database import summary_to_db, write_scores_to_db, next_id

######
# Setup Modeling Options and Functions

def define_clfs_params(filename):
    """
    Defines the range of possible classifiers and parameters to search.
    model_options[model_classes_selected] determines which of these models
    are actually run

    :param str filename: name of a yaml file containing parameter values
    for each model
    :returns: a dictionary of models and a dictionary of parameter values
    :rtype: pair of dicts
    """

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

def build_outcomes_plus_features(model_options, subset_n=None):
    """
    Returns a pandas dataframe containing the student_lookup, cohort
    identifier, outcome variable, and all numerical or binarized features.
    Reads in the features and outcomes from database according to the
    specification given in model_options dictionary.

    Assumes:
    model.outcome table contains a column (name in cohort_grade_level_begin)
    with int values identifying each student's cohort year
    e.g. 'cohort_9th' contains the year each student is seen in 9th grade
    and contains an outcome column (name given in outcome_name)
    and all feature and outcomes tables contain student_lookup

    Usage:
    select train, validation, and test based on values in column
    'cohort_grade_level_begin' according to value in 'cohorts_val'

    :param dict model_options: all options read in from yaml file
    :param int subset_n: number of students to subsample (only for debugging)
    """
    with postgres_pgconnection_generator() as connection:
        outcome_name = model_options['outcome_name']
        outcomes_with_student_lookup = read_table_to_df(connection,
            table_name = 'outcome', schema = 'model', nrows = -1,
            columns = ['student_lookup', outcome_name,
            model_options['cohort_grade_level_begin']])

        # drop students without student_lookup, outcome, or cohort identifier
        # can use subset=[colnames] to drop based on certain columns only
        outcomes_with_student_lookup.dropna(inplace=True)

        # sub-sampling for test purposes
        # half postive examples, half negative
        if subset_n:
            outcomes_with_student_lookup = outcomes_with_student_lookup \
            .groupby(outcome_name).apply(lambda x:
                                         x.sample(n=int(np.floor(subset_n/2))))
            outcomes_with_student_lookup.index = \
            outcomes_with_student_lookup.index.droplevel()

        joint_label_features = outcomes_with_student_lookup.copy()

        # get all requested input features
        # assumes every features table contains 'student_lookup'
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

def temporal_cohort_test_split(joint_df, cohort_grade_level_begin,
                               cohorts_test, cohorts_val, cohorts_training):
    """
    Splits the given joint_df of features & outcomes and
    returns a train/test dataset
    :param pd.DataFrame joint_df: data frame withcohort, outcome, and features
    :param list[int] cohorts_val: a list of years to split val set on
    :param list[int] cohorts_test: a list of years to split test set on
    :param string or list[int] cohorts_training: either the string 'all' or
        a list of years to include in the training, all years must precede
        the test set years in cohorts_val
    :returns: two dataframes consisting of rows from joint_df, one for training
        and one to be used for testing
    :rtype: pd.DataFrame, pd.DataFrame
    """
    if (cohorts_training=='all'):
        train = joint_df[~joint_df[cohort_grade_level_begin]\
                         .isin(cohorts_val + cohorts_test)]
        assert (np.max(train[cohort_grade_level_begin])
                < min(cohorts_val+cohorts_test)), \
            "Training years do not completely precede test years"
    else:
        assert (max(cohorts_training) < min(cohorts_val+cohorts_test)), \
            "Training years do not completely precede test years"
        train = joint_df[joint_df[cohort_grade_level_begin].\
                         isin(cohorts_training)]
    val = joint_df[joint_df[cohort_grade_level_begin].isin(cohorts_val)]
    test = joint_df[joint_df[cohort_grade_level_begin].isin(cohorts_test)]
    return train, val, test


def parse_features(features_included_raw, feature_grade_range):
    """
    Expands feature names including * to given grade range

    :param dict features_included_raw: dictionary of tables and columns
    read in from model_options
    :param list feature_grade_range: list of grades to include
    """
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
    :rtype: dict
    """
    with open(filename, 'r') as f:
        model_options = yaml.load(f)

    assert(type(model_options) == dict), "bad formatting in yaml file"
    required_keys = set(('batch_name','model_classes_selected',
                         'user_description', 'file_save_name',
                         'write_predictions_to_database', 'user', 'debug',
                         'model_test_holdout',
                         'parameter_cross_validation_scheme',
                         'cohort_grade_level_begin',
                         'prediction_grade_level', 'feature_grade_range',
                         'cohorts_training', 'cohorts_val', 'cohorts_test',
                         'random_seed', 'validation_criterion',
                         'features_included', 'outcome_name',
                         'missing_impute_strategy', 'feature_scaling'))
    assert (all([key in model_options.keys() for key in required_keys])), \
        "missing model specifications in yaml file"
    assert(type(model_options['features_included']) == dict), \
        "bad formatting in yaml file"
    assert(type(model_options['model_classes_selected']) == list),\
        "bad formatting in yaml file"
    assert(type(model_options['cohorts_val']) == list),\
        "bad formatting in yaml file"
    assert(type(model_options['cohorts_training']) == list or
        model_options['cohorts_training'] == 'all'),\
        "bad formatting in yaml file"
    return model_options

def scale_features(train, val, test, strategy):
    """
    Scales features based on the training values with the given strategy

    :param pd.DataFrame train:
    :param pd.DataFrame val:
    :param pd.DataFrame test:
    :param str strategy:
    :returns: scaled training, val, and test sets
    :rtype: pd.DataFrame, pd.DataFrame, pd.DataFrame
    """
    num_values_by_column = {x: len(train[x].unique()) for x in train.columns}
    zero_variance_columns = [k for k,v in num_values_by_column.items()
                             if v == 1]
    train.drop(zero_variance_columns, axis=1, inplace=True)
    val.drop(zero_variance_columns, axis=1, inplace=True)
    test.drop(zero_variance_columns, axis=1, inplace=True)

    if (strategy == 'none'):
        return train, val, test

    elif(strategy == 'standard' or strategy == 'robust'):
        non_binary_columns = [k for k, v in num_values_by_column.items()
                              if v > 2]
        if (len(non_binary_columns) > 0):
            scaler = StandardScaler() if strategy == 'standard' \
                     else RobustScaler()
            train_non_binary = train[non_binary_columns]
            val_non_binary = val[non_binary_columns]
            test_non_binary = test[non_binary_columns]
            scaler.fit(train_non_binary)
            train_non_binary = pd.DataFrame(scaler.transform(train_non_binary),
                columns = non_binary_columns, index = train.index)
            val_non_binary = pd.DataFrame(scaler.transform(val_non_binary),
                columns = non_binary_columns, index = val.index)
            test_non_binary = pd.DataFrame(scaler.transform(test_non_binary),
                columns = non_binary_columns, index = test.index)
            train_scaled = train.drop(non_binary_columns, axis=1)
            val_scaled = val.drop(non_binary_columns, axis=1)
            test_scaled = test.drop(non_binary_columns, axis=1)
            train_scaled = train_scaled.merge(train_non_binary,
                left_index=True, right_index=True)
            val_scaled = val_scaled.merge(val_non_binary,
                left_index=True, right_index=True)
            test_scaled = test_scaled.merge(test_non_binary,
                left_index=True, right_index=True)
            return train_scaled,val_scaled, test_scaled
        else:
            return train,val, test

    else:
        print('unknown feature scaling strategy. try "{}", "{}", or "{}"'\
              .format('standard', 'robust', 'none'))
        return train, val, test

def add_null_dummies_train_test(train, val, test):
    """
    Adds a dummy column for each feature that has null values

    :param pd.DataFrame train:
    :param pd.DataFrame val:
    :param pd.DataFrame test:
    :returns: training, val, and test sets
    :rtype: pd.DataFrame, pd.DataFrame, pd.DataFrame
    """
    train_null_columns = train.columns[train.isnull().sum() > 0]
    val_null_columns = val.columns[val.isnull().sum() > 0]
    test_null_columns = test.columns[test.isnull().sum() > 0]
    null_column_set = set(train_null_columns).union(set(test_null_columns))\
                      .union(set(val_null_columns))
    null_columns = pd.indexes.base.Index(null_column_set)

    train_nullified = add_null_dummies(train, null_columns)
    val_nullified = add_null_dummies(val, null_columns)
    test_nullified = add_null_dummies(test, null_columns)
    return train_nullified, val_nullified, test_nullified

def add_null_dummies(data, null_columns):
    """
    Adds a dummy column for each null values in each of the given columns.
    Used by add_null_dummies_train_test

    :param pd.DataFrame data:
    :param list null_columns:
    :returns: data with dummy columns
    :rtype: pd.DataFrame
    """
    data_null_columns = data[null_columns]
    data_null_dummies = data_null_columns.isnull()*1.0
    data_null_dummies.rename(columns=lambda x: x + '_isnull', inplace=True)
    data_plus_dummies = data.merge(data_null_dummies,
        left_index=True, right_index=True)
    return data_plus_dummies

def impute_missing_values(train,val, test, strategy):
    """
    Imputes missing values based on the training set values

    :param pd.DataFrame train:
    :param pd.DataFrame val:
    :param pd.DataFrame test:
    :param str strategy:
    :returns: training, val, and test sets
    :rtype: pd.DataFrame, pd.DataFrame, pd.DataFrame
    """
    if (strategy=='none'):
        return train, val, test

    elif(strategy == 'mean_plus_dummies' or strategy == 'median_plus_dummies'):
        # add feature_isnull columns 0 or 1
        train, val, test = add_null_dummies_train_test(train, val, test)
        train_null_cols = train.columns[train.isnull().all(axis=0)]
        train.drop(train_null_cols, axis=1, inplace=True)
        val.drop(train_null_cols, axis=1, inplace=True)
        test.drop(train_null_cols, axis=1, inplace=True)
        imputer = Imputer(strategy=strategy.split("_")[0])
        imputer.fit(train) # fit the imputer on the training mean/median
        train = pd.DataFrame(imputer.transform(train), # returns a numpy array
            columns = train.columns, index = train.index) # back to dataframe
        val = pd.DataFrame(imputer.transform(val),
            columns = val.columns, index = val.index)
        test = pd.DataFrame(imputer.transform(test),
            columns = test.columns, index = test.index)
        return train, val, test

    else:
        print('unknown imputation strategy. try "{}", "{}", or "{}"'.format(
            'mean_plus_dummies', 'median_plus_dummies', 'none'))
        return train, val, test

def clf_loop(clfs, params, train_X, train_y, val_X, val_y, test_X, test_y,
        criterion_list, models_to_run, cv_folds, save_location, options):
    """
    Returns a dictionary where the keys are model nicknames (strings)
    and the values are classifiers with methods predict and fit and
    either predict_proba or decision_function

    :param dict(str:estimator) clfs: clfs as returned by define_clfs_params
    :param dict(str:dict) params: grid of classifier hyperparameter options
        to grid search over as returned by define_clfs_params
    :param pandas.DataFrame train_X: index is student_lookup, columns are all
        features to train over in the model
    :param pandas.Series(int) train_y: index is student_lookup, value is 0 or 1
        for outcome label
    :param pandas.DataFrame val_X: index is student_lookup, columns are all
        features to train over in the model
    :param pandas.Series(int) val_y: index is student_lookup, value is 0 or 1
        for outcome label
    :param pandas.DataFrame test_X: index is student_lookup, columns are all
        features to train over in the model
    :param pandas.Series(int) test_y: index is student_lookup, value is 0 or 1
        for outcome label
    :param string criterion: evaluation criterion for model selection on the
        validation set, to be read in from model_options (e.g. 'f1')
    :param list[string] models_to_run: which models to actually run as read in
        from model_options (e.g. ['logit', 'DT'])
    :param sklearn.KFolds cv_folds: a KFolds generator object over the index
        given in train_X and train_y (a list of lists of student_lookups)
    :returns: length of time to run full loop
    :rtype: float
    """

    downsample_param = 0.
    upsample_param = 0.
    sample_wt_ratio = 0.
    if 'downsample_param' in options:
        downsample_param = options['downsample_param']
    elif 'upsample_param' in options:
        upsample_param = options['upsample_param']
    elif 'sample_wt_ratio' in options:
        sample_wt_ratio = options['sample_wt_ratio']

    tuple_score = build_tuple_scorer(criterion_list)
    n_criteria = len(criterion_list)
    with Timer('clf_loop') as qq:
        for index,clf in enumerate([clfs[x] for x in models_to_run]):
            model_name=models_to_run[index]
            parameter_values = params[model_name]
            for p in ParameterGrid(parameter_values):
                with Timer(model_name) as t:
                    clf.set_params(**p)
                    cv_scores_avg = np.empty((len(cv_folds), n_criteria))
                    for i, (train_list, val_list) in enumerate(cv_folds):
                        if downsample_param:
                            train_X_downsampled, train_y_downsampled = \
                                downsample(downsample_param,
                                X = train_X.iloc[train_list],
                                y = train_y.iloc[train_list])
                            clf.fit(train_X_downsampled,
                                train_y_downsampled)
                        elif upsample_param:
                            train_X_upsampled, train_y_upsampled = \
                                upsample(upsample_param,
                                X = train_X.iloc[train_list],
                                y = train_y.iloc[train_list])
                            clf.fit(train_X_upsampled,
                                train_y_upsampled)
                        elif sample_wt_ratio:
                            wts_array = get_sample_weights(sample_wt_ratio,
                                y = train_y.iloc[train_list])
                            clf.fit(train_X.iloc[train_list],
                                train_y.iloc[train_list],
                                sample_weight = wts_array)
                        else:
                            clf.fit(train_X.iloc[train_list],
                                train_y.iloc[train_list])
                        cv_score = tuple_score(clf,
                            train_X.iloc[val_list], train_y.iloc[val_list])
                        cv_scores_avg[i] = list(cv_score)
                    cv_scores_avg = np.mean(cv_scores_avg, axis=0)

                    if downsample_param:
                        train_X_downsampled, train_y_downsampled = \
                            downsample(downsample_param,
                            X = train_X, y = train_y)
                        clf.fit(train_X_downsampled,
                            train_y_downsampled)
                    elif upsample_param:
                        train_X_upsampled, train_y_upsampled = \
                            upsample(upsample_param,
                            X = train_X, y = train_y)
                        clf.fit(train_X_upsampled,
                            train_y_upsampled)
                    elif sample_wt_ratio:
                        wts_array = get_sample_weights(sample_wt_ratio,
                            y = train_y)
                        clf.fit(train_X, train_y, sample_weight = wts_array)
                    else:
                        clf.fit(train_X, train_y)
                    run_time = t.time_check()
                write_out_predictions(options, model_name, clf, run_time,
                    cv_scores_avg, parameter_values, save_location,
                    train_X, train_y,val_X, val_y, test_X, test_y)
    return qq.time_check()

def get_sample_weights(sample_wt_ratio, y):
    # currently this option is implemented in LogisticRegression only with
    # the solvers {‘newton-cg’, ‘lbfgs’, ‘sag’} not the default 'liblinear'
    # none of these solvers support L1 penalty
    ratio = np.array([sample_wt_ratio, 1-sample_wt_ratio])
    y = y.astype(int)
    wts = ratio/np.bincount(y)
    wts_array = wts[y]
    return wts_array

def upsample(upsample_param, X, y):
    n_negative = len(y)-float(sum(y))
    pct_negative = n_negative/len(y)
    if (pct_negative < upsample_param):
        return X, y
    n_resampled_positive = round(n_negative/upsample_param - n_negative)
    negatives_ix = np.where(y==0)[0]
    # sklearn.utils.resample doesn't work here because n_samples > n_max_samples
    positives_ix = np.random.choice(np.where(y)[0], replace=True,
        size = n_resampled_positive)
    shuffled_ix = shuffle(np.append(positives_ix,negatives_ix))
    return X.iloc[shuffled_ix], y.iloc[shuffled_ix]

def downsample(downsample_param, X, y):
    n_positive = float(sum(y))
    pct_positive = n_positive/len(y)
    if (pct_positive > 1. - downsample_param):
        return X, y
    ratio = downsample_param / (1. - downsample_param)
    n_resampled_negative = round(ratio * n_positive)
    negatives_ix = resample(np.where(y==0)[0], replace=False,
        n_samples = n_resampled_negative)
    positives_ix = np.where(y)[0]
    shuffled_ix = shuffle(np.append(positives_ix,negatives_ix))
    return X.iloc[shuffled_ix], y.iloc[shuffled_ix]

def write_out_predictions(model_options, model_name, clf, run_time,
        average_cv_scores, params, save_location,
        train_X, train_y, val_X, val_y, test_X, test_y):
    """
    Saves the output of a model in 3 ways:
    (1) saves a pkl file to mtn/data
    (2) saves a markdown report (from save_reports.py)
    (3) writes information to the database (from write_to_database.py)

    :param dict model_options:
    :param str model_name: model nickname
    :param estimator clf: sklearn estimator object
    :param float run_time: time for the model run
    :param np.array average_cv_scores: score for each cv_criterion
    :param str save_location: path to save reports to
    :param pd.DataFrame train_X:
    :param pd.DataFrame val_X:
    :param pd.DataFrame test_X:
    :param pd.Series train_y:
    :param pd.Series val_y:
    :param pd.Series test_y:
    """

    # generate predictions
    if hasattr(clf, "predict_proba"):
        test_set_scores = clf.predict_proba(test_X)[:,1]
        val_set_scores = clf.predict_proba(val_X)[:,1]
        train_set_scores = clf.predict_proba(train_X)[:,1]
    else:
        test_set_scores = clf.decision_function(test_X)
        val_set_scores = clf.decision_function(val_X)
        train_set_scores = clf.decision_function(train_X)

    assert (test_set_scores.size==test_y.size),\
        "dimensions of test predictions don't match"

    assert (val_set_scores.size==val_y.size),\
        "dimensions of val predictions don't match"

    assert (train_set_scores.size==train_y.size),\
        "dimensions of train predictions don't match"

    # increment counter
    count = next_id(model_options['user'])

    # gather data to save
    saved_outputs = {
        'model_name' : model_name,
        'file_name' : "{filename}_{model}_{user}_{number}"\
            .format(filename = model_options['file_save_name'],
                    model = model_name,
                    user = model_options['user'],
                    number = count),
        'estimator' : clf,
        'estimator_features' : list(train_X.columns)
        'model_options' : model_options,
        'cross_validation_scores': average_cv_scores,
        'test_y' : test_y,
        'test_set_soft_preds' : test_set_scores,
        'test_set_preds' : clf.predict(test_X),
        'val_y' : val_y,
        'val_set_soft_preds' : val_set_scores,
        'val_set_preds' : clf.predict(val_X),
        'train_y' : train_y,
        'train_set_soft_preds' : train_set_scores,
        'train_set_preds' : clf.predict(train_X),
        'train_set_balance': {0:sum(train_y==0), 1:sum(train_y==1)},
        'features' : train_X.columns,
        'parameter_grid' : params,
        'time': run_time
        }

    # save python object as a pkl file on mnt drive
    file_name = saved_outputs['file_name'] +'_' + model_name + '.pkl'
    pkl_dir = 'pkls'
    with open(os.path.join('/mnt/data/mvesc/Models_Results',
                           pkl_dir, file_name), 'wb') as f:
        pickle.dump(saved_outputs, f)

    # write features and predictions to database
    if model_options['write_predictions_to_database']:
        write_scores_to_db(saved_outputs)

    # generate markdown report and images
#    write_model_report(save_location, saved_outputs)

    # write summary row to model.reports
    summary_to_db(saved_outputs)


def run_all_models(model_options, clfs, params, save_location):
    """
    Runs all the models based on the given options

    :param dict model_options:
    :param dict clfs:
    :param dict params:
    :param str save_location:
    """
    # get DataFrame with outcome and features specified in model_options
    subset_n = model_options['subset_n']
    outcome_plus_features=build_outcomes_plus_features(model_options,subset_n)

    # drop these students with null values in cohort or outcome
    outcome_plus_features.dropna(subset=[model_options['outcome_name'],
        model_options['cohort_grade_level_begin']], inplace=True)

    # select test set
    if model_options['model_test_holdout'] == 'temporal_cohort':
        # if using temporal cohort model performance validation,
        # we choose the cohorts in cohorts_val for the val set
        # and cohorts in cohorts_test for the test set
        train, val, test = temporal_cohort_test_split(outcome_plus_features,
            model_options['cohort_grade_level_begin'],
            model_options['cohorts_test'],
            model_options['cohorts_val'],
            model_options['cohorts_training'])
#    else:
        # if not using temporal test set, split randomly
        # this function doesn't actually exist?
        # train, test = train_test_split(outcome_plus_features,val_size = 0.1,
        #                                test_size=0.10,
        #                                random_state= \
        #                                model_options['random_seed'])

    # get subtables for each for easy reference
    train_X = train.drop([model_options['outcome_name'],
                          model_options['cohort_grade_level_begin']],axis=1)
    test_X = test.drop([model_options['outcome_name'],
                        model_options['cohort_grade_level_begin']],axis=1)
    val_X = val.drop([model_options['outcome_name'],
                      model_options['cohort_grade_level_begin']],axis=1)
    train_y = train[model_options['outcome_name']]
    test_y = test[model_options['outcome_name']]
    val_y = val[model_options['outcome_name']]

    # imputation for missing values in features
    train_X, val_X, test_X = impute_missing_values(train_X, val_X, test_X,
        model_options['missing_impute_strategy'])
    assert (all(train_X.columns == test_X.columns)),\
        "train and test have different columns"

    # feature scaling
    train_X, val_X, test_X = scale_features(train_X, val_X, test_X,
        model_options['feature_scaling'])
    assert (all(train_X.columns == test_X.columns)),\
        "train and test have different columns"

    # IGNORE the `test_X`, `test_y` data until evaluating the model

    # parameter cross-validation
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
        for train_list, test_list in cohort_kfolds_plus_future:
            test_year = pd.unique(cohort_kfolds_plus_future.labels[test_list])
            train_years_after_test = cohort_kfolds_plus_future.labels[train_list] > \
                                     test_year
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

    # run all the models in a loop
    output = clf_loop(clfs, params, train_X, train_y, val_X, val_y,
                      test_X, test_y,
                      criterion_list = model_options['validation_criterion'],
                      models_to_run = model_options['model_classes_selected'],
                      cv_folds = cohort_kfolds, #cv_folds is a k-fold generator
                      save_location = save_location, options = model_options)

def main(args=None):
    """
    Takes command line arguments for the model_options file (-m),
    grid_options (-g), and the output path (-o),
    and provides defaults for each of these values
    """

    parser = OptionParser()
    parser.add_option('-m','--modelpath', dest='model_options_file',
        help="filename for model options; default 'model_options.yaml' ")
    parser.add_option('-g','--gridpath', dest='grid_options_file',
        help="filename for grid options; default 'grid_options_bare.yaml' ")
    parser.add_option('-o', '--outputpath', dest='save_location',
        help="location for saving output reports; default 'Reports/' ")

    (options, args) = parser.parse_args(args)

    # default values
    model_options_file = os.path.join(base_pathname, 'Models_Results',
                                      'model_options','model_options.yaml')
    grid_options_file = os.path.join(base_pathname, 'Models_Results',
                                     'grid_options', 'grid_options_bare.yaml')
    save_location = os.path.join(base_pathname, 'Reports')

    # replacing with entered values
    if options.model_options_file:
        model_options_file = options.model_options_file
    if options.grid_options_file:
        grid_options_file = options.grid_options_file
    if options.save_location:
        save_location = options.save_location

    # reading in model_options
    model_options = read_in_yaml(model_options_file)

    # set seed for this program from model_options
    random.seed(model_options['random_seed'])

    # get grid search options for all classifiers
    clfs, params = define_clfs_params(grid_options_file)

    # run the models, generate markdown reports, and save results to database
    run_all_models(model_options, clfs, params, save_location)

if __name__ == '__main__':
    main()
