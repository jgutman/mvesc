import os, sys
pathname = os.path.dirname(sys.argv[0])
full_pathname = os.path.abspath(pathname)
split_pathname = full_pathname.split(sep="mvesc")
base_pathname = os.path.join(split_pathname[0], "mvesc")
sys.path.insert(0, os.path.join(base_pathname, 'ETL'))

from mvesc_utility_functions import *

def main():
    with postgres_pgconnection_generator() as connection:
        with connection.cursor() as cursor:
            optimization_criteria = ['val_precision_5', 'val_recall_5']
            top_models_query = """
        create temporary table top_models as
        select distinct on (model_name, label)
        * from
            (select model_name, filename, label, feature_categories,
            feature_grades, {criteria},
            rank() over (partition by model_name, label)
                order by {ranker} desc) as val_rank
            from model.reports
            where debug=false
            order by model_name, label, val_rank) vr
        order by model_name, label, val_rank;
        """.format(criteria = ", ".join(optimization_criteria),
            ranker = optimization_criteria[0])
            cursor.execute(top_models_query)

            cursor.execute("""select filename, feature_categories
            from top_models;""")
            models_and_features = cursor.fetchall()

            for table_name, feature_table_list in models_and_features:
                print('table: {} type: {}'.format(table_name,
                    type(table_name)))
                print('features: {} type: {}'.format(feature_table_list,
                    type(feature_table_list)))

if __name__ == '__main__':
    main()
