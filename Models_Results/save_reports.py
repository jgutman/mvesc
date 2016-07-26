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
    confusion_matrix, precision_score

class Top_features():
    def DT(model, columns, k):
        imp = model.best_estimator_.feature_importances_
        top_feat = sorted(zip(columns,imp.tolist()),
                           key=lambda x: x[1], reverse=True)
        return top_feat[:k]

    def logit(model, columns, k):
        coefs = model.best_estimator_.coef_
        top_coefs = sorted(zip(columns,coefs.tolist()[0]),
                           key=lambda x: x[1], reverse=True)
        return top_coefs[:k]

    # def SVM(model, columns, k):
    #     coefs = model.best_estimator_.coef_
    #     top_coefs = sorted(zip(columns,coefs.tolist()[0]),
    #                        key=lambda x: x[1], reverse=True)
    #     return top_coefs[:k]

    
def plot_precision_recall_n(y_true, y_prob, save_location, 
                            run_name, model_name):
    # from Rayid's magicloops code
    y_score = y_prob
    precision_curve, recall_curve, pr_thresholds = precision_recall_curve(y_true, y_score)
    precision_curve = precision_curve[:-1]
    recall_curve = recall_curve[:-1]
    pct_above_per_thresh = []
    number_scored = len(y_score)
    for value in pr_thresholds:
        num_above_thresh = len(y_score[y_score>=value])
        pct_above_thresh = num_above_thresh / float(number_scored)
        pct_above_per_thresh.append(pct_above_thresh)
    pct_above_per_thresh = np.array(pct_above_per_thresh)
    plt.clf()
    fig, ax1 = plt.subplots()
    ax1.plot(pct_above_per_thresh, precision_curve, 'b')
    ax1.set_xlabel('percent of population')

    ax1.set_ylabel('precision', color='b')
    ax2 = ax1.twinx()
    ax2.plot(pct_above_per_thresh, recall_curve, 'r')
    ax2.set_ylabel('recall', color='r')
    
    base = save_location + "/" + run_name + "_" + model_name
    plt.savefig(base+'_precision_recall_at_k.png', bbox_inches='tight')

def precision_at_k(y_true, y_scores, k):
    # from Rayid's magicloops code
    threshold = np.sort(y_scores)[::-1][int(k*len(y_scores))]
    y_pred = np.asarray([1 if i >= threshold else 0 for i in y_scores])
    return precision_score(y_true, y_pred)    

def plot_score_distribution(soft_predictions, save_location, 
                            run_name, model_name):
    min_x = min(min(soft_predictions), 0)
    max_x = max(max(soft_predictions), 1)
    plt.figure()
    plt.hist(soft_predictions, np.linspace(min_x,max_x,100), align = 'left')
    plt.title("distribution of scores for {} model".format(model_name))
    plt.xlabel("soft prediction score")
    plt.xlim([min_x,max_x])
    plt.ylabel("number of students")
    base = save_location + "/" + run_name + "_" + model_name
    plt.savefig(base+'_score_dist.png', bbox_inches='tight')


def plot_precision_recall(soft_predictions, test_y, save_location,
                          run_name, model_name):
    precision,recall,thresholds=precision_recall_curve(test_y,soft_predictions)
    plt.figure()
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
    # add precision/recall cutoffs
    plt.figure()
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
    

def markdown_report(f, save_location, saved_outputs):
    model_options = saved_outputs['model_options']
    model_name = saved_outputs['model_name']
    run_name = model_options['file_save_name']
    test_y = saved_outputs['test_y']
    test_set_scores = saved_outputs['test_set_soft_preds']

    # header
    f.write("# Report for {}".format(" ".join(run_name.split('_'))
                                       + " " + model_name))
    f.write(model_options['user_description']+',')
    
    # model options used
    f.write("### Model Options\n")

    f.write("* label used: {}\n".format(model_options['outcome_name']))

    f.write("* initial cohort grade: {}\n"\
            .format(model_options['cohort_grade_level_begin'][-3:-2]))

    f.write("* test cohorts: {}\n"\
            .format(", ".join([str(a) for a in 
                               model_options['cohorts_held_out']])))

    f.write("\t * {0} positive examples, {1} negative examples\n"\
            .format(sum(test_y==1), sum(test_y==0)))

    train_set = model_options['cohorts_training']
    if train_set == "all":
        train_set += " except test/val"
    else:
        train_set = ", ".join([str(a) for a in train_set])
    f.write("* train cohorts: {}\n".format(train_set))
    f.write("\t * {0} postive examples, {1} negative examples\n"\
            .format(saved_outputs['train_set_balance'][1],
                    saved_outputs['train_set_balance'][0]))

    cv_scheme = " ".join(model_options['parameter_cross_validation_scheme']\
                         .split('_'))
    if "fold" in cv_scheme:
        cv_scheme += ", with {} folds".format(model_options['n_folds'])
    f.write("* cross-validation scheme: {}\n".format(cv_scheme))
    params = saved_outputs['parameter_grid']
    model = saved_outputs['estimator'].best_estimator_
    n_models = 1;
    for param, options in params.items():
        option_str = ", ".join([str(a) for a in options])
        f.write("\t * searching {} in {}\n".format(param, option_str))
        f.write("\t * chose {} = {}\n".format(param, getattr(model,param)))
        n_models *= len(options)
    f.write("\t * using {}\n".format(model_options['validation_criterion']))

    imputation = " ".join(model_options['missing_impute_strategy'].split('_'))
    f.write("* imputation strategy: {}\n".format(imputation))

    scaling = model_options['feature_scaling']
    f.write("* scaling strategy: {}\n".format(scaling))
    
    # features used 
    f.write("### Features Used\n")
    for key, features in model_options['features_included'].items():
        f.write("* {}\n".format(key))
        for i in features:
            f.write("\t * {}\n".format(i))

    # performance metrics (must have first generated these images)
    f.write("### Performance Metrics\n")
    f.write("on average, model run in {:0.2f} seconds ({} times) <br/>"\
            .format(saved_outputs['time']/float(n_models),n_models))
    prec_10 = precision_at_k(test_y, test_set_scores, .1)
    prec_5 = precision_at_k(test_y, test_set_scores, .05)
    f.write("precision on top 10%: {:0.3} <br/>".format(prec_10))
    f.write("precision on top 5%: {:0.3} <br/>".format(prec_5))
    try:
        get_top_features = getattr(Top_features, model_name)
    except AttributeError:
        print('top features not implemented for {}'.format(model_name))
        pass
    else:
        top_features = get_top_features(saved_outputs['estimator'],
                                        saved_outputs['features'], 3)
        f.write("top features: {} ({:0.2}), {} ({:0.2}), {} ({:0.2})\n"\
                .format(top_features[0][0],top_features[0][1],
                        top_features[1][0],top_features[1][1],
                        top_features[2][0],top_features[2][1]))
    images = [a for a in os.listdir(save_location) if 
              ('png' in a and model_name in a and run_name in a)]
    for fn in images:
        f.write("![{fn}]({fn})\n".format(fn=fn))
        

def write_model_report(save_location, saved_outputs):
    model_options = saved_outputs['model_options']
    model_name = saved_outputs['model_name']
    run_name = model_options['file_save_name']
    test_y = saved_outputs['test_y']
    test_set_scores = saved_outputs['test_set_soft_preds']

    plot_score_distribution(test_set_scores, save_location, run_name, 
                            model_name)
    #plot_precision_recall_threshold(test_set_scores, test_y, save_location, 
    #                                run_name, model_name)
    plot_precision_recall(test_set_scores, test_y, save_location, 
                          run_name, model_name)
    plot_precision_recall_n(test_y, test_set_scores,save_location, 
                            run_name, model_name)
    #plot_confusion_matrix(test_set_scores, test_y, .5, save_location, 
    #                      run_name, model_name)
    plot_confusion_matrix(test_set_scores, test_y, .3, save_location, 
                          run_name, model_name)
    with open(save_location+"/"+run_name+"_"+model_name+'.md','w+') as f:
                markdown_report(f,save_location, saved_outputs)
    print("report written to",save_location)


def main():
    # note: this testing is outdated
    try:
        save_location = sys.argv[1]
        options_location = sys.argv[2]
    except:
        print("usage: python save_reports <directory to save to> "
              "<location of model options file>")
        sys.exit(1)

    model_options = read_in_yaml(options_location)
    model_name = 'logit'
    test_y = np.concatenate((np.ones(50),np.zeros(50)))
    test_set_scores = test_y + np.random.randn(test_y.size)
    test_set_scores = np.maximum(np.minimum(test_set_scores,1),0)
    saved_outputs = {
        'model_name' : model_name,
        'test_y' : test_y,
        'test_set_soft_preds' : test_set_scores,
        'model_options' : model_options
        }

    write_model_report(save_location, saved_outputs)


if __name__ == "__main__":
    main()
