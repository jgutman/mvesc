import os, sys
pathname = os.path.dirname(sys.argv[0])
full_pathname = os.path.abspath(pathname)
split_pathname = full_pathname.split(sep="mvesc")
base_pathname = os.path.join(split_pathname[0], "mvesc")
parentdir = os.path.join(base_pathname, "ETL")
sys.path.insert(0, parentdir)
from mvesc_utility_functions import *
import pickle
from estimate_prediction_model import *
import pandas as pd
import numpy as np


def read_in_model(filename, model_name,
        pkl_dir = '/mnt/data/mvesc/Models_Results/pkls'):
    full_filename = filename +'_' + model_name + '.pkl'
    with open(os.path.join(pkl_dir, full_filename), 'rb') as model:
        model_pkl = pickle.load(model)
    clf, options = model_pkl['estimator'], model_pkl['model_options']
    grade = int(model_pkl['model_options']['cohort_grade_level_begin'].split('_')[-1][:-2])
    return clf, options, grade

def build_test_feature_set(options, current_year = 2016):
    # get student list of 2016 students in specified cohort grade level
    with postgres_pgconnection_generator() as connection:
        cohort = options['cohort_grade_level_begin']
        test_outcomes = read_table_to_df(connection,
            table_name = 'outcome', schema = 'model', nrows = -1,
            columns = ['student_lookup', 'current_students', cohort])
        test_outcomes.dropna(subset=['current_students', cohort], inplace=True)
        test_outcomes = pd.DataFrame(test_outcomes.student_lookup[
            test_outcomes[cohort] == current_year])

        for table, column_names in options['features_included'].items():
            features = read_table_to_df(connection, table_name = table,
                schema = 'model', nrows = -1,
                columns=(['student_lookup'] + column_names))
            # join to only keep features for current_students
            test_outcomes = pd.merge(test_outcomes, features,
                how = 'left', on = 'student_lookup')

    # build dataframe containing student_lookup
    # and all features as numeric non-categorical values
    test_outcomes.set_index('student_lookup', inplace=True)
    test_outcomes_raw = test_outcomes
    test_outcomes = df2num(test_outcomes_raw, drop_reference = False,
        dummify = True, drop_entirely_null = False)
    return test_outcomes_raw, test_outcomes

def test_impute_and_scale(test_outcomes, options):
    all_past_data = build_outcomes_plus_features(options)
    train, val, val = temporal_cohort_test_split(all_past_data,
            options['cohort_grade_level_begin'],
            options['cohorts_test'], options['cohorts_val'],
            options['cohorts_training'])
    exclude = set((options['outcome_name'],
                options['cohort_grade_level_begin']))
    train = train.drop([options['outcome_name'],
            options['cohort_grade_level_begin']],axis=1)
    val = val.drop([options['outcome_name'],
            options['cohort_grade_level_begin']],axis=1)

    category_missing = [col for col in train.columns if
                    col not in test_outcomes.columns]
    for col in category_missing:
        test_outcomes[col] = 0
    test_outcomes = test_outcomes.filter(train.columns)

    # imputation for missing values in features
    train, val, test_outcomes = impute_missing_values(train, val, test_outcomes,
        options['missing_impute_strategy'])

    # feature scaling
    train, val, test_outcomes = scale_features(train, val, test_outcomes,
        options['feature_scaling'])

    assert (all(train.columns == test_outcomes.columns)),\
        "train and current_students have different columns"
    return test_outcomes

def make_and_save_predictions(future_predictions, clf, filename):
    # generate soft predictions
    if hasattr(clf, "predict_proba"):
        future_set_scores = clf.predict_proba(future_predictions)[:,1]
    else:
        future_set_scores = clf.decision_function(future_predictions)

    saved_outputs = {
        'file_name' : filename,
        'future_index' : future_predictions.index,
        'future_scores' : future_set_scores,
        'future_preds' : clf.predict(future_predictions)
    }
    #write_scores_to_db(saved_outputs, importance_scores = False)
    return(saved_outputs)

def topK_features_logit(model, data, feature_names, topK=3):
    importances = np.transpose(model.coef_)[:, 0]*data
    indices = importances.argsort()
    indices = indices[::-1]
    #print(indices[:3])
    return(list(np.array(feature_names)[indices[:topK]]))

def risk_score2level(score, percentiles, risk_levels):
    ind = (percentiles>score).sum()
    return(risk_levels[ind])

def get_school_district(df, grade, year=2015):
    with postgres_pgconnection_generator() as conn:
        with conn.cursor() as cursor:
            select_current_grade = """
            select student_lookup, grade, school_year, school_code, district
            from clean.all_snapshots
            where grade={g} and school_year={yr}
            """.format(g=grade-1, yr=2015)
            df_school_etc = pd.read_sql_query(select_current_grade, conn)
    return df.merge(df_school_etc, on='student_lookup')

def main():
    filename_list = ['08_12_2016_grade_6_param_set_8_logit_ht_16587', 
                     '08_12_2016_grade_7_param_set_17_logit_ht_19082', 
                     '08_12_2016_grade_8_param_set_16_logit_ht_19857', 
                     '08_12_2016_grade_9_param_set_22_logit_ht_22737',
                     '08_12_2016_grade_10_param_set_22_logit_ht_23459']
    topK = 3
    schema, table = 'model', 'individual_risk_scores_factors'
    dir_pkls = '/mnt/data/mvesc/Models_Results/pkls'
    if_exists = 'append'
    random_seed = 62571

    #if options.filename_list:
    #    filename_list = options.filename_list

    for filename in filename_list:
        # load saved model
        print("- Processing pkl: ", filename)
        model_name = filename.split('_')[-3]
        clf, options, grade = read_in_model(filename, model_name)

        # fetch and process feature data
        features_raw, feaures_num = build_test_feature_set(options)
        features_processed = test_impute_and_scale(feaures_num, options)

        # predict and find top factors
        risk_probas = clf.predict_proba(features_processed)[:,1]
        predictions = clf.predict(features_processed)
        top_individual_features = []
        for i in range(features_processed.shape[0]):
            x = np.array(features_processed.iloc[i, :])
            top_individual_features.append(topK_features_logit(clf, x, features_processed.columns, topK=topK))

        top_risk_factor_names = ['risk_factor_'+str(i) for i in range(1, topK+1)]
        top_individual_features = pd.DataFrame(top_individual_features, 
                                               columns=top_risk_factor_names)

        # individual risk score, level & factors
        individual_scores_factors = pd.DataFrame()
        individual_scores_factors['student_lookup'] = features_raw.index

        # assign risk score & levels
        individual_scores_factors['risk_score'] =  risk_probas
        percentiles = individual_scores_factors.risk_score.quantile(q=[0.95, 0.85, 0.70])
        risk_levels = ['High', 'Medium', 'Low', 'Safe']
        student_risk_levels = [risk_score2level(s, percentiles, risk_levels) for s in individual_scores_factors.risk_score]
        individual_scores_factors['risk_level'] = student_risk_levels
        individual_scores_factors = pd.concat([individual_scores_factors, top_individual_features], axis=1)

        top_feature_values = {'risk_factor_'+str(i):[] for i in range(1, topK+1)}
        for risk_i in top_feature_values:
            for student_i in range(features_processed.shape[0]):
                column_in_features_processed = individual_scores_factors.ix[student_i, risk_i]
                top_feature_values[risk_i].append(features_processed[column_in_features_processed].iloc[student_i])
        top_feature_values = pd.DataFrame(top_feature_values)
        top_feature_values = top_feature_values.rename(columns={x:x+'_value' for x in top_feature_values.columns})
        individual_scores_factors = pd.concat([individual_scores_factors, top_feature_values], axis=1)

        # subset the data to only include current students and corrent grades
        individual_scores_factors = get_school_district(individual_scores_factors, grade)

        # model and its file name
        individual_scores_factors['model'] = model_name
        individual_scores_factors['model_file'] = filename
        individual_scores_factors.sort_values(by=['risk_score'],inplace=True, ascending=False)


        # output to postgres
        eng = postgres_engine_generator()
        individual_scores_factors.to_sql(table, eng, schema = schema, if_exists=if_exists, index=False)
        print('- Processed ', filename)

if __name__=='__main__':
    main()
