
import os, sys
pathname = os.path.dirname(sys.argv[0])
full_pathname = os.path.abspath(pathname)
split_pathname = full_pathname.split(sep="mvesc")
base_pathname = os.path.join(split_pathname[0], "mvesc")
import jinja2 as jnj
import yaml
import estimate_prediction_model

def generate_yaml(template_options, yaml_location=None):
    """
    This function takes in a dictionary of template options with all the 
    information necessary to create a model options file.
    Specifically, this must include:
    batch_name (str)
    model_classes (list of str)
    description (str)
    name (str)
    write_to_database (bool)
    user (str)
    test_set_type (str)
    cv_scheme (str)
    prediction_grade (int)
    feature_grade_range (list of ints)
    cohorts_test (list of ints)
    cohorts_val (list of ints)
    cohorts_training (list of ints)
    random_seed (int)
    cv_criterions (list of str)
    outcome (str)
    imputation (str)
    scaling (str)
    debug (bool)
    features (dict or string 'all')

    optional keys: 
    downsample_param (float) - (all the weight of the negative majority class)
    upsample_param (float)
    sample_wt_ratio (float)
    subset_n (int)
    drop_reference (bool)
    dummify (bool)

    the features dictionary should have table names as keys, 
    with each value being either:
       - the string 'all'
       - a list of stings which are each either a feature name, a grade-level
         feature base name with '*' at the end, or a subtring with 
         'like_' prepended
       - a dictionary with a single key 'except', with a value 
         like those above

    :param dict template_options:
    :param str yaml_location: path to save the yaml file, 
        defaults to 'model_options/{batch_name}'
    """
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
                to_remove = []
                for e in features['except']:
                    if type(e) == int:
                        # if except a number, then remove all features 
                        # with that grade level
                        for f in feature_list:
                            if int(f.split('_')[-1]) == e:
                                to_remove.append(f)
                    elif e.split('_')[0] == 'like':
                        # if except starts with 'like', then remove features
                        # containing the string following like
                        e = '_'.join(e.split('_')[1:])
                        for f in feature_list:
                            if e in f:
                                to_remove.append(f)
                    else: 
                        # if except is a feature, then remove that feature
                        to_remove.append(e)
                to_remove = set(to_remove) # removing duplicates
                for f in to_remove:
                    feature_list.remove(f)
                template_options['features'][table] = feature_list
            else: 
                to_add = []
                to_remove = []
                for a in features:
                    if a.split('_')[0] == 'like': 
                        # if one of the features had 'like' prepended, 
                        # then add features containing the string 
                        #following 'like'
                        to_remove.append(a)
                        a  = '_'.join(a.split('_')[1:])
                        for f in all_features[table]:
                            if a in f:
                                to_add.append(f)
                to_add = set(to_add)
                to_remove = set(to_remove)
                for f in to_add:
                    features.append(f)
                for f in to_remove:
                    features.remove(f)
                template_options['features'][table] = features
                            
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
                     {'except':['like__gpa','like_classes']},
                     'demographics': 'all',
                     'mobility': 'all',
                     'oaa_normalized': 
                     {'except': [8, 'like_pl', 'like_percentile']},
                     'absence': ['like_unexcused']
                 },
        'outcome': 'definite',
        'imputation': 'median_plus_dummies',
        'scaling': 'robust',
        'debug': True,
        'upsample_param': .9,
        'drop_reference': False
    }    
    
    generate_yaml(template_options)

if __name__ == "__main__":
    main()
