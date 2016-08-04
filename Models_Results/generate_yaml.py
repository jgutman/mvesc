import os
import jinja2 as jnj
import yaml
import estimate_prediction_model

def generate_yaml(template_options, yaml_location='.'):
    with(open('all_features.yaml')) as f:
        all_features = yaml.load(f)

    if template_options['features'] == 'all':
        template_options['features'] = all_features
    else:
        for table, features in template_options['features'].items():
            if features == 'all':
                template_options['features'][table] = all_features[table]
            elif type(features)==dict and list(features.keys())[0] == 'except':
                feature_list = all_features[table]
                for f in features['except']:
                    feature_list.remove(f)
                    template_options['features'][table] = feature_list
                    
    env = jnj.Environment(loader=jnj.FileSystemLoader('.'))
    env.trim_blocks = True
    temp = env.get_template('model_options.jinja')
    
    with(open(os.path.join(template_options['name'] + '.yaml'), "w")) as f:
        f.write(temp.render(template_options))
    print(template_options['name'] + '.yaml written!' )

def main():
    template_options = {
        'model_classes': ['logit','DT'],
        'description': 'testing yaml creation',
        'name': 'yaml_creation',
        'write_to_database': True,
        'user': 'ht',
        'test_set_type': 'temporal_cohort',
        'cv_scheme': 'leave_cohort_out',
        # if cv_scheme = 'k_fold', need  'n_folds' key
        'cohort': 'cohort_9th',
        'prediction_grade': 10,
        'feature_grade_range': range(6,10),
        'cohorts_held_out': [2011,2012],
        'cohorts_training': [2009,2010],
        'random_seed': 2851,
        'cv_criterion': 'custom_precision_10',
        'features': {'grades':
                     {'except':['gpa*']},
                     'demographics': 'all',
                     'mobility': 'all'
                 },
        'outcome': 'definite',
        'imputation': 'median_plus_dummies',
        'scaling': 'robust'
    }    
    
    time_scales = zip([range(2009,2011),range(2008,2011),range(2007,2011),
                       range(2006,2011)], 
                      [range(6,10),range(7,10),range(8,10),range(9,10)])
    for years, grades in time_scales:
        template_options['cohorts_training'] = years
        template_options['feature_grade_range'] = grades
        template_options['name'] = '{0}_years_data_{1}_cohorts'.\
                                   format(len(grades),len(years))
        generate_yaml(template_options)
        estimate_prediction_model.main(['-m',template_options['name']+'.yaml'])

if __name__ == "__main__":
    main()
