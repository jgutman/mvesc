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
    'batch_name' : 'small_sample_test', 
    'model_classes': ['logit','DT','RF','ET','AB','SVM','GB','NB','SGD','KNN'],
    'write_to_database': True,
    'user': 'ht',
    'test_set_type': 'temporal_cohort',
    'cv_criterions': ['custom_precision_5','f1'],
    # if cv_scheme = 'k_fold', need  'n_folds' key 
    'n_folds': 4,
    'prediction_grade': 9, 
    'cohorts_held_out': [2011,2012],
    'debug': True,
    'subset_n': 100
}

cv_scheme_list = ['leave_cohort_out', 'past_cohorts_only'] #k-fold needs many students
feature_list = []
#table_list = ['absence','demographics','grades','mobility','snapshots']
#for t in table_list:
#    feature_list.append({t: 'all'})
basic_features = {
    'demographics': 'all',
    'grades': ['gpa*'],
    'oaa_normalized': 'all',
    'snapshots': 'all'
}
feature_list.append(basic_features)

outcome_list = ['not_on_time', 'definite']
time_scales = list(zip([range(2009,2011),range(2007,2011)],
                  [range(6,9),range(8,9)]))
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
                            template_options['cohorts_training']=years
                            template_options['feature_grade_range']=grades
                            # innermost layer of loop
                            template_options['random_seed'] = time.time()
                            template_options['name'] = 'param_set_'+str(c)
                            template_options['description'] = \
                            """testing all options by looping through """\
                            """with a just {} students"""\
                                .format(template_options['subset_n'])
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
