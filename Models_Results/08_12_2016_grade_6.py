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
   'batch_name' : '08_12_2016_grade_6',
   'model_classes': ['logit','DT','RF','ET','SVM'],
   'write_to_database': True,
   'user': 'ht',
   'test_set_type': 'temporal_cohort',
   'cv_criterions': ['custom_precision_5_15','custom_recall_5_15'],
   'n_folds': 5,
   'prediction_grade': 6,
   'cohorts_test': [2009],
   'cohorts_val': [2008],
   'debug': False,
   'imputation': 'median_plus_dummies',
   'scaling': 'robust',
   'cv_scheme': 'k_fold'
}

outcome_list = ['not_on_time', 'definite', 'definite_plus_ogt']
max_year = min(template_options['cohorts_val'])
max_grade = template_options['prediction_grade']
cohorts = [range(2007, max_year)]
grade_ranges = [range(max_grade-1,max_grade)]
time_scales = list(zip(cohorts,grade_ranges)) # change with prediction grade


downsample_list = [None, .8, .9]

almost_all = {
   'grades': 'all',
   'demographics': 'all',
   'absence': 'all',
   'intervention': 'all',
   'mobility': 'all',
   'oaa_normalized': {'except': ['like_pl','like_percentile',6,7,8]},
   'snapshots': 'all'
   }
basic = {
   'grades': {'except':['like__gpa','like_classes']},
   'demographics': 'all',
   'absence': ['absence*','absence_unexcused*','tardy*','tardy_unexcused*'],
   'oaa_normalized': {'except': ['like_pl','like_percentile',6,7,8]},
   'snapshots': 'all'
   }

feature_list = []
feature_list.append(almost_all)
feature_list.append(basic)

with Timer('batch {}'.format(template_options['batch_name'])) as batch_timer:
   c = 0; #counter for yaml naming
   for weight in downsample_list:
      template_options['downsample_param'] = weight
      for features in feature_list:
         template_options['features'] = features
         for outcome in outcome_list:
            template_options['outcome'] = outcome
            for years, grades in time_scales:
               #if len(years)==1 and 'cohort' in cv_scheme:
                #  continue
               template_options['cohorts_training']=years
               template_options['feature_grade_range']=grades
               # innermost layer of loop
               template_options['random_seed'] = time.time()
               template_options['name'] = template_options\
                                          ['batch_name']+\
                                          '_param_set_'+str(c)
               template_options['description']= "third pass for grade 6"
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
