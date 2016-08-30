import os, sys
import pickle
from optparse import OptionParser
import re

pathname = os.path.dirname(sys.argv[0])
full_pathname = os.path.abspath(pathname)
split_pathname = full_pathname.split(sep="mvesc")
base_pathname = os.path.join(split_pathname[0], "mvesc")
parentdir = os.path.join(base_pathname, "ETL")
sys.path.insert(0, parentdir)

from estimate_prediction_model import *
from RF_feature_scores import scale_features_plus_scaler
from write_to_database import write_scores_to_db

def read_in_model(filename, model_name,
        pkl_dir = '/mnt/data/mvesc/Models_Results/pkls'):
    """
    Extract the model estimator and the model options dictionary from the
    pickled output file, stored in the pkl directory.

    params:
        str filename: the filename denoting the desired model to unpickle
        str model_name: the type of model for the desired model
    returns: the estimator corresponding to the filename and its model options
    rtype: sklearn estimator, dict
    """
    full_filename = filename +'_' + model_name + '.pkl'
    with open(os.path.join(pkl_dir, full_filename), 'rb') as model:
        model_pkl = pickle.load(model)
    clf, options = model_pkl['estimator'], model_pkl['model_options']
    options['estimator_features'] = model_pkl['estimator_features']
    return clf, options

def build_test_feature_set(options, current_year = 2016, return_raw = False):
    """
    Build and dummify a feature design matrix according to the features in the
    model options and the students at the prediction grade level in the current
    year, without removing extra features and reference categories.

    params:
        dict options: the model options dictionary for the desired model
        int current_year: the year to draw students cohort values from
    returns: the current students features without extra processing steps
    rtype: pd.DataFrame
    """
    # get student list of 2016 students in specified cohort grade level
    with postgres_pgconnection_generator() as connection:
        cohort = options['cohort_grade_level_begin']
        test_outcomes = read_table_to_df(connection,
            table_name = 'outcome', schema = 'model', nrows = -1,
            columns = ['student_lookup', 'current_students', cohort])
        test_outcomes.dropna(subset=['current_students', cohort], inplace=True)
        test_outcomes = pd.DataFrame(test_outcomes.student_lookup[
            test_outcomes[cohort] == current_year])

        for table, column_names in options['features_included'].items():
            features = read_table_to_df(connection, table_name = table,
                schema = 'model', nrows = -1,
                columns=(['student_lookup'] + column_names))
            # join to only keep features for current_students
            test_outcomes = pd.merge(test_outcomes, features,
                how = 'left', on = 'student_lookup')

    # build dataframe containing student_lookup
    # and all features as numeric non-categorical values
    test_outcomes.set_index('student_lookup', inplace=True)
    test_outcomes_processed = df2num(test_outcomes, drop_reference = False,
        dummify = True, drop_entirely_null = False)
    if return_raw:
        return test_outcomes_processed, test_outcomes
    return test_outcomes_processed

def test_impute_and_scale(test_outcomes, options):
    """
    Takes a design matrix for current students and the model options dictionary
    used to train a model and performs imputation, scaling, and dropping unused
    columns according to the imputation and scaling learned on the test set.

    params:
        pd.DataFrame test_outcomes: the current students design matrix coming
            out of build_test_feature_set
    returns:
        the test_outcomes dataframe, now ready for the model with imputation
        and feature scaling, and dummified features matching training data
    rtype: pd.DataFrame
    """
    all_past_data = build_outcomes_plus_features(options)
    train, val, _ = temporal_cohort_test_split(all_past_data,
            options['cohort_grade_level_begin'],
            options['cohorts_test'], options['cohorts_val'],
            options['cohorts_training'])
    column_set = options['estimator_features']
    train = train.filter(train.columns[2:])
    val = val.filter(val.columns[2:])

    category_missing = [col for col in train.columns if
                    col not in test_outcomes.columns]
    for col in category_missing:
        test_outcomes[col] = 0
    test_outcomes = test_outcomes.filter(train.columns)

    # imputation for missing values in features
    train, val, test_outcomes = impute_missing_values(train, val, test_outcomes,
        options['missing_impute_strategy'])

    # feature scaling
    train, val, test_outcomes, scaler = scale_features_plus_scaler(train, val, test_outcomes,
        options['feature_scaling'])

    train = train.filter(column_set)
    test_outcomes = test_outcomes.filter(column_set)

    assert (all(train.columns == test_outcomes.columns)),\
        "train and current_students have different columns"
    
    return test_outcomes, scaler

def make_and_save_predictions(future_predictions, clf, filename,
        current_year = 2016, write_to_db = True):
    """
    Takes a feature design matrix for current students with student lookup as
    index, and a classifier, and writes these soft/hard predictions on these
    students to the database.

    params:
        pd.DataFrame future_predictions: a dataframe with column features
            corresponding to the features in the model and index student_lookup
        sklearn estimator clf: some binary classifier
        str filename: the filename for clf to write to the database
        int current_year: current_year to include in predictions table_name
    returns: writes predictions for the model to the database
    rtype: None
    """
    # generate soft predictions
    if hasattr(clf, "predict_proba"):
        future_set_scores = clf.predict_proba(future_predictions)[:,1]
    else:
        future_set_scores = clf.decision_function(future_predictions)

    saved_outputs = {
        'file_name' : filename,
        'future_index' : future_predictions.index,
        'future_scores' : future_set_scores,
        'future_preds' : clf.predict(future_predictions)
    }
    if current_year:
        new_table = 'predictions_' + str(current_year)
    else:
        new_table = 'predictions'

    if write_to_db:
        write_scores_to_db(saved_outputs, table_name = new_table,
            importance_scores = False)
    return(saved_outputs)

def write_model_predictions_to_db(model_name, filename, current_year = 2016):
    """
    Takes as input a model_name and filename identifier for a pickled model
    and reads that model from disk to make hard and soft predictions for
    current students, and writes these predictions to the database

    params:
        str model_name: the kind of model, like 'RF' or 'logit'
        str filename: the filename for the model as stored in model.reports
        int current_year: current_year to pull predictions for students in
            desired cohort as of this year
    returns:
        writes predictions for the model to model.predictions where
            split = 'current' and true_label = NULL
    rtype: None
    """
    clf, options = read_in_model(filename, model_name)
    future_predictions = build_test_feature_set(options, current_year)
    future_predictions = test_impute_and_scale(future_predictions, options)
    make_and_save_predictions(future_predictions, clf, filename,
        current_year)

def main():
    parser = OptionParser()
    # take as argument a filename or list of filenames for models to generate
    # predictions on the students at prediction grade level in current
    # year with default = 2016
    parser.add_option('-f','--filename', dest='filename_list',
        help="filename for model to generate predictions",
        action="append")
    parser.add_option('-y', '--year', dest='current_year',
        help="current year to generate predictions for", type="int")
    (options, args) = parser.parse_args()

    filename_list = ['08_17_2016_grade_6_param_set_8_RF_jg_155',
        '08_17_2016_grade_7_param_set_17_RF_jg_138',
        '08_17_2016_grade_8_param_set_16_RF_jg_144',
        '08_17_2016_grade_9_param_set_16_RF_jg_179',
        '08_17_2016_grade_10_param_set_16_RF_jg_151',
        '08_17_2016_grade_6_param_set_8_logit_jg_97',
        '08_17_2016_grade_7_param_set_17_logit_jg_98',
        '08_17_2016_grade_8_param_set_16_logit_jg_111',
        '08_17_2016_grade_9_param_set_16_logit_jg_111',
        '08_17_2016_grade_10_param_set_22_logit_jg_122']
    current_year = 2016
    if options.filename_list:
        filename_list = options.filename_list
    if options.current_year:
        current_year = options.current_year

    # pull predictions for current students for every model and write to db
    for filename in filename_list:
        # filename ends in model_user_number
        model_name = filename.split('_')[-3]
        write_model_predictions_to_db(model_name, filename, current_year)
        print("predictions written for {}, {}, year {}".format(
            model_name, filename, current_year))

if __name__ == '__main__':
    main()
