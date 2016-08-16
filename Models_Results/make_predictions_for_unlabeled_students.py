import os, sys
import pickle
from optparse import OptionParser

pathname = os.path.dirname(sys.argv[0])
full_pathname = os.path.abspath(pathname)
split_pathname = full_pathname.split(sep="mvesc")
base_pathname = os.path.join(split_pathname[0], "mvesc")
parentdir = os.path.join(base_pathname, "ETL")
sys.path.insert(0, parentdir)

from mvesc_utility_functions import *
from estimate_prediction_model import *

def read_in_model(filename, model_name,
        pkl_dir = '/mnt/data/mvesc/Models_Results/pkls'):
    full_filename = filename +'_' + model_name + '.pkl'
    with open(os.path.join(pkl_dir, full_filename), 'rb') as model:
        model_pkl = pickle.load(model)
    clf, options = model_pkl['estimator'], model_pkl['model_options']
    return clf, options

def build_test_feature_set(options, current_year = 2016):
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
    test_outcomes = df2num(test_outcomes, drop_reference = False,
        dummify = True, drop_entirely_null = False)
    return test_outcomes

def test_impute_and_scale(test_outcomes, options):
    all_past_data = build_outcomes_plus_features(options)
    train, val, None = temporal_cohort_test_split(all_past_data,
            options['cohort_grade_level_begin'],
            options['cohorts_test'], options['cohorts_val'],
            options['cohorts_training'])
    exclude = set((options['outcome_name'],
                options['cohort_grade_level_begin']))
    train = train.drop([options['outcome_name'],
            options['cohort_grade_level_begin']],axis=1)
    val = val.drop([options['outcome_name'],
            options['cohort_grade_level_begin']],axis=1)

    category_missing = [col for col in train.columns if
                    col not in test_outcomes.columns]
    for col in category_missing:
        test_outcomes[col] = 0
    test_outcomes = test_outcomes.filter(train.columns)

    # imputation for missing values in features
    train, val, test_outcomes = impute_missing_values(train, val, test_outcomes,
        options['missing_impute_strategy'])

    # feature scaling
    train, val, test_outcomes = scale_features(train, val, test_outcomes,
        options['feature_scaling'])

    assert (all(train.columns == test_outcomes.columns)),\
        "train and current_students have different columns"
    return test_outcomes

def make_and_save_predictions(future_predictions, clf, options):
    

def main():
    model_name = 'RF'
    filename = '08_12_2016_grade_8_param_set_11_RF_ht_18728'
    clf, options = read_in_model(filename, model_name)
    future_predictions = build_test_feature_set(options)
    future_predictions = test_impute_and_scale(future_predictions, options)

if __name__ == '__main__':
    main()
