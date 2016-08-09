import os, sys
pathname = os.path.dirname(sys.argv[0])
full_pathname = os.path.abspath(pathname)
split_pathname = full_pathname.split(sep="mvesc")
base_pathname = os.path.join(split_pathname[0], "mvesc")
sys.path.insert(0, os.path.join(base_pathname, 'ETL'))

from mvesc_utility_functions import *
import pandas as pd
import re

def main():
    with postgres_pgconnection_generator() as connection:
        with connection.cursor() as cursor:
            optimization_criteria = ['val_precision_5', 'val_recall_5']
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
                print('table:{}, features:{}, grades:{}'.format(
                    table_name, feature_tables, feature_grade_range))
                print(predictions.dtypes)

def make_df_categorical(raw_data):
    string_features = raw_data.select_dtypes(include=[object, bool])
    numeric_features = raw_data.select_dtypes(include=[np.number])


if __name__ == '__main__':
    main()
