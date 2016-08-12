import estimate_prediction_model
from generate_yaml import generate_yaml

# includes all options for each field

template_options = {
    'batch_name' : 'name_for_folder_with_all_yamls_for_batch'
    'model_classes': ['logit','DT','RF','ET','AB','SVM','GB','NB','SGD','KNN'],
    'description': 'name_for_this_parameter_set',
    'name': 'yaml_creation',
    'write_to_database': True, # True or False
    'user': 'ht', # ht, jg, xc, zz - this is case sensitive
    'test_set_type': 'temporal_cohort', # anything other text will result in a random split
    'cv_scheme': 'leave_cohort_out', # k_fold, past_cohorts_only, leave_cohort_out
    # if cv_scheme = 'k_fold', need  'n_folds' key 
    'prediction_grade': 9, # currently only 9 or 6, soon 6-10
    'feature_grade_range': range(6,9), # max must be less than prediction_grade
    'cohorts_held_out': [2011,2012], # any range not overlapping with cohorts_training
    'cohorts_training': [2010]
    'random_seed': 2851,
    'cv_criterion': 'custom_precision_10', # can replace precision with recall and use any number 0-100 or
    # f1, average_precision
    # features can be the string 'all', or a dictionary where keys are table names
    # the table names can have a list of features, the string 'all', 
    # or a dictionary with the single key 'except', then a list of features to exclude
    # 'all' values are drawn from the all_features yaml file in Features, 
    # so check there if you are getting unexpected results
    'features': {
        'grades': {'except':['gpa*']},
        'demographics': ['gender'],
        'mobility': 'all'
    },
    'outcome': 'definite', # not_on_time, is_dropout, definite
    'imputation': 'median_plus_dummies', # median_plus_dummies, mean_plus_dummies, none
    'scaling': 'robust', # robust, standard, none
    'debug': True # True or False
}

time_scales = zip([range(2009,2011),range(2008,2011),range(2007,2011)],
                  [range(6,9),range(7,9),range(8,9)])

for years, grades in time_range:
    template_options['cohorts_training'] = years
    template_options['feature_grade_range'] = grades
    template_options['name'] = '{0}_years_data_{1}_cohorts'.\
                               format(len(grades),len(years))
    generate_yaml(template_options)
    estimate_prediction_model.main(['-m',template_options['name']+'.yaml'])
