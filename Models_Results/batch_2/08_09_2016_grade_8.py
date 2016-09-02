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
   'batch_name' : '08_09_2016_grade_8', 
   'model_classes': ['logit','DT','RF','ET','SVM','GB'],
   'write_to_database': True,
   'user': 'ht',
   'test_set_type': 'temporal_cohort',
   'cv_criterions': ['custom_precision_5','custom_precision_10',
                     'custom_recall_5', 'f1'],
   # if cv_scheme = 'k_fold', need  'n_folds' key 
   'n_folds': 5,
   'prediction_grade': 8, 
   'cohorts_test': [2011],
   'cohorts_val': [2010],
   'debug': False,
   'features': 'all',
   'imputation': 'median_plus_dummies',
   'scaling': 'robust'
}

cv_scheme_list = ['leave_cohort_out', 'past_cohorts_only', 'k_fold']
outcome_list = ['not_on_time', 'is_dropout', 'definite']
max_year = min(template_options['cohorts_val'])
max_grade = template_options['prediction_grade']
cohorts = [range(a, max_year) for a in range(2007,max_year)]
grade_ranges = [range(a,max_grade) for a in reversed(range(5,max_grade))]
time_scales = list(zip(cohorts,grade_ranges)) # change for different predictions

with Timer('batch {}'.format(template_options['batch_name'])) as batch_timer:
   c = 0; #counter for yaml naming
   for cv_scheme in cv_scheme_list:
      template_options['cv_scheme'] = cv_scheme
      for outcome in outcome_list:
         template_options['outcome'] = outcome
         for years, grades in time_scales:
            if len(years)==1 and 'cohort' in cv_scheme:
               continue
            template_options['cohorts_training']=years
            template_options['feature_grade_range']=grades
            # innermost layer of loop
            template_options['random_seed'] = time.time()
            template_options['name'] = template_options\
                                       ['batch_name']+\
                                       '_param_set_'+str(c)
            template_options['description'] = "running second pass for grade 8"
            generate_yaml(template_options)
            model_option_path = os.path.join(base_pathname,
                                             'Models_Results',
                                             'model_options',
                                             template_options\
                                             ['batch_name'],
                                             template_options['name']
                                             +'.yaml')
            grid_option_path = os.path.join(base_pathname,
                                            'Models_Results',
                                            'grid_options',
                                            'grid_options_small.yaml')
            try:
               estimate_prediction_model.main(['-m', model_option_path,
                                               '-g', grid_option_path])
            except:
               print(template_options)
               raise
            print('param set {0} finished: run for {1} seconds so far'\
                  .format(c, batch_timer.time_check()))
            c = c+1
