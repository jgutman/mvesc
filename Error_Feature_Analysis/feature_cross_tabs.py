import os, sys
pathname = os.path.dirname(sys.argv[0])
full_pathname = os.path.abspath(pathname)
split_pathname = full_pathname.split(sep="mvesc")
base_pathname = os.path.join(split_pathname[0], "mvesc")
sys.path.insert(0, os.path.join(base_pathname, 'ETL'))

from mvesc_utility_functions import *
import pandas as pd
import numpy as np
import re
import pickle
from optparse import OptionParser

def main():
    parser = OptionParser()
    parser.add_option('-p','--path', dest='path',
        help="path to store pkl output")
    parser.add_option('-f','--file', dest='file',
        help="filename for pkl output")
    parser.add_option('-l','--load', dest='load_pkl',
        action='store_true', help="whether to load pkl instead of recompute")
    parser.add_option('-c','--criterion', dest='optimization_criteria',
        action='append', help="metric(s) to select top models")

    (options, args) = parser.parse_args()

    # set default args
    path = os.path.join(base_pathname, 'Error_Feature_Analysis', 'pkls')
    filename = 'crosstabs.pkl'
    load_pkl = False
    optimization_criteria = ['val_precision_5', 'val_recall_5']

    if options.path:
        path = options.path
    if options.file:
        filename = options.file
    if options.load_pkl:
        load_pkl = options.load_pkl
    if options.optimization_criteria:
        optimization_criteria = options.optimization_criteria

    # either load a stored pkl or compute it from scratch
    if load_pkl:
        # load pkl file
        pkl_file = open(os.path.join(path, filename),'rb')
        all_top_crosstabs = pickle.load(pkl_file)
    else:
        all_top_crosstabs = loop_through_top_models(optimization_criteria)
        with open(os.path.join(path, filename), 'wb') as f:
            pickle.dump(all_top_crosstabs, f)

    # models and features to display crosstabs for
    model_list = [model[0] for model in all_top_crosstabs.keys()]
    outcome_list = ['not_on_time']
    feature_list = ['gpa_gr_9','seventh_read_normalized','days_present_gr_9',
                    'mid_year_withdraw_gr_9', 'mid_year_withdraw_gr_8',
                    'gender', 'discipline_incidents_gr_9']
    for model in model_list:
        for outcome in outcome_list:
            for feature in feature_list:
                try:
                    print(model, outcome)
                    print(get_specific_cross_tabs(
                        all_top_crosstabs, model, outcome, feature))
                except KeyError:
                    # this model doesn't exist in this pkl
                    # or this feature doesn't exist in this model
                    continue

def get_specific_cross_tabs(crosstabs, model_name, label, feature,
    split = 'val'):
    """
    Given the dictionary of all possible crosstabs, and a filename for a
    single model, and a single feature, and whether to use the predictions on
    train/val/test set, returns a nicely formatted crosstab dataframe for that
    model/feature/set.

    :param dict(tuple: list(dataframe)) crosstabs: the full crosstabs dictionary
        as computed by loop_through_top_models function
    :param str model_name: a string containing the model type for the
        specific model run to pull crosstabs for
    :param str label: a string containing the outcome label to pull
    :param str feature: a string containing the feature e.g. 'days_present_gr_9'
    :param str split: whether to pull predictions on train, val, or test
    :returns dataframe containing actual vs predicted vs marginal proportions
        on positive/negative class by binned level of feature
    :rtype pd.dataframe
    """
    crosstab = crosstabs[(model_name, label, split)][feature]
    totals = crosstab.ix['true_label: All']
    predicted = 100*crosstab.ix[['predicted_label: True',
        'predicted_label: False']]/totals
    actual = 100*crosstab.ix[['true_label: True',
        'true_label: False']]/totals
    full = predicted.append(actual)
    full = full.append(totals*100)
    full = full.round(2)
    return full

def build_temp_table_best_models(cursor, optimization_criteria,
    table_name = 'top_models', feature_categories = 'all',
    prediction_grade = 10, timestamp_filter = '2016-08-09 06:00:00'):
    """
    For each model_name and label category, filtered on specified options
    grab the highest ranking model according to the optimization criteria.
    Return a list of tuples containing the filename, model_name, label,
    feature list, and grade range for the models you want to pull predictions

    :param pscyopg2.cursor cursor: a cursor to execute queries on the database
    :param str table_name: name for the temporary table to hold best models
    :param str feature_categories: specify what features are given to the models
        being compared, by default include only models trained on all features
    :param int prediction_grade: the prediction time point for all models
    :param str timestamp_filter: a timestamp format string to ignore all models
        run prior to the time specified here

    :returns a list of the top models to compare features for
        each model specified as (filename, model_name, label, features, grades)
    :rtype list(tuple)
    """
    if (feature_categories == 'all'):
        feature_categories = '%,%,%'
    top_models_query = """
    drop table if exists {table};
    create temporary table {table} as
    select distinct on (model_name, label) * from
        (select model_name, filename, label, feature_categories,
        feature_grades, {criteria},
        rank() over (partition by (model_name, label)
        order by {ranker} desc) as val_rank
        from model.reports
        where debug=false
        and feature_categories like {features}
        and cv_scheme = 'leave_cohort_out'
        and prediction_grade = {grade}
        and timestamp_filter > {timestamp}
        order by model_name, label, val_rank) vr
    order by model_name, label, val_rank;
    """.format(table = table_name, features = feature_categories,
        grade = prediction_grade, timestamp = timestamp_filter,
        criteria = ", ".join(optimization_criteria),
        ranker = optimization_criteria[0])

    cursor.execute(top_models_query)
    cursor.execute("""select filename, model_name, label,
        feature_categories, feature_grades from {table}
        """.format(table=table_name))
    models_and_features = cursor.fetchall()

    print('done grabbing models')
    return models_and_features

def loop_through_top_models(optimization_criteria,
    splits = ['train', 'val', 'test']):
    """
    Get a list of models to search over and then for each model, pull the
    predictions and feature values for every student in the specified splits
    for all features included in the feature categories and grade range of the
    model. Then bin those features into categorical variables and build rough
    crosstabs on each model-feature-split combination.

    :param list(str) optimization_criteria: a list of model selection criteria
        to compare models, with the first element used to pull the top model
    :param list(str) splits: a list of what sets should be included, i.e. some
        combination of 'train', 'test', 'val'
    :returns a dictionary of rough crosstabs, keyed by model
    """
    with postgres_pgconnection_generator() as connection:
        with connection.cursor() as cursor:
            models_and_features = build_temp_table_best_models(
                cursor, optimization_criteria)
            crosstabs_by_model_and_feature = dict()

            for (table_name, model_name, label, feature_tables,
                    feature_grade_range) in models_and_features:
                print('working on {}:{}'.format(model_name, label))
                feature_table_list = feature_tables.split(", ")
                feature_grades = [int(i) for i in
                        feature_grade_range.split(", ")]
                feature_grade_regex = '({})'.format('|'.join(
                    [str(i) for i in feature_grades]))
                pattern = re.compile('(_gr_{rx}\Z)|(\D\Z)'.format(
                    rx=feature_grade_regex))

                for test_set in splits:
                    get_model_predictions = """
                    select * from
                    (select student_lookup, true_label, predicted_label,
                    predicted_label = true_label as correct
                    from predictions."{table}"
                    where split = '{test_set}') preds
                    """.format(table = table_name, test_set = test_set)

                    for features in feature_table_list:
                        get_model_predictions += """ left join
                    (select * from model.{features}) {features}
                    using(student_lookup)
                    """.format(features = features)

                    cursor.execute(get_model_predictions)
                    predictions_and_features = cursor.fetchall()
                    colnames = [i[0] for i in cursor.description]

                    predictions = pd.DataFrame.from_records(
                        predictions_and_features,
                        index = 'student_lookup',
                        columns = colnames)
                    predictions = predictions.filter(regex=pattern)
                    predictions[['true_label', 'predicted_label']] = \
                    predictions[['true_label', 'predicted_label']].astype(bool)
                    predictions = make_df_categorical(predictions)

                    crosstabs = build_crosstabs(predictions)
                    key = (model_name, label, test_set)
                    crosstabs_by_model_and_feature[key] = crosstabs
    return crosstabs_by_model_and_feature

def build_crosstabs(prediction_data):
    # base_rates = {col: prediction_data[col].value_counts()
    #                    for col in prediction_data.columns}
    predicted = {col: pd.crosstab(index=prediction_data.predicted_label,
                    columns = prediction_data[col], margins=True,
                    normalize = True)
                for col in prediction_data.columns[3:]}
    actual = {col: pd.crosstab(index=prediction_data.true_label,
                    columns = prediction_data[col], margins=True,
                    normalize = True)
                 for col in prediction_data.columns[3:]}
    correct = {col: pd.crosstab(index=prediction_data.correct,
                    columns = prediction_data[col], margins=True,
                    normalize = True)
                 for col in prediction_data.columns[3:]}

    predicted_plus_actual = dict()
    for feature in predicted.keys():
        preds = predicted[feature]
        true = actual[feature]
        corr = correct[feature]
        preds.index = ['{name}: {value}'.format(name=preds.index.name,
                        value=value) for value in preds.index]
        true.index = ['{name}: {value}'.format(name=true.index.name,
                        value=value) for value in true.index]
        corr.index = ['{name}: {value}'.format(name=corr.index.name,
                        value=value) for value in corr.index]
        full = preds.append(true)
        full = full.append(corr)
        predicted_plus_actual[feature] = full
    return predicted_plus_actual

def make_df_categorical(raw_data):
    string_features = raw_data.select_dtypes(include=[object, bool])
    numeric_features = raw_data.select_dtypes(include=[np.number])

    for string_col in string_features.columns:
        raw_data[string_col] = string_features[string_col].astype('category')
        if (len(raw_data[string_col].cat.categories) < 2
            and string_col != 'predicted_label'
            and string_col != 'true_label'
            and string_col != 'correct'):
            raw_data.drop(string_col, axis=1, inplace=True)

    for numeric_col in numeric_features.columns:
        num_values = len(numeric_features[numeric_col].unique())
        num_bins = min(5, num_values)
        if (num_values < 2):
            raw_data.drop(numeric_col, axis=1, inplace=True)
        elif (num_values == 2 and
            numeric_features[numeric_col].isnull().sum() > 0):
            raw_data[numeric_col] = numeric_features[numeric_col] \
                .isnull().astype('category')
        else:
            raw_data[numeric_col] = pd.cut(numeric_features[numeric_col],
                bins = num_bins, precision = 1)

    return raw_data

if __name__ == '__main__':
    main()
