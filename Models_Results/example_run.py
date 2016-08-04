import estimate_prediction_model
from generate_yaml import generate_yaml

template_options = {
        'batch_name' : 'testing_yaml_creation', # for an entire batch, fldr name
        'model_classes': ['logit','DT'],
        'description': 'testing yaml creation',
        'name': 'yaml_creation', # specific to a particular set of options      
        'write_to_database': True,
        'user': 'ht',
        'test_set_type': 'temporal_cohort',
        'cv_scheme': 'leave_cohort_out',
        # if cv_scheme = 'k_fold', need  'n_folds' key                          
        'prediction_grade': 9, #currently only 9 or 6
        'feature_grade_range': None, #filled in below
        'cohorts_held_out': [2011,2012],
        'cohorts_training': None, #filled in below
        'random_seed': 2851,
        'cv_criterion': 'custom_precision_10',
        'features': {'grades':
                     {'except':['gpa*']},
                     'demographics': 'all',
                     'mobility': 'all'
                 },
        'outcome': 'definite',
        'imputation': 'median_plus_dummies',
        'scaling': 'robust',
        'debug': True
    }
time_scales = zip([range(2009,2011),range(2008,2011),range(2007,2011)],
                  [range(6,9),range(7,9),range(8,9)])

for years, grades in time_scales:
    template_options['cohorts_training'] = years
    template_options['feature_grade_range'] = grades
    template_options['name'] = '{0}_years_data_{1}_cohorts'.\
                               format(len(grades),len(years))
    generate_yaml(template_options)
    estimate_prediction_model.main(['-m',template_options['name']+'.yaml'])
