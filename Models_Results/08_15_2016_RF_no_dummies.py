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
   'batch_name' : '08_15_2016_RF_no_dummies', 
   'model_classes': ['RF'],
   'write_to_database': True,
   'user': 'ht',
   'test_set_type': 'temporal_cohort',
   'cv_criterions': ['custom_precision_5_15','custom_recall_5_15'],
   'n_folds': 5,
   'debug': False,
   'imputation': 'median_plus_dummies',
   'scaling': 'robust',
   'cv_scheme': 'k_fold',
   'dummify': False
}


outcome_list = ['not_on_time', 'definite', 'definite_plus_ogt']

prediction_grade_list = list(reversed([6,7,8,9,10]))
cohorts_test_list = list(reversed([2009,2010,2011,2012,2013]))
time_scales = list(zip(prediction_grade_list, cohorts_test_list))

downsample_list = [None, .8, .9]


with Timer('batch {}'.format(template_options['batch_name'])) as batch_timer:
   c = 0; #counter for yaml naming
   for weight in downsample_list:
      template_options['downsample_param'] = weight
      for outcome in outcome_list:
         template_options['outcome'] = outcome
         almost_all = {
            'grades': 'all',
            'demographics': 'all',
            'absence': 'all',
            'intervention': 'all',
            'mobility': 'all',
            'oaa_normalized': {'except': ['like_pl','like_percentile']},
            'snapshots': 'all'
         }
         for grade, test in time_scales:
            template_options['prediction_grade'] = grade
            template_options['cohorts_test'] = [test ]
            template_options['cohorts_val'] = [test - 1]
            template_options['cohorts_training'] = [test - 2]
            template_options['feature_grade_range'] = [grade - 1]
            if grade not in almost_all['oaa_normalized']['except']:
               almost_all['oaa_normalized']['except'].append(grade)
            template_options['features'] = almost_all
            # innermost layer of loop
            template_options['random_seed'] = time.time()
            template_options['name'] = template_options\
                                       ['batch_name']+\
                                       '_param_set_'+str(c)
            template_options['description']= "trying not including dummies"
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
