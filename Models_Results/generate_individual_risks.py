import os, sys, json
pathname = os.path.dirname(sys.argv[0])
full_pathname = os.path.abspath(pathname)
split_pathname = full_pathname.split(sep="mvesc")
base_pathname = os.path.join(split_pathname[0], "mvesc")
parentdir = os.path.join(base_pathname, "ETL")
sys.path.insert(0, parentdir)
from mvesc_utility_functions import *
import pickle
from estimate_prediction_model import *
from make_predictions_for_unlabeled_students import \
    test_impute_and_scale, read_in_model
from RF_feature_scores import build_top_k_df, cts_feature_importance, \
    binary_feature_importance, split_columns, categorical_feature_dict
import pandas as pd
import numpy as np
import pdb
# global constants
threshold_percentiles = [0.95, 0.85, 0.70]
risk_levels = ['High', 'Medium', 'Low', 'Safe']

"""
Generate individual Risk Scores and Factors
"""
def topK_features_logit(model, data, feature_names, topK=3):
    """ 
    Find the top k features in logistic regression for a single observation

    :param sklearn.object model: a LogisticRegression() model
    :param 1D np.array data: data of one student's all feature data in 
        the correct sequence
    :param list[str] feature_names: a list of feature names
    :param int topK: number of top features to return
    :return list[str], list[str]: list of topK features names, 
        list of corresponding directions ('protective' or 'risky')
    :rtype list of str:
    """
    importances = np.transpose(model.coef_)[:, 0]*data
    indices = np.absolute(importances).argsort()
    indices = indices[::-1]
    direction = ['risky' if i>0 else 'protective' 
                 for i in importances[indices]]
    return list(np.array(feature_names)[indices[:topK]]), direction[:topK]

def risk_score2level(score, percentiles, risk_levels):
    """ 
    Find risk levels based on risk score and threshold
    
    :param float score: risk score/probability; e.g. 0.862
    :parma percentiles: threshold scores for risk levels, 
        e.g. [0.9552, 0.8977, 0.7821]
    :param risk_levels: risk levels top to bottom, 
        e.g. ['High', 'Medium', 'Low', 'Safe']
    """
    ind = (percentiles>score).sum()
    return(risk_levels[ind])

def get_school_district(df, grade, year=2015):
    """ 
    Add school, district information to the table and return only current 
    student at a grade. School and district information are taken from the 
    most recent appearance of that student in the given grade and year, based 
    on district admit dates (this information is not perfect - about 10% of 
    values are missing, and this date corresponds to their first time in the 
    district, so if a student switches between two districts multiple times
    we cannot tell definitively which was most recent)
    
    :param pd.dataframe df: data frame with at least student lookups
    :param int grade: the only grade to return
    :param int year: school year
    :return pd.dataframe df: inner joined dataframe with only current grade 
        at the year 
    """
    with postgres_pgconnection_generator() as conn:
        with conn.cursor() as cursor:
            select_current_grade = """
            select distinct on(student_lookup, grade)
            student_lookup, grade, school_year, school_code, district
            from clean.all_snapshots
            where grade={g} and school_year={yr}
            order by student_lookup, grade, district_admit_date desc
            """.format(g=grade-1, yr=year)
            df_school_etc = pd.read_sql_query(select_current_grade, conn)
    return df.merge(df_school_etc, on='student_lookup', how='inner')

def colnames_mathing_processed2raw(processed_column_names, raw_column_names):
    """
    Create a dict to map processed feature column names to raw feature 
    column names
    
    :param list/set processed_column_names: processed column names
    :param list/set raw_column_names: raw column names
    :return dict matching: a dictionary with keys of processed names and 
        values of raw names
    :rtype python dictionary
    """
    matching = {}
    processed_column_names = set(processed_column_names)
    raw_column_names = set(raw_column_names)
    gender, ethnicity = 'gender', 'ethnicity'  # static columns with no grade
    for c in processed_column_names:
        if c in raw_column_names:
            matching[c] = c
        elif gender in c or ethnicity in c:
            matching[c] = c.split('_')[0]
        else:
            parts = c.split('_gr_')
            matching[c] = parts[0]+'_gr_'+ parts[1].split('_')[0]
    return(matching)    

def build_individual_risk_df(clf, topK, grade, features_processed, 
                             features_raw, scaler, options, 
                             model_name, filename):
    """
    Build individual risk score, factors data frame

    :parma sklearn.clf clf: model trained
    :param int topK: number of top features to report
    :param pd.df feature_processed: processed feature data frame
    :parma pd.df feature_raw: raw feature data frame
    :param str model_name: type of model
    :param str filename: file where model is saved (identifier for db)
    :return pd.df individual_risk: data frame of individual risk info
    :rtype pd.df
    """
    # create mapping of processed colnames and raw ones
    colnames_processed2raw = colnames_mathing_processed2raw(
        features_processed.columns, features_raw.columns)

    # predict and find top factors
    if hasattr(clf, "predict_proba"):
        risk_probas = clf.predict_proba(features_processed)[:,1]
    else:
        risk_probas = clf.decision_function(features_processed)

    # set up dataframe
    individual_scores_factors = pd.DataFrame()
    individual_scores_factors['student_lookup'] = features_raw.index

    # assign risk score & levels
    individual_scores_factors['risk_score'] =  risk_probas
    percentiles = individual_scores_factors.risk_score\
                                           .quantile(q=threshold_percentiles)
    student_risk_levels = [risk_score2level(s, percentiles, risk_levels) 
                           for s in individual_scores_factors.risk_score]
    individual_scores_factors['risk_level'] = student_risk_levels

    # individual risk factors - process different for logit or other models
    if model_name == 'logit':
        top_individual_features = []
        top_individual_directions = []
        for i in range(features_processed.shape[0]):
            x = np.array(features_processed.iloc[i, :])
            top_features, top_feature_directions = topK_features_logit(clf, x, 
                                                    features_processed.columns,
                                                    topK=topK)
            top_feature_names_raw = [colnames_processed2raw[c] for c in 
                                     top_features]
            top_individual_features.append(top_feature_names_raw)
            top_individual_directions.append(top_feature_directions)
        top_risk_factor_names = ['risk_factor_'+str(i) 
                                 for i in range(1, topK+1)]
        top_directions = ['risk_factor_'+str(i)+'_direction'
                          for i in range(1, topK+1)]
        top_individual_features = pd.DataFrame(top_individual_features, 
                                               columns=top_risk_factor_names)
        top_individual_features = pd.concat([top_individual_features, 
                                             pd.DataFrame(
                                                 top_individual_directions, 
                                                 columns = top_directions)], 
                                            axis=1)
                                                        
        individual_scores_factors = pd.concat([individual_scores_factors, 
                                               top_individual_features],axis=1)
        top_feature_values = {'risk_factor_'+str(i):[] for i 
                              in range(1, topK+1)}
        for risk_i in top_feature_values:
            for student_i in range(features_processed.shape[0]):
                column_in_features_raw = individual_scores_factors.ix\
                                         [student_i, risk_i]
                top_feature_values[risk_i].append(str(
                    features_raw[column_in_features_raw].iloc[student_i]))
        top_feature_values = pd.DataFrame(top_feature_values)
        top_feature_values = top_feature_values.rename(
            columns={x:x+'_value' for x in top_feature_values.columns})
        individual_scores_factors = pd.concat([individual_scores_factors,
                                               top_feature_values], axis=1)
    else:
        cts_columns, binary_columns = split_columns(features_processed, 
                                            options['estimator_features'])
        binary_dict = categorical_feature_dict(os.path.join(base_pathname, 
                                            'Features/all_features.yaml'),
                                            binary_columns)
        students = individual_scores_factors['student_lookup']
        with Timer('cts_features for grade {}'.format(grade)):
            I_cts = cts_feature_importance(clf, students, cts_columns, 
                                           features_raw, features_processed,
                                           scaler, 1)
        I_binary = []
        with Timer('binary_features') as t:
            for count, student in enumerate(students):
                temp = binary_feature_importance(clf, student, binary_dict, 
                                                 features_processed)
                I_binary.append(temp)
                print('student {0}/{1} for grade {2}, {3} sec'.format(count,
                                len(students), grade, t.time_check()))
        I_all = [pd.concat([c,b]) for c,b in zip(I_cts, I_binary)]
        top_k_df = build_top_k_df(I_all, students, 3)
        individual_scores_factors = individual_scores_factors.merge(
            top_k_df, left_on = 'student_lookup', right_index=True)
        individual_scores_factors = reorder_columns(individual_scores_factors,
                                                    topK)


    # subset the data to only include current students and current grade
    individual_scores_factors = get_school_district(individual_scores_factors,
                                                    grade)

    # model and its file name
    individual_scores_factors['model'] = model_name
    individual_scores_factors['model_file'] = filename
    if model_name == 'logit':
        individual_scores_factors = reorder_columns(individual_scores_factors,
                                                    topK)
    individual_scores_factors.sort_values(by=['district', 'school_code', 
                                              'risk_score'],
                                          inplace=True, ascending=False)
    return individual_scores_factors


def reorder_columns(df, topK):
    """ 
    Reorder columns names for readability

    :param pd.df: dataframe of individual scores
    :param int topK: int of topK feautres
    :return pd.df df: dataframe of new ordered df
    :rtype pd.df
    """
    new_colnames = ['student_lookup','grade', 'school_year', 'school_code', 
                    'district', 'risk_score', 'risk_level']
    model_names = ['model', 'model_file']
    risk_names = []
    for i in range(1, topK+1):
        risk_names = risk_names+['risk_factor_'+str(i), 
                                 'risk_factor_'+str(i)+'_value',
                                 'risk_factor_{}_direction'.format(i)]
    new_colnames = new_colnames + risk_names + model_names
    return df[new_colnames]


def generate_csv4mvesc(table = 'individual_risks_logit', 
                       csvfile = 'current_student_predictions_logit.csv'):
    """
    Generate and save a csv file of current student predictions

    :param str table: table name
    :param str csvfile: csvfile name
    :return None:
    """
    ### Generate a CSV for our partner
    schema = 'model'
    sql_select = """
    select student_lookup, grade, school_year, school_code, district,
    round(risk_score::numeric, 3) as risk_score, risk_level, 
    risk_factor_1, risk_factor_1_value, risk_factor_1_direction, 
    risk_factor_2, risk_factor_2_value, risk_factor_2_direction,
    risk_factor_3, risk_factor_3_value, risk_factor_3_direction
    from {s}."{t}"
    order by grade, district, school_code, risk_score desc;
    """.format(s=schema, t=table)
    with postgres_pgconnection_generator() as conn:
        df = pd.read_sql_query(sql_select, conn)
    df.to_csv(csvfile, index=False)


def main():
    parser = OptionParser()
    parser.add_option('-t','--topK', dest='topK',
                      help="topK features to retrieve", type="int", default=3)
    parser.add_option('-m','--model', dest='model', type="choice",
                      choices = ['logit','RF'],
                      help= 'gets predictions from best models of given type')
    parser.add_option('-f','--filename', dest='filename_list',
        help="filename for model to generate predictions",
                      action="append")
    parser.add_option('-d','--pkl_dir', dest='pkl_dir',
                      help="path to directory where pkl files are saved",
                      default = '/mnt/data/mvesc/Models_Results/pkls')

    (options, args) = parser.parse_args()

    logit_list = ['08_17_2016_grade_6_param_set_8_logit_jg_97',
                  '08_17_2016_grade_7_param_set_17_logit_jg_98',
                  '08_17_2016_grade_8_param_set_16_logit_jg_111',
                  '08_17_2016_grade_9_param_set_16_logit_jg_111',
                  '08_17_2016_grade_10_param_set_22_logit_jg_122']

    RF_list = ['08_17_2016_grade_6_param_set_8_RF_jg_155',
               '08_17_2016_grade_7_param_set_17_RF_jg_138',
               '08_17_2016_grade_8_param_set_16_RF_jg_144',
               '08_17_2016_grade_9_param_set_16_RF_jg_179',
               '08_17_2016_grade_10_param_set_16_RF_jg_151']

    if not options.model and not options.filename_list:
        parser.error('no file names provided: either provide a list with -f or'
                     'select logit or RF with -m')

    if options.model and options.filename_list:
        parser.error('cannot set both model type and explicit file list')

    if options.model == 'logit':
        filename_list = logit_list
    elif options.model == 'RF':
        filename_list = RF_list
    else:
        filename_list = options.filename_list
    topK = int(options.topK)        
    dir_pkls = options.pkl_dir

    if_exists = 'append'
    with open(os.path.join(base_pathname,'Models_Results', 
                           'feature_name_mapping_to_human_readable.json'),
                           'r') as f:
       names_mapping = json.load(f)

    for filename in filename_list:
        print("- Processing pkl: ", filename)

        # load saved model
        model_name = filename.split('_')[-3]
        clf, options = read_in_model(filename, model_name)
        grade = options['prediction_grade_level']
        
        # fetch and process feature data
        features_processed, features_raw = build_test_feature_set(options,
                                        current_year=2016, return_raw=True)
        features_processed, scaler = test_impute_and_scale(features_processed, 
                                                      options)
        individual_scores_factors = build_individual_risk_df(clf, topK, grade, 
                                    features_processed, features_raw, 
                                    scaler, options, model_name, filename)
        
        schema, table = 'model', 'individual_risks_{}'.format(model_name)
        
        # mapping feature names to human-readable names
        colnames = list(individual_scores_factors.columns)
        risk_factor_colnames = list(filter(lambda x: ('risk_factor' in x) 
                                           and ('value' not in x) 
                                           and ('direction' not in x),
                                           colnames))
        risk_factor_column_indice = [colnames.index(x) for x 
                                     in risk_factor_colnames]
        for i in range(individual_scores_factors.shape[0]):
            for colind in risk_factor_column_indice:
                individual_scores_factors.iloc[i, colind] = names_mapping[
                    individual_scores_factors.iloc[i, colind]]

        # output to postgres
        eng = postgres_engine_generator()
        individual_scores_factors.to_sql(table, eng, schema = schema, 
                                         if_exists=if_exists, index=False)
        print('- Processed ', filename)

    csvfile = 'current_student_predictions_{}.csv'.format(model_name)
    generate_csv4mvesc(table, csvfile)
    print("- current student predictions saved to", csvfile )

if __name__=='__main__':
    main()
