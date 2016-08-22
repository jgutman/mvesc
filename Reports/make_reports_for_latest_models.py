import os, sys
import pickle
pathname = os.path.dirname(sys.argv[0])
full_pathname = os.path.abspath(pathname)
split_pathname = full_pathname.split(sep="mvesc")
base_pathname = os.path.join(split_pathname[0], "mvesc")

sys.path.insert(0, os.path.join(base_pathname, "ETL"))
sys.path.insert(0, os.path.join(base_pathname, "Models_Results"))

from mvesc_utility_functions import postgres_pgconnection_generator
from save_reports import write_model_report

def read_in_saved_outputs(filename, model_name,
        pkl_dir = '/mnt/data/mvesc/Models_Results/pkls'):
    full_filename = filename +'_' + model_name + '.pkl'
    with open(os.path.join(pkl_dir, full_filename), 'rb') as model:
        model_pkl = pickle.load(model)
    return model_pkl

def get_model_list(batch_date = '08_17_2016', outcome = 'definite_plus_ogt'):
    model_list = ["'RF'", "'logit'"]

    with postgres_pgconnection_generator() as connection:
        with connection.cursor() as cursor:
            temp_explore_results = """
            select filename from model.reports
                where filename in
                    (select distinct on (prediction_grade, model_name)
                    filename from model.reports
                    where filename like '{batch_date}%'
                    and cv_criterion like 'custom_recall%'
                    and model_name in ({model_list})
                    and label like '{outcome}'
                    order by prediction_grade, model_name, cv_score desc)
                and cv_criterion like 'custom_recall%'
                order by model_name, prediction_grade;
            """.format(batch_date=batch_date,
                    model_list = ', '.join(model_list), outcome = outcome)
            cursor.execute(temp_explore_results)
            models = [i[0] for i in cursor.fetchall()]
    return models

def main():
    models = get_model_list()
    model_names = [filename.split('_')[-3] for filename in models]
    save_location = os.path.join(base_pathname, "Reports")
    for filename, model_name in zip(models, model_names):
        saved_outputs = read_in_saved_outputs(filename, model_name)
        write_model_report(save_location, saved_outputs)

if __name__ == '__main__':
    main()
