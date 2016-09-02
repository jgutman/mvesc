import os, sys
pathname = os.path.dirname(sys.argv[0])
full_pathname = os.path.abspath(pathname)
split_pathname = full_pathname.split(sep="mvesc")
base_pathname = os.path.join(split_pathname[0], "mvesc")

import estimate_prediction_model
from generate_yaml import generate_yaml
from my_timer import Timer
import time


# setting options that will stay constant for this batch
template_options = {
    'batch_name' : 'first_run_08_05_2016', 
    'model_classes': ['logit','DT','RF','ET','AB','SVM','GB','NB','SGD','KNN'],
    'write_to_database': True,
    'user': 'ht',
    'test_set_type': 'temporal_cohort',
    'cv_criterions': ['custom_precision_5','custom_precision_10',
                      'custom_recall_5', 'f1'],
    # if cv_scheme = 'k_fold', need  'n_folds' key 
    'n_folds': 5,
    'prediction_grade': 10, 
    'cohorts_test': [2013],
    'cohorts_val': [2012],
    'debug': False
}

cv_scheme_list = ['leave_cohort_out', 'past_cohorts_only', 'k-fold']
feature_list = []
table_list = ['absence','grades','mobility', 'oaa_normalized']
for t in table_list:
    feature_list.append({t: 'all'})
feature_list.append('all')
basics = {
    'demographics':'all',
    'snapshots':'all'
}
feature_list.append(basics)
outcome_list = ['not_on_time', 'is_dropout', 'definite']
cohorts = [range(a, 2012) for a in range(2007,2012)]
grade_ranges = [range(a,10) for a in reversed(range(5,10))]
time_scales = list(zip(cohorts,grade_ranges))
imputation_list = ['median_plus_dummies', 'mean_plus_dummies']
scaling_list = ['robust','standard'] # error with none for KNN

with Timer('batch {}'.format(template_options['batch_name'])) as batch_timer:
    c = 0; #counter for yaml naming
    for cv_scheme in cv_scheme_list:
        template_options['cv_scheme'] = cv_scheme
        for features in feature_list:
            template_options['features'] = features
            for outcome in outcome_list:
                template_options['outcome'] = outcome
                for imputation in imputation_list:
                    template_options['imputation'] = imputation
                    for scaling in scaling_list:
                        template_options['scaling'] = scaling
                        for years, grades in time_scales:
                            if len(years)==1 and 'cohort' in cv_scheme:
                                continue
                            template_options['cohorts_training']=years
                            template_options['feature_grade_range']=grades
                            # innermost layer of loop
                            template_options['random_seed'] = time.time()
                            template_options['name'] = 'param_set_'+str(c)
                            template_options['description'] = \
                           """First large run looping through many """\
                            """models on 08/5/2016 """
                            generate_yaml(template_options)
                            path = os.path.join(base_pathname,
                                                'Models_Results',
                                                'model_options',
                                                template_options\
                                                ['batch_name'],
                                                template_options['name']
                                                +'.yaml')
                            try:
                                estimate_prediction_model.main(['-m',path])
                            except:
                                print(template_options)
                                raise
                            print('param set {0} finished: run for {1} '\
                                  'seconds so far'\
                                  .format(c, batch_timer.time_check()))
                            c = c+1
