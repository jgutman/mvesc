import os, sys
pathname = os.path.dirname(sys.argv[0])
full_pathname = os.path.abspath(pathname)
split_pathname = full_pathname.split(sep="mvesc")
base_pathname = os.path.join(split_pathname[0], "mvesc")
sys.path.insert(0, os.path.join(base_pathname, 'ETL'))
sys.path.insert(0, os.path.join(base_pathname, 'ModelsResults'))
sys.path.insert(0, os.path.join(base_pathname, 'Features'))

from mvesc_utility_functions import *
from estimate_prediction_model import build_outcomes_plus_features,temporal_cohort_test_split,impute_missing_values
import numpy as np
import pandas as pd
import random
from functools import partial
import itertools
from my_timer import Timer 
import pickle
import yaml
from sklearn.metrics import precision_score, recall_score
from sklearn.preprocessing import RobustScaler

def scale_features_plus_scaler(train, val, test, strategy):
    """
    Scales features based on the training values with the given strategy   
    Modified here to also return the scaler
    Note: used in make_predictions_for_unlabeled_students

    :param pd.DataFrame train:
    :param pd.DataFrame val:  
    :param pd.DataFrame test: 
    :param str strategy:      
    :returns: scaled training, val, and test sets, and scaler
    :rtype: pd.DataFrame, pd.DataFrame, pd.DataFrame, sklearn scaler object  
    """
    zero_variance_columns = [x for x in train.columns 
                             if len(train[x].unique()) == 1]
    train.drop(zero_variance_columns, axis=1, inplace=True)
    val.drop(zero_variance_columns, axis=1, inplace=True)
    test.drop(zero_variance_columns, axis=1, inplace=True)

    if (strategy == 'none'):
        return train, val, test
    elif(strategy == 'standard' or strategy == 'robust'):
        non_binary_columns = [x for x in train.columns if  
                              len(train[x].unique())>2]
        if (len(non_binary_columns) > 0):
            if strategy == 'standard':
                scaler = StandardScaler() 
            else:
                scaler = RobustScaler()
            train_non_binary = train[non_binary_columns]
            val_non_binary = val[non_binary_columns]
            test_non_binary = test[non_binary_columns]
            scaler.fit(train_non_binary)
            train_non_binary = pd.DataFrame(scaler.transform(train_non_binary),
                columns = non_binary_columns, index = train.index)
            val_non_binary = pd.DataFrame(scaler.transform(val_non_binary),
                columns = non_binary_columns, index = val.index)
            test_non_binary = pd.DataFrame(scaler.transform(test_non_binary),
                columns = non_binary_columns, index = test.index)
            train_scaled = train.drop(non_binary_columns, axis=1)
            val_scaled = val.drop(non_binary_columns, axis=1)
            test_scaled = test.drop(non_binary_columns, axis=1)
            train_scaled = train_scaled.merge(train_non_binary,
                left_index=True, right_index=True)
            val_scaled = val_scaled.merge(val_non_binary,
                left_index=True, right_index=True)
            test_scaled = test_scaled.merge(test_non_binary,
                left_index=True, right_index=True)
            return train_scaled,val_scaled, test_scaled, scaler
        else:
            return train, val, test, scaler
    else:
        print('unknown feature scaling strategy. try "{}", "{}", or "{}"'\
              .format('standard', 'robust', 'none'))
        return train, val, test

def read_and_preprocess(filename):
    """
    Reads in a pickeled model file and rebuilds the training, test, and 
    validation data. This function works returns features for the original
    training, validation, and test students. For a similar function for current
    students, see `test_impute_and_scale` in 
    `make_predictions_for_unlabeled_students.py`.
    Returns features for all the students, both scaled and unscaled, 
    the scaler, the column-order, and the model itself.
    
    :param str filename: the filename specifying which model to read in
    :returns: scaled features, unscaled features, sklearn scaler, 
        list of columns in order, the model
    :rtype: pd.DataFrame, pd.DataFrame, sklearn scaler object, list of str, 
        sklearn estimator object
    """
    model_name = filename.split('_')[-3]
    with open('/mnt/data/mvesc/Models_Results/pkls/'+filename+'_'+ model_name\
              + '.pkl', "rb" ) as f:
        d = pickle.load(f)
    model_options = d['model_options']
    model = d['estimator']
    columns = d['estimator_features']
    outcome_plus_features = build_outcomes_plus_features(model_options,None)
    outcome_plus_features.dropna(subset=[model_options['outcome_name'],
            model_options['cohort_grade_level_begin']], inplace=True)
    train, val, test = temporal_cohort_test_split(outcome_plus_features,
            model_options['cohort_grade_level_begin'],
            model_options['cohorts_test'],
            model_options['cohorts_val'],
            model_options['cohorts_training'])
    train_X_pre = train.drop([model_options['outcome_name'],
                      model_options['cohort_grade_level_begin']],axis=1)
    test_X_pre = test.drop([model_options['outcome_name'],
                        model_options['cohort_grade_level_begin']],axis=1)
    val_X_pre = val.drop([model_options['outcome_name'],
                      model_options['cohort_grade_level_begin']],axis=1)
    train_y = train[model_options['outcome_name']]
    test_y = test[model_options['outcome_name']]
    val_y = val[model_options['outcome_name']]
    train_X, val_X, test_X = impute_missing_values(train_X_pre, val_X_pre,\
                    test_X_pre, model_options['missing_impute_strategy'])
    train_X = train_X.filter(columns)
    val_X = val_X.filter(columns)
    test_X = test_X.filter(columns)
    train_X, val_X, test_X, scaler = scale_features(train_X, val_X, test_X,
                    model_options['feature_scaling'])
    X = pd.concat([train_X,val_X,test_X])
    X_pre = pd.concat([train_X_pre,val_X_pre,test_X_pre])
    return X, X_pre, scaler, columns, model

def split_columns(X, columns):
    """
    Splits the list of feature names into binary features and continuous 
    features.
    This function is called in generate_individual_risks.py.
    
    :param pd.DataFrame X: feature values for students
    :param list columns: list of strings indicating the desired order for 
    column names - read in from pickle
    :returns: list of continuous column names, list of binary column names
    :rtypes: list, list
    """
    binary_features = pd.DataFrame(~X.apply(lambda x: len(x.unique()),\
                                        axis=0).gt(2), columns = ['binary'])
    cts_columns = [c for c in columns if not binary_features['binary'].loc[c]]
    binary_columns = [c for c in columns if binary_features['binary'].loc[c]]
    return cts_columns, binary_columns

def categorical_feature_dict(all_features_path, binary_columns):
    """
    Generates a dictionary mapping binary columns to their appropriate 
    categorical base feature name
    This function is called in generate_individual_risks.py.    

    :param str all_features_path: path from current directory to 
    all_features.yaml in the Features folder
    :param list binary_columns: list of column names for binary features
    :returns: dictionary maping binary columns to their appropriate 
    categorical base feature name
    :rtypes: dict
    """
    with open(all_features_path, 'r') as f:
            all_features = yaml.load(f)
    feature_base = itertools.chain.from_iterable([a  for a in 
                                                  all_features.values()])
    feature_base = [y[:-1] if '*' in y else y for y in feature_base]
    binary_base = set()
    for f in feature_base:
        for b in binary_columns:
            if f in b and 'null' not in b:
                base = []
                flag=False
                if 'gr' in b:
                    for a in b.split('_'):
                        if flag:
                            base.append(a)
                            break
                        base.append(a)
                        if a=='gr':
                            flag=True
                    binary_base.add('_'.join(base))
                else:
                    binary_base.add(f)
    binary_base = list(binary_base)
    binary_dict = {}
    for b in binary_base:
        binary_dict[b] = [f for f in binary_columns if b == f[:len(b)]]
    return binary_dict

def plot_binary_features(model, student, binary_dict, train_X, 
                         save_location=None):
    """
    Generates plots of the effect of each binary or categorical feature
    on a particular student's risk score.

    :param sklearn.estimator model: model object to generate risk scores
    :param int student: student lookup number
    :param dict binary_dict: dictionary mapping categorical variables to their 
        respective indicator variable names, can be drawn from 
        `categorical_feature_dict`
    :param pd.DataFrame train_X: feature matrix with `student` as one of the
        indices
    :param str save_location: optional, if present images will be saved to this
        directory
    :rtype: None
    """
    X_student = train_X.loc[student]
    I = pd.DataFrame(columns = ['delta','direction', 'current_val',\
                                'var_type', 'was_null'], 
                     index=binary_dict.keys())
    base_list = []
    for base, features in binary_dict.items():
        base_list.append(base)
        if len(features)>1: # for categorical
            X = pd.DataFrame(np.tile(X_student,[len(features),1]).transpose(),
                             index=X_student.index) # reset X matrix
            current_val = 'other'
            for i,f in enumerate(features):
                if train_X[f].loc[student]:
                    current_val = f[len(base)+1:]
                for g in features:
                    X[i].loc[g] = 1 if g == f else 0
            if current_val == 'other': # for dropped features
                X[i+1] = X[i]
                for g in features:
                    X[i+1].loc[g] = 0
                current_val_ind = len(features)
                features.append(current_val)
            else:
                current_val_ind = [i for i,f in enumerate(features) 
                                   if current_val in f][0]
            prob = [a[1] for a in model.predict_proba(X.transpose())]
            I['delta'].loc[base] = abs(np.mean([p - prob[current_val_ind] 
                                                 for i, p in enumerate(prob)
                                                if i != current_val_ind ]))
            I['direction'].loc[base] = 'protective' if prob[current_val_ind]\
                                       < np.mean(prob) else 'risky'
            I['current_val'].loc[base] = current_val
            I['var_type'].loc[base] = 'categorical'
            I['was_null'].loc[base] = np.bool('null' in current_val)
            # TODO: order by probability
            fig, ax = plt.subplots()
            plt.scatter( np.arange(len(features)), prob);
            plt.scatter( current_val_ind , prob[current_val_ind], 
                         label=current_val, color = 'red');
            ax.set_xticks( np.arange(len(features)))
            ax.set_xticklabels( [f[len(base)+1:] for f in features], 
                                rotation=90 ) ;
            plt.ylim([0,1])
            plt.title('student {}'.format(student));
            plt.xlabel('{} value'.format(base))
            plt.ylabel('risk score')
            if save_location:
                plt.savefig(os.path.join(save_location, 
                            'student_{0}_{1}'.format(student,base)),
                            bbox_inches='tight')
        else: # for truly binary features
            f= features[0]
            X = pd.DataFrame(np.tile(X_student,[2,1]).transpose(),
                             index=X_student.index) # reset X matrix
            current_val = train_X[f].loc[student]
            X[0].loc[f] = 0 
            X[1].loc[f] = 1 
            prob = [a[1] for a in model.predict_proba(X.transpose())]
            diff = prob[int(current_val)] -  prob[int(not  bool(current_val))]
            I['delta'].loc[base] = abs(diff)
            I['current_val'].loc[base] = current_val
            I['var_type'].loc[base] = 'binary'
            I['was_null'].loc[base] = np.isnan(current_val) 
            if diff > 0:
                I['direction'].loc[base] = 'protective'   
            else:
                I['direction'].loc[base] = 'risky' 
            if plot:
                fig, ax = plt.subplots()
                plt.scatter( [0,1], prob);
                plt.scatter( current_val , prob[int(current_val)], 
                             label=current_val, color = 'red');
                ax.set_xticks([0,1] )
                ax.set_xticklabels( ['False', 'True'], rotation=90 ) ;
                plt.ylim([0,1])
                plt.title('student {}'.format(student));
                plt.xlabel('{} value'.format(base))
                plt.ylabel('risk score')
                if save_location:
                    plt.savefig(os.path.join(save_location, 
                            'student_{0}_{1}'.format(student,base)),
                            bbox_inches='tight')
    return I

def binary_feature_importance(model, student, binary_dict, train_X):
    """
    Calculates the importance of each binary or categorical feature to the 
    risk of a given student.
    Note: calling this function in a loop for all students is very slow,
    it could be sped up by restructuring so all students are run through 
    the model at the same time - see cts_feature_importance for an quick 
    attempt at a similar optimization.
    This function is called in generate_individual_risks.py.

    :param sklearn.estimator model: model object to generate risk scores
    :param int student: student lookup number
    :param dict binary_dict: dictionary mapping categorical variables to their 
        respective indicator variable names, can be drawn from 
        `categorical_feature_dict`
    :param pd.DataFrame train_X: feature matrix with `student` as one of the
        indices
    :returns: all binary/categorical feature importances for each student
    :rtype: list[pd.DataFrame]
    """

    X_student = train_X.loc[student]
    I = pd.DataFrame(columns = ['delta','direction', 'current_val','var_type',
                                'was_null'], index=binary_dict.keys())
    for base, features in binary_dict.items():
        X = pd.DataFrame(np.tile(X_student,[len(features),1]).transpose(),
                         index=X_student.index) 
        if len(features)>1: # for categorical
            # if none of the corresponding binary values are one, 
            # then this student's category was one that didn't appear 
            # in training data
            current_val = 'other' 
            for i,f in enumerate(features):
                if train_X[f].loc[student]:
                    current_val = f[len(base)+1:]
                for g in features:
                    X[i].loc[g] = 1 if g == f else 0
            if current_val == 'other':
                X[i+1] = X[i]
                for g in features:
                    X[i+1].loc[g] = 0
                current_val_ind = len(features)
            else:
                current_val_ind = [i for i,f in enumerate(features) 
                                   if current_val in f][0]
            prob = [a[1] for a in model.predict_proba(X.transpose())]
            I['delta'].loc[base] = abs(np.mean([p - prob[current_val_ind] 
                                                 for i, p in enumerate(prob)
                                                if i != current_val_ind ]))
            # protective if current risk < mean of all possible options
            I['direction'].loc[base] = 'protective' if prob[current_val_ind] <\
                                       np.mean(prob) else 'risky'
            I['current_val'].loc[base] = current_val
            I['var_type'].loc[base] = 'categorical'
            I['was_null'].loc[base] = np.bool('null' in current_val)
        else: # for truly binary features
            f= features[0]
            X = pd.DataFrame(np.tile(X_student,[2,1]).transpose(),\
                             index=X_student.index) # reset X matrix
            current_val = train_X[f].loc[student]
            X[0].loc[f] = 0 
            X[1].loc[f] = 1 
            prob = [a[1] for a in model.predict_proba(X.transpose())]
            diff = prob[int(current_val)] -  prob[int(not  bool(current_val))]
            I['delta'].loc[base] = abs(diff)
            I['current_val'].loc[base] = current_val
            I['var_type'].loc[base] = 'binary'
            I['was_null'].loc[base] = np.isnan(current_val) 
            if diff > 0:
                I['direction'].loc[base] = 'risky' # switching would lower risk
            else:
                I['direction'].loc[base] = 'protective' 
    return I

def plot_cts_features(model, student, cts_columns, train_X_pre, train_X, \
                      scaler, save_location=None):
    """
    Generates plots of the effect of each continuous feature
    on a particular student's risk score.

    :param sklearn.estimator model: model object to generate risk scores
    :param int student: student lookup number
    :param list cts_columns: list of columns names containing cts features
    :param pd.DataFrame train_X_pre: feature matrix prior to imputation 
        and scaling
    :param pd.DataFrame train_X: feature matrix with `student` as one of the
        indices
    :param sklearn.preprocessing.scaler scaler: scaler used to transform 
        train_X_pre into train_X
    :param str save_location: optional, if present images will be saved to this
        directory
    :rtype: None
    """
    X_student = train_X.loc[student]
    n_steps = 100
    for feature in cts_columns:
        current_val = train_X_pre[feature].loc[student]
        if not np.isnan(current_val): # skip null values
            X = pd.DataFrame(np.tile(X_student,[n_steps,1]).transpose(),
                             index=X_student.index) # reset X matrix
            values = np.linspace(min(train_X[feature]), max(train_X[feature]),
                                 n_steps)
            for i,v in enumerate(values):
                X[i].loc[feature] = v
            prob = [a[1] for a in model.predict_proba(X.transpose())]
            values_pre = pd.DataFrame(scaler.inverse_transform(
                X.loc[cts_columns].transpose()).transpose(),
                                      index = cts_columns,
                                      columns = X.columns)
            values_pre = values_pre.loc[feature]
            plt.figure()
            plt.hold='on'
            plt.vlines(current_val,0,1,label=str(current_val))
            plt.plot(values_pre, prob);
            plt.ylim([0,1])
            plt.xlim([min(values_pre)-.1,max(values_pre)+.1])
            plt.title('student {}'.format(student));
            plt.xlabel('{} value'.format(feature))
            plt.ylabel('risk score')
            if save_location:
                plt.savefig(os.path.join(save_location, 
                            'student_{0}_{1}'.format(student,feature)),
                            bbox_inches='tight')

def cts_feature_importance(model, students, cts_columns, train_X_pre, train_X,
                           scaler, shift):
    """
    Generates plots of the effect of each continuous feature
    on a particular student's risk score.
    This function is called in generate_individual_risks.py.

    :param sklearn.estimator model: model object to generate risk scores
    :param list[int] students: list of student lookup numbers
    :param list cts_columns: list of columns names containing cts features
    :param pd.DataFrame train_X_pre: feature matrix prior to imputation 
        and scaling
    :param pd.DataFrame train_X: feature matrix with `students` as a subset 
        of indices
    :param sklearn.preprocessing.scaler scaler: scaler used to transform 
        train_X_pre into train_X
    :param numeric shift: amount to shift the value of the feature, as a
        multiple of a standard deviation
    :returns: all feature cts importances for each student
    :rtype: list[pd.DataFrame]
    """

    train_std = train_X.std(axis=0)
    n_features = len(cts_columns)
    n_students = len(students)
    X = pd.DataFrame(columns = range(3*n_features*n_students),
                     index=train_X.columns)
    I_list = []
    for s_ind, s in enumerate(students):
        X_student = train_X.loc[s]
        X[X.columns[(s_ind*3*n_features):(s_ind*3*n_features+3*n_features)]] =         np.tile(X_student,[3*n_features,1]).transpose()
        for f_ind, feature in enumerate(cts_columns):
            # three steps per student/feature
            current_ind = s_ind*n_features*3+f_ind*3 
            s = shift*train_std[feature]
            X[current_ind].loc[feature] = X[current_ind+1].loc[feature] - s
            X[current_ind+2].loc[feature] = X[current_ind+1].loc[feature] + s
    results = model.predict_proba(X.transpose())
    prob = pd.Series([a[1] for a in results])
    # difference in probability when feature is pushed down
    down = prob.diff().abs().iloc[1::3] 
    # difference in probability when feature is pushed up
    up = prob.diff().abs().iloc[2::3] 
    for s_ind, s in enumerate(students):
        I = pd.DataFrame(columns = ['delta', 'direction', 'current_val',
                                    'var_type','was_null'],index=cts_columns)
        for f_ind, feature in enumerate(cts_columns):
            current_ind = s_ind*n_features+f_ind # one step per student/feature
            I['delta'].loc[feature] = max(up.iloc[current_ind], 
                                          down.iloc[current_ind])
            prob_current = prob.iloc[current_ind*3+1]
            if down.iloc[current_ind] > up.iloc[current_ind]:
                prob_shift = prob.iloc[current_ind*3]  
            else: 
                prob_shift = prob.iloc[current_ind*3+2]
            if prob_current < prob_shift:
                # feature is lessening to student's risk
                I['direction'].loc[feature] = 'protective' 
            else:
                # feature is raising student's risk
                I['direction'].loc[feature] = 'risky'
            I['current_val'].loc[feature] = X[current_ind*3+1].loc[feature]
            I['was_null'].loc[feature] = np.isnan(train_X_pre[feature].loc[s])
        I['var_type'] = 'continuous'
        I_list.append(I)
    return I_list

def plot_features(model_filename, student, all_features_path, 
                  save_location=None): 
    """
    Generates plots of the effect of each feature
    on a particular student's risk score.

    :param str model_filename: identifier of model object saved as a pkl
    :param int student: student lookup number
    :param str all_feature_path: path to all_features.yaml (in Features dir)
    :param str save_location: optional, if present images will be saved to this
        directory
    :rtype: None
    """
    X, X_pre, scaler, column_order, model = read_and_preprocess(filename)
    cts_columns, binary_columns = split_columns(X, column_order)
    binary_dict = categorical_feature_dict(all_features_path, binary_columns)
    x,y,current, current_prob = plot_cts_features(model, student, cts_columns,
                                                  X_pre, X, scaler,
                                                  save_location)
    plot_binary_features(model, student, binary_dict, X, save_location)
    return x,y,current, current_prob

def get_feature_importances(model_filename, students, 
                            all_features_path, shift):
    """
    Calculates the effect of each feature on a particular student's risk score.
    Note: this is very slow, see binary_feature_importance doc string for
    suggestions for possible optimization

    :param str model_filename: identifier of model object saved as a pkl
    :param list[int] students: list of student lookup numbers
    :param str all_feature_path: path to all_features.yaml (in Features dir)
    :param numeric shift: amount to shift the value of the feature, as a
        multiple of a standard deviation
    :returns: all feature importances for each student
    :rtype: list[pd.DataFrame]
    """
    X, X_pre, scaler, column_order, model = read_and_preprocess(filename)
    cts_columns, binary_columns = split_columns(X, column_order)
    binary_dict = categorical_feature_dict(all_features_path, binary_columns)
    I_cts = cts_feature_importance(model, students, cts_columns, X_pre, X, 
                                   scaler, shift)
    I_binary = []
    for student in students:
        temp = binary_feature_importance(model, student, binary_dict, X)
        I_binary.append(temp)
    I_all = [pd.concat([c,b]) for c,b in zip(I_cts, I_binary)]
    return I_all

def build_top_k_df(I_all, students, k):
    """
    Builds a datafame with the top k risk factors and their direction and 
    current value for each student

    Note: ordering of students list must match ordering of I_all list
    If `students` was used as input to get_feature_importances, this holds true
    
    This function is called in generate_individual_risks.py.

    :param list[pd.DataFrame] I_all: list of individual feature importance 
        dataframes, one for each student
    :param list[int] students: list of student_lookup numbers
    :param int k: number of risk factors returned
    :returns: dataframe indexed by `students` with top k risk factors
    :rtype: pd.DataFrame
    """
    columns = []
    for i in range(k):
        columns.append('risk_factor_{}'.format(i+1))
        columns.append('risk_factor_{}_value'.format(i+1))
        columns.append('risk_factor_{}_direction'.format(i+1))
    top_k = pd.DataFrame(columns=columns, index=students)
    for i, s in enumerate(students):
        top = I_all[i][np.logical_not(I_all[i]['was_null'])]\
                .sort_values('delta', ascending=False).head(3)
        for j in range(3):
            top_k.loc[s,'risk_factor_{}'.format(j+1)] = top.index[j]
            top_k.loc[s,'risk_factor_{}_value'.format(j+1)] = \
                    top['current_val'].iloc[j]
            top_k.loc[s,'risk_factor_{}_direction'.format(j+1)] = \
                    top['direction'].iloc[j]
    return top_k

def top_3(filename, students):
    """
    Returns a dataframe with the top 3 risk factors/values/directions

    :param str filename: identifier for a model saved as a pkl
    :param list[int] students: list of student_lookup numbers
    :returns: dataframe with the top 3 risk factors/values/directions 
    :rtype: pd.DataFrame
    """

    all_features_path = os.path.join(base_pathname, 
                                     'Features/all_features.yaml')
    with Timer('feature importances'):
        all_I = get_feature_importances(filename, students, 
                                        all_features_path, 1)
    top_3 = build_top_k_df(all_I, students, 3)
    return top_3

def population_top_k(all_I,k):
    # TODO: make this so null features get something sensible for 
    # averaging/sorting
    I = pd.DataFrame(all_I[0]['delta'], index=all_I[0].index)
    for i, I_next in enumerate(all_I[1:]):
        I_temp = pd.DataFrame(I_next['delta'], index=I_next.index)
        I_temp.columns = [i]
        I = I.join(I_temp, how='outer')
    pop = pd.DataFrame(I.mean(axis=1), columns=['mean_delta'])
    return pop.sort_values('mean_delta', ascending = False).head(k)


def main():
    
    filename = '08_17_2016_grade_10_param_set_16_RF_jg_139'
    train_students, val_students, test_students = student_list(filename)
    students = val_students[:10]
    print(top_3(filename, students))

    # one-off plot for poster
    # plt.figure()
    # plt.hold='on'
    # plt.plot(x, y, color='k');
    # plt.plot(current,current_prob,'or',label='current value', markersize=10)
    
    # plt.ylim([.5,.9])
    # plt.xlim([min(x),max(x)])
    # #plt.title('student {}'.format(student));
    # plt.legend(numpoints=1)
    # plt.xlabel('8th grade Math OAA (normalized)', size=18)
    # plt.ylabel('risk score',size=18)
    # plt.savefig(os.join(base_pathname, 'Error_Feature_Analysis',
    #                     'RF_feature_plots',
    #                     'student_{0}_{1}_clean'\
    #                     .format(student,'math_normalized_gr_8')),
    #             bbox_inches='tight')

if __name__=='__main__':
    main()
