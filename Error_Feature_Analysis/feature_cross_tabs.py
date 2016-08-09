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

def main():
    optimization_criteria = ['val_precision_5', 'val_recall_5']
    loop_through_top_models(optimization_criteria)

def loop_through_top_models(optimization_criteria):
    with postgres_pgconnection_generator() as connection:
        with connection.cursor() as cursor:
            predictions = None
            top_models_query = """
        create temporary table top_models as
        select distinct on (model_name, label)
        * from
            (select model_name, filename, label, feature_categories,
            feature_grades, {criteria},
            rank() over (partition by (model_name, label)
                order by {ranker} desc) as val_rank
            from model.reports
            where debug=false
            order by model_name, label, val_rank) vr
        order by model_name, label, val_rank;
        """.format(criteria = ", ".join(optimization_criteria),
            ranker = optimization_criteria[0])
            cursor.execute(top_models_query)

            cursor.execute("""select filename, feature_categories,
                feature_grades from top_models;""")
            models_and_features = cursor.fetchall()

            for (table_name, feature_tables, feature_grade_range) \
                    in models_and_features:
                feature_table_list = feature_tables.split(", ")
                feature_grades = [int(i) for i in
                        feature_grade_range.split(", ")]
                feature_grade_regex = '({})'.format('|'.join(
                    [str(i) for i in feature_grades]))
                pattern = re.compile('(_gr_{rx}\Z)|(\D\Z)'.format(
                    rx=feature_grade_regex))

                for test_set in ['val', 'test']:
                    get_model_predictions = """select * from
                    (select student_lookup, true_label, predicted_label,
                    predicted_label = true_label as correct
                    from predictions."{table}" where split = '{test_set}') preds
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
                        predictions_and_features, index = 'student_lookup',
                        columns = colnames)
                    predictions = predictions.filter(regex=pattern)
                    predictions[['true_label', 'predicted_label']] = \
                    predictions[['true_label', 'predicted_label']].astype(bool)
                    predictions = make_df_categorical(predictions)

                    crosstabs = build_crosstabs(predictions)

                print('table:{}, features:{}, grades:{}'.format(
                    table_name, feature_tables, feature_grade_range))
                print(predictions.dtypes)

def build_crosstabs(prediction_data):
    # do something
    return crosstabs

def make_df_categorical(raw_data):
    string_features = raw_data.select_dtypes(include=[object, bool])
    numeric_features = raw_data.select_dtypes(include=[np.number])

    for string_col in string_features.columns:
        raw_data[string_col] = string_features[string_col].astype('category')
        if len(raw_data[string_col].cat.categories) < 2:
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
