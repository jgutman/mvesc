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

def plot_score_distribution(soft_predictions, save_location, 
                            run_name, model_name):
    plt.hist(soft_predictions, 
             np.linspace(min(min(soft_predictions), 0),
                         max(max(soft_predictions), 1), 
                         100), align = 'left')
    plt.title("distribution of scores for {} model".format(model_name))
    plt.xlabel("soft prediction score")
    plt.ylabel("number of students")
    base = save_location + "/" + run_name + "_" + model_name
    plt.savefig(base+'_score_dist.png', bbox_inches='tight')

def plot_precision_recall(soft_predictions, test_y, save_location,
                          run_name, model_name):
    precision,recall,thresholds=precision_recall_curve(test_y,soft_predictions)
    plt.figure()
    plt.hold(True)
    plt.plot(recall, precision)
    plt.title("precision vs. recall")
    plt.xlabel("recall")
    plt.ylabel("precision")
    base = save_location + "/" + run_name + "_" + model_name
    plt.savefig(base+'_pr_vs_threshold.png', bbox_inches='tight')

def plot_precision_recall_threshold(soft_predictions, test_y, save_location,
                                    run_name, model_name):
    precision,recall,thresholds=precision_recall_curve(test_y,soft_predictions)
    thresholds = np.concatenate(([0],thresholds))
    plt.figure()
    plt.hold(True)
    plt.plot(thresholds, precision)
    plt.plot(thresholds, recall)
    plt.title("precision and recall vs threshold")
    plt.xlabel("threshold")
    plt.legend(["precision", "recall"])
    base = save_location + "/" + run_name + "_" + model_name
    plt.savefig(base+'_precision_recall.png', bbox_inches='tight')

def plot_confusion_matrix(soft_predictions, test_y, threshold, save_location,
                     run_name, model_name):
    cm = confusion_matrix(test_y, soft_predictions > threshold)
    plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    plt.title("confusion matrix at probability {} threshold".format(threshold))
    plt.colorbar()
    # tick_marks = np.arange(len(class_names)) 
    # plt.xticks(tick_marks, class_names, rotation=45)
    # plt.yticks(tick_marks, class_names)
    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    base = save_location + "/" + run_name + "_" + model_name
    plt.savefig(base+'_confusion_mat_{}.png'.format(threshold),
                bbox_inches='tight')
    

def markdown_report(f,model_options,save_location, run_name,model_name):

    # header
    f.write("# Report for {}\n".format(" ".join(run_name.split('_'))
                                       + " " + model_name))
    f.write(model_options['user_description']+'\n')
    
    # model options used
    f.write("\n### Model Options\n")
    f.write("* label used: {}\n".format(model_options['outcome_name']))
    f.write("* initial cohort grade: {}\n"\
            .format(model_options['cohort_grade_level_begin'][-3:-2]))
    f.write("* test cohorts: {}\n"\
            .format(", ".join([str(a) for a in 
                               model_options['cohorts_held_out']])))
    train_set = model_options['cohorts_training']
    if train_set == "all":
        train_set += " except test/val"
    else:
        ", ".join(train_set)
    f.write("* train cohorts: {}\n".format(train_set))
    cv_scheme = " ".join(model_options['model_test_holdout'].split('_'))
    if "fold" in cv_scheme:
        cv_scheme += ", with {} folds".format(model_options['n_folds'])
    f.write("* cross-validation scheme: {}\n".format(cv_scheme))
    f.write("\t * using {}\n".format(model_options['validation_criterion']))
    imputation = "_".join(model_options['missing_impute_strategy'].split('_'))
    f.write("* imputations strategy: {}\n".format(imputation))
    
    # features used 
    f.write("\n### Features Used\n")
    for key, features in model_options['features_included'].items():
        f.write("* {}\n".format(key))
        for i in features:
            f.write("\t * {}\n".format(i))

    # performance metrics (must have first generated these images)
    f.write("\n### Performance Metrics\n")
    images = [a for a in os.listdir(save_location) if 
              ('png' in a and model_name in a and run_name in a)]
    for fn in images:
        f.write("![{fn}]({fn})\n".format(fn=fn))
        
def main():
    save_location = sys.argv[1]
    options_location = sys.argv[2]

    test_y = np.ones(100)
    test_set_scores = np.random.rand(100)
    model_options = read_in_yaml(options_location)
    model_name = 'logit'
    run_name = model_options['file_save_name']
    
    plot_score_distribution(test_set_scores, save_location, run_name, 
                            model_name)
    plot_precision_recall_threshold(test_set_scores, test_y, save_location, 
                                    run_name, model_name)
    plot_precision_recall(test_set_scores, test_y, save_location, 
                          run_name, model_name)
    plot_confusion_matrix(test_set_scores, test_y, .5, save_location, 
                          run_name, model_name)

    with open(save_location+"/"+run_name+"_"+model_name+'.md','w+') as f:
        markdown_report(f,model_options,save_location, run_name,model_name)
    print("report written to",save_location)


if __name__ == "__main__":
    main()
