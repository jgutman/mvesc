import estimate_prediction_model
from generate_yaml import generate_yaml
import time


# setting options that will stay constant for this batch
template_options = {
    'batch_name' : 'testing_yaml_creation', 
    'model_classes': ['logit','DT','RF','ET','AB','SVM','GB','NB','SGD','KNN'],
    'write_to_database': True,
    'user': 'ht',
    'test_set_type': 'temporal_cohort',
    'cv_scheme': 'leave_cohort_out',
    # if cv_scheme = 'k_fold', need  'n_folds' key 
    'prediction_grade': 9, 
    'cohorts_held_out': [2011,2012],
    'debug': True,
    'n_sample': 500
}

cv_scheme_list = ['k_fold', 'past_cohorts_only', 'leave_cohort_out']
cv_criterion_list = ['custom_precision_5','custom_recall_5', 'f1', 
                         'average_precision']
feature_list = []
table_list = ['absence','demographics','grades','mobility','snapshots']
for t in table_list:
    feature_list.append({t: 'all'})
basic_features = {
    'demographics': 'all',
    'grades': ['gpa*'],
    'oaa_normalized': 'all',
    'snapshots': 'all'
}
feature_list.append(basic_features)
feature_list.append('all')

outcome_list = ['not_on_time', 'definite']
time_scales = zip([range(2009,2011),range(2008,2011),range(2007,2011)],
                  [range(6,9),range(7,9),range(8,9)])
imputation_list = ['median_plus_dummies', 'mean_plus_dummies']
scaling_list = ['robust','standard','none']

for cv_scheme in cv_scheme_list:
    template_options['cv_scheme'] = cv_scheme
    for cv_criterion in cv_criterion_list:
        template_options['cv_criterion'] = cv_criterion
        for features in feature_list:
            template_options['features'] = features
            for outcome in outcome_list:
                template_options['outcome'] = outcome
                for imputation in imputation_list:
                    template_options['imputation'] = imputation
                    for scaling in scaling_list:
                        template_options['scaling'] = scaling
                        for years, grades in time_scales:
                            template_options['cohorts_training'] = years
                            template_options['feature_grade_range'] = grades
                            
                            # innermost layer of loop
                            template_options['random_seed'] = time.time()
                            template_options['name'] = 'test'
                            template_options['description'] = """
                            testing all options by looping through 
                            with a just 500 students"""
                            generate_yaml(template_options)
                            estimate_prediction_model.main(['-m',
                                                            template_options\
                                                            ['name']+'.yaml'])
