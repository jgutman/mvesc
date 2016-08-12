import os, sys
pathname = os.path.dirname(sys.argv[0])
full_pathname = os.path.abspath(pathname)
split_pathname = full_pathname.split(sep="mvesc")
base_pathname = os.path.join(split_pathname[0], "mvesc")
sys.path.insert(0, os.path.join(base_pathname, 'ETL'))

from mvesc_utility_functions import *
import pandas as pd
import numpy as np
from optparse import OptionParser

def copy_model_predictions_over(cursor, models_to_copy):
    # copy predictions from predictions schema to model.predictions
    for model in models_to_copy:
        check_if_model_copied = """
        select distinct(filename) from model.predictions;"""
        cursor.execute(check_if_model_copied)
        existing_models = set(model[0] for model in cursor.fetchall())

        if model not in existing_models:
            pull_old_predictions = """
            select student_lookup, true_label, predicted_score, predicted_label,
            split, '{model}' as filename
            from predictions."{model}";""".format(model=model)

            insert_predictions_to_table = """
            insert into model.predictions
            (student_lookup, true_label, predicted_score, predicted_label,
            split, filename)
            {nested_query}""".format(nested_query=pull_old_predictions)

            print(insert_predictions_to_table)
            cursor.execute(insert_predictions_to_table)

def copy_model_feature_scores_over(cursor, models_to_copy):
    # copy feature scores from feature_scores schema to model.feature_scores
    for model in models_to_copy:
        check_if_model_copied = """
        select distinct(filename) from model.feature_scores;"""
        cursor.execute(check_if_model_copied)
        existing_models = set(model[0] for model in cursor.fetchall())

        if model not in existing_models:
            pull_old_feature_scores = """
            select index, feature, importance, '{model}' as filename
            from feature_scores."{model}";""".format(model=model)

            insert_feature_scores_to_table = """
            insert into model.feature_scores
            (index, feature, importance, filename)
            {nested_query}""".format(nested_query=pull_old_feature_scores)

            print(insert_feature_scores_to_table)
            cursor.execute(insert_feature_scores_to_table)

def main():
    parser = OptionParser()
    parser.add_option('-m','--model', dest='models_to_copy',
        action='append', help="model results to copy over to new table")
    (options, args) = parser.parse_args()

    models_to_copy = ['08_09_2016_grade_6_param_set_0_RF_ht_8585',
    '08_09_2016_grade_7_param_set_7_RF_ht_10497',
    '08_09_2016_grade_8_param_set_13_RF_ht_13254',
    '08_09_2016_grade_9_param_set_0_RF_ht_8645',    '08_09_2016_grade_10_param_set_0_RF_ht_8680']

    if options.models_to_copy:
        models_to_copy = options.models_to_copy

    with postgres_pgconnection_generator() as connection:
        with connection.cursor() as cursor:
            copy_model_predictions_over(cursor, models_to_copy)
            copy_model_feature_scores_over(cursor, models_to_copy)
        connection.commit()

if __name__ == '__main__':
    main()
