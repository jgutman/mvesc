import os, sys
pathname = os.path.dirname(sys.argv[0])
full_pathname = os.path.abspath(pathname)
split_pathname = full_pathname.split(sep="mvesc")
base_pathname = os.path.join(split_pathname[0], "mvesc")
parentdir = os.path.join(base_pathname, "ETL")
sys.path.insert(0,parentdir)
from mvesc_utility_functions import * 

import numpy as np
from sklearn.metrics import precision_recall_curve
from sklearn.metrics import roc_curve
from sklearn.metrics import confusion_matrix
from sklearn.metrics import f1_score

columns = [
    'description',
    'features',
    'parameter_val',
    'train_set', 
    'test_set',
    'model_type',
    'train_f1',
    'test_f1'
    ]

def build_results_table(cursor):
    """
    builds the results table if it does not already exist

    :param pg_cursor cursor:
    """
    results_table_query = "create table if not exists model.reports ("
    for c in columns:
        results_table_query += "{} text, ".format(c)
    results_table_query = results_table_query[:-2] + ");"
    #print(results_table_query)
    cursor.execute(results_table_query)

def add_row(cursor, values):
    """
    adds a row to the results table consisting of the values given

    :param pg_cursor cursor:
    :param dict values: a dictionary with keys corresponding the the col names
    """
    add_row_query = "insert into model.reports ( "
    for c in columns:
        add_row_query += "{}, ".format(c)
    add_row_query = add_row_query[:-2] + " ) values ("
    add_row_query += """
    %(user_description)s,
    %(features)s,
    %(parameter_cross_validation_scheme)s,
    %(cohorts_train)s,
    %(cohorts_held_out)s,
    %(model_class_selected)s,
    %(train_f1)s,
    %(test_f1)s,
    );"""
#    print(add_row_query)
#    print(values)
    cursor.execute(add_row_query, values)
        
def main():
    test_y = np.array([1,0])
    train_y = np.array([1,0])
    test_prob_preds = np.array([1,0])
    train_prob_preds = np.array([1,0])
    model_options = {'model_class_selected' : 'logit',                                        
                     'model_performance_estimate_scheme' : 'temporal_cohort',                         
                     'parameter_cross_validation_scheme' : 'none',                                    
                     'n_folds' : 10,                                                                  
                     'file_save_name' : 'gender_ethnicity_logit.pkl',                                 
                     'randomSeed' : 2187,                                                             
                     'user_description' : """initial skeleton pipeline test""",                       
                     'cohort_chosen' : 'cohort_9th',                                                  
                     'cohorts_held_out' : [2015] ,
                     'features' : 'demographics',
                     'cohorts_train' : [2012,2013,2014]
                 }
    db_saved_outputs = {
        'train_f1': f1_score(test_y,test_prob_preds),
        'test_f1': f1_score(train_y,train_prob_preds)
    }
    db_saved_outputs.update(model_options)

    with postgres_pgconnection_generator() as connection:
        with connection.cursor() as cursor:
            build_results_table(cursor)
            print('table built')
            add_row(cursor,db_saved_outputs)
            print('row added')
        connection.commit()

if __name__ == "__main__":
    main()
