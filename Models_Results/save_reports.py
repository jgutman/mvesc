import os, sys
pathname = os.path.dirname(sys.argv[0])
full_pathname = os.path.abspath(pathname)
split_pathname = full_pathname.split(sep="mvesc")
base_pathname = os.path.join(split_pathname[0], "mvesc")
parentdir = os.path.join(base_pathname, "ETL")
sys.path.insert(0,parentdir)
from mvesc_utility_functions import * 

import numpy as np
from sklearn.metrics import precision_recall_curve, roc_curve, f1_score, \
    confusion_matrix, average_precision

# def build_results_table(cursor):
#     """
#     builds the results table if it does not already exist

#     :param pg_cursor cursor:
#     """
#     results_table_query = "create table if not exists model.reports ("
#     for c in columns:
#         results_table_query += "{} text, ".format(c)
#     results_table_query = results_table_query[:-2] + ");"
#     #print(results_table_query)
#     cursor.execute(results_table_query)

# def add_row(cursor, values):
#     """
#     adds a row to the results table consisting of the values given

#     :param pg_cursor cursor:
#     :param dict values: a dictionary with keys corresponding the the col names
#     """
#     add_row_query = "insert into model.reports ( "
#     for c in columns:
#         add_row_query += "{}, ".format(c)
#     add_row_query = add_row_query[:-2] + " ) values ("
#         for c in columns:
#         add_row_query += "{}, ".format(c)
#     add_row_query += ");"
# #    print(add_row_query)
# #    print(values)
#     cursor.execute(add_row_query, values)


def score_distribution(soft_predictions, model_name, base_file_name):
    plt.hist(soft_predictions, 
             np.linspace(min(min(soft_predictions), 0),
                         max(max(soft_predictions), 1), 
                         100), align = 'left')
    model_name = base_file_name.split('_')[-1]
    plt.title("distribution of scores for {} model".format(model_name))
    plt.xlabel("
    plt.savefig(base_file_name+'_score_dist.png', bbox_inches='tight')
    

def markdown_report(f, model_options,model_name):
    base_path = '/mnt/data/mvesc/Reports/'
    base_file_name = (base_path + model_options['file_save_name'] +'_' 
                      + model_name)
    # header
    f.write("# Report for {title}".format(" ".join(file_name.split('_'))))
    f.write(model_options['user_description'])
    f.write("Label used: {}".format(model_options['outcome_name']))
    
    # model options used
    f.write("### Model Options")
    f.write("* initial cohort grade: {}"\
            .format(model_options['cohort_grade_level_begin'][-3:-2))))
    f.write("* test cohorts: {}"\
            .format(", ".join(model_options['cohorts_held_out'])))
    #        f.write("* validation cohorts: {}"\
        #             .format(", ".join(model_options['cohorts_validating'])))
    train_set = ", ".join(model_options['cohorts_training'])
    if train_set == "all":
        train_set += " except test/val"
    f.write("* train cohorts: {}".format(train_set))
    cv_scheme = " ".join(model_options['model_test_holdout'].split('_'))
    if "fold" in cv_scheme:
        cv_scheme += ", with {} folds".format(model_options['n_folds'])
    f.write("* cross-validation scheme: {}".format(cv_scheme))
    f.write("\t * using {}".format(model_options['validation_criterion']))
    
    
    # features used 
    f.write("### Features Used")
    for key, features in model_options['features_included'].items():
        f.write("* {}".format(key))
        for i in features:
            f.write("\t * {}".format(i))
    
    # performance metrics (must have first generated these images)
    images = [a for a in os.listdir(base_path_name) if 
              ('png' in a and model_name in a)]
    for fn in images:
        f.write("![{fn}]({fn}.png)".format(fn=fn))
        
def main():
    test_y = np.array([1,0])
    train_y = np.array([1,0])
    test_set_scores = np.array([.9,0])
    train_set_scores = np.array([.8, .1])
    
    with open(base_file_name+'.md') as f:
        markdown_report(f,model_options,model_name)


if __name__ == "__main__":
    main()


    # old stuff not using anymore

    # with postgres_pgconnection_generator() as connection:
    #     with connection.cursor() as cursor:
    #         db_saved_outputs = {
    #             'description': model_options['user_description'],
    #             'feature_types': model_options['features_included'].keys(),
    #             'train_cohorts': model_options['cohorts_training'],
    #             'test_cohorts': model_options['cohorts_held_out'],
    #             'n_train_pos' : sum(train_y == 1),
    #             'n_train_neg' : sum(train_y == 0),
    #             'n_test_pos' : sum(test_y == 1),
    #             'n_test_neg' : sum(test_y == 0),
    #             'model_type': model_name,
    #             'train_ap' : average_precision(train_y,train_set_scores),
    #             'test_ap' : average_precision(test_y,test_set_scores),
    #             'file_name' : file_name
    #             }
    #         build_results_table(cursor)
    #         add_row(cursor,db_saved_outputs)
    #         print('row added')
    #     connection.commit()
