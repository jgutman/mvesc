import estimate_prediction_model
from generate_yaml import generate_yaml

# includes all options for each field
# Note: The only field here that takes a range of values (in the sense that generate_yaml
#       would produce the crossproduct of those ranges) is model_classes. Don't give
#       sets of parameters to anything else.

template_options = {
    'batch_name' : 'name_for_folder_with_all_yamls_for_batch',
    'name': 'name_for_specifice_param_set',
    'model_classes': ['logit','DT','RF','ET','AB','SVM','GB','NB','SGD','KNN'],
    'description': 'name_for_this_parameter_set',
    'write_to_database': True, # True or False
    'user': 'ht', # ht, jg, xc, zz - this is case sensitive
    'test_set_type': 'temporal_cohort', # anything other text will result in a random split
    'cv_scheme': 'leave_cohort_out', # k_fold, past_cohorts_only, leave_cohort_out
    # if cv_scheme = 'k_fold', need  'n_folds' key 
    'prediction_grade': 9, # between 6 and 10
    'feature_grade_range': range(6,9), # max must be less than prediction_grade
    'cohorts_held_out': [2011,2012], # any range not overlapping with cohorts_training
    'cohorts_training': [2010],
    'random_seed': 2851,
    'cv_criterion': 'custom_precision_10', # can replace precision with recall and use any number 0-100 or, can also use f1, average_precision
    # features can be the string 'all', or a dictionary where keys are table names
    # the table names can have a list of features (i.e., columns in the table), the string 'all', 
    # or a dictionary with the single key 'except', then a list of features to exclude
    # 'all' values are drawn from the all_features yaml file in Features, 
    # so check there if you are getting unexpected results.
    # If you are putting * after a column name, it gives all grades in the feature_grade_range.
    'features': {
        'grades': {'except':['gpa*']},
        'demographics': ['gender'],
        'mobility': 'all'
    },
    'outcome': 'definite', # not_on_time, is_dropout, definite, definite_plus_ogt
    'imputation': 'median_plus_dummies', # median_plus_dummies, mean_plus_dummies, none
    'scaling': 'robust', # robust, standard, none
    'debug': True # True or False
}

# optional values:
# 'subset_n': uses only a small number of students - only for debugging purposes
# 'downsample_param': if you want to use downsampling, this is the percentage of students in the negative class after rebalancing 
# 'upsample_param': if you want to use upsampling, this is the percentage of students in the negative class after rebalancing
# 'sample_wt_ratio: if you want to re-weight classes, re-weighting param passed to sklearn models
# 'dummify': turn categorical variables into dummy variables (1-hot representation) - defaults to true, true required for some model types
# 'drop_reference': if 'dummify' is true, this drops the most frequent dummy variable as a reference, to preserve independence of the variables - defaults to true


# after making the dictionary, call generate_yaml to build the options file
generate_yaml(template_options)

# after generating the yaml file, call estimate_prediction_model with the appropriate option
estimate_prediction_model.main(['-m',template_options['name']+'.yaml'])
