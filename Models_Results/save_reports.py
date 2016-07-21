import os, sys
pathname = os.path.dirname(sys.argv[0])
full_pathname = os.path.abspath(pathname)
split_pathname = full_pathname.split(sep="mvesc")
base_pathname = os.path.join(split_pathname[0], "mvesc")
parentdir = os.path.join(base_pathname, "ETL")
sys.path.insert(0,parentdir)
from mvesc_utility_functions import * 
from estimate_prediction_model import read_in_yaml

import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import precision_recall_curve, roc_curve, f1_score, \
    confusion_matrix

def score_distribution(soft_predictions, base_file_name):
    plt.hist(soft_predictions, 
             np.linspace(min(min(soft_predictions), 0),
                         max(max(soft_predictions), 1), 
                         100), align = 'left')
    model_name = base_file_name.split('_')[-1]
    plt.title("distribution of scores for {} model".format(model_name))
    plt.xlabel("soft prediction score")
    plt.ylabel("number of students")
    plt.savefig(base_file_name+'_score_dist.png', bbox_inches='tight')
    

def markdown_report(f, model_options, base_file_name,  model_name):
    file_name =  model_options['file_save_name']

    # header
    f.write("# Report for {}\n".format(" ".join(file_name.split('_')))) # int instead of str error
    f.write(model_options['user_description']+'\n')
    f.write("Label used: {}\n".format(model_options['outcome_name']))
    
    # model options used
    f.write("### Model Options")
    f.write("* initial cohort grade: {}\n"\
            .format(model_options['cohort_grade_level_begin'][-3:-2]))
    f.write("* test cohorts: {}\n"\
            .format(", ".join([str(a) for a in 
                               model_options['cohorts_held_out']])))
    train_set = ", ".join(model_options['cohorts_training'])
    if train_set == "all":
        train_set += " except test/val"
    f.write("* train cohorts: {}\n".format(train_set))
    cv_scheme = " ".join(model_options['model_test_holdout'].split('_'))
    if "fold" in cv_scheme:
        cv_scheme += ", with {} folds".format(model_options['n_folds'])
    f.write("* cross-validation scheme: {}\n".format(cv_scheme))
    f.write("\t * using {}\n".format(model_options['validation_criterion']))
    
    
    # features used 
    f.write("### Features Used")
    for key, features in model_options['features_included'].items():
        f.write("* {}\n".format(key))
        for i in features:
            f.write("\t * {}\n".format(i))
    
    # performance metrics (must have first generated these images)
    report_dir = '.'
    images = [a for a in os.listdir(report_dir) if 
              ('png' in a and model_name in a and file_name in a)]
    for fn in images:
        f.write("![{fn}]({fn})\n".format(fn=fn))
        
def main():
    test_y = np.ones(100)
    test_set_scores = np.random.rand(100)
    
    base_path = ''
    model_options = read_in_yaml("../Models_Results/test_reporting_options.yaml")
    model_name = 'logit'
    base_file_name = (base_path + model_options['file_save_name'] +'_' 
                      + model_name)
    
    score_distribution(test_set_scores,base_file_name)

    with open(base_file_name+'.md','w+') as f:
        markdown_report(f,model_options,base_file_name,model_name)



if __name__ == "__main__":
    main()
