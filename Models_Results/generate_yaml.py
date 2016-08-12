
import os, sys
pathname = os.path.dirname(sys.argv[0])
full_pathname = os.path.abspath(pathname)
split_pathname = full_pathname.split(sep="mvesc")
base_pathname = os.path.join(split_pathname[0], "mvesc")
import jinja2 as jnj
import yaml
import estimate_prediction_model

def generate_yaml(template_options, yaml_location=None):
    path_name = os.path.join(base_pathname,'Models_Results')
    if not yaml_location:
        yaml_location = 'model_options/'+template_options['batch_name']
    with(open(os.path.join(base_pathname,'Features/all_features.yaml'))) as f:
        all_features = yaml.load(f)

    if template_options['features'] == 'all':
        template_options['features'] = all_features
    else:
        for table, features in template_options['features'].items():
            if features == 'all':
                template_options['features'][table] = all_features[table]
            elif type(features)==dict and list(features.keys())[0] == 'except':
                feature_list = all_features[table]
                if type(features['except'][0]) == int:
                    for gr in features['except']:
                        to_remove = []
                        for f in feature_list:
                            if int(f.split('_')[-1]) == gr:
                                to_remove.append(f)
                        for f in to_remove:
                            feature_list.remove(f)
                    template_options['features'][table] = feature_list
                else: 
                    for f in features['except']:
                        feature_list.remove(f)
                    template_options['features'][table] = feature_list
    
    if type(template_options['cv_criterions']) != list:
        template_options['cv_criterions'] = [template_options['cv_criterions']]

    env = jnj.Environment(loader=jnj.FileSystemLoader(path_name))
    env.trim_blocks = True
    temp = env.get_template('model_options.jinja')
    os.makedirs(os.path.join(path_name,yaml_location), exist_ok=True)
    with(open(os.path.join(path_name, yaml_location, 
                           template_options['name'] + '.yaml'), "w")) as f:
        f.write(temp.render(template_options))
    print(template_options['name'] + '.yaml written!' )

def main():
    template_options = {
        'batch_name' : 'testing_new_options',# for an entire batch, fldr name
        'model_classes': ['logit','DT'],
        'description': 'testing writing all features to a single table and ' \
            'all scores to a single table and new cv_scorer and '\
            'new test score feature names',
        'name': 'test', # specific to a particular set of options
        'write_to_database': True,
        'user': 'ht',
        'test_set_type': 'temporal_cohort',
        'cv_scheme': 'leave_cohort_out',
        # if cv_scheme = 'k_fold', need  'n_folds' key
        'prediction_grade': 8,
        'feature_grade_range': range(6,8),
        'cohorts_test': [2010],
        'cohorts_val': [2009],
        'cohorts_training': [2007,2008],
        'random_seed': 2851,
        'cv_criterions': ['custom_precision_10_20','custom_recall_5_15'],
        'features': {'grades':
                     {'except':['gpa*']},
                     'demographics': 'all',
                     'mobility': 'all',
                     'oaa_normalized': 
                     {'except': [8]}
                 },
        'outcome': 'definite',
        'imputation': 'median_plus_dummies',
        'scaling': 'robust',
        'debug': True
    }    
    
    generate_yaml(template_options)

if __name__ == "__main__":
    main()
