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
from make_predictions_for_unlabeled_students import *
from RF_feature_scores import top_k
import pandas as pd
import numpy as np
# global constants
threshold_percentiles = [0.95, 0.85, 0.70]
risk_levels = ['High', 'Medium', 'Low', 'Safe']

"""
Generate individual Risk Scores and Factors
"""
def topK_features_logit(model, data, feature_names, topK=3):
    """ 
    Find topK features in logistic regression for a single observation
    We may generate similar functions for other methods
    :param sklearn.object model: model; it should be LogisticRegression()
    :param 1D np.array data: data of one student's all feature data in the right sequence
    :param list[str] feature_names: a list of feature names
    :param int topK: number of top features to return
    :return list[str]: list of topK features names
    :rtype list of str:
    """
    importances = np.transpose(model.coef_)[:, 0]*data
    indices = importances.argsort()
    indices = indices[::-1]
    return(list(np.array(feature_names)[indices[:topK]]))

def risk_score2level(score, percentiles, risk_levels):
    """ 
    Find risk levels based on risk score and threshold
    :param float score: risk score/probability; e.g. 0.862
    :parma percentiles: threshold scores for risk levels, e.g. [0.9552, 0.8977, 0.7821]
    :param risk_levels: risk levels top to bottom, e.g. ['High', 'Medium', 'Low', 'Safe']
    """
    ind = (percentiles>score).sum()
    return(risk_levels[ind])

def get_school_district(df, grade, year=2015):
    """ 
    Add school, district information to the table and return only current student at a grade
    :param pd.dataframe df: data frame with at least student lookups
    :param int grade: the only grade to return
    :param int year: school year
    :return pd.dataframe df: inner joined dataframe with only current grade at the year 
    """
    with postgres_pgconnection_generator() as conn:
        with conn.cursor() as cursor:
            select_current_grade = """
            select student_lookup, grade, school_year, school_code, district
            from clean.all_snapshots
            where grade={g} and school_year={yr}
            """.format(g=grade-1, yr=2015)
            df_school_etc = pd.read_sql_query(select_current_grade, conn)
    return df.merge(df_school_etc, on='student_lookup')

def colnames_mathing_processed2raw(processed_column_names, raw_column_names):
    """
    Create a dict to map processed feature column names to raw feature column names
    :param list/set processed_column_names: processed column names in a list or set
    :param list/set raw_column_names: raw column names in a list or set
    :return dict matching: a dictionary with keys of processed names and values of raw names
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

    

def build_individual_risk_df(clf, topK, grade, features_processed, features_raw, model_name, filename):
    """
    Build individual risk score, factors data frame
    :parma sklearn.clf clf: model trained
    :param pd.df feature_processed: processed feature data frame
    :parma pd.df feature_raw: raw feature data frame
    :return pd.df individual_risk: data frame of individual risk info
    :rtype pd.df
    """
    # create mapping of processed colnames and raw ones
    colnames_processed2raw = colnames_mathing_processed2raw(features_processed.columns, 
                                                                         features_raw.columns)
    # predict and find top factors
    if hasattr(clf, "predict_proba"):
        risk_probas = clf.predict_proba(features_processed)[:,1]
    else:
        risk_probas = clf.decision_function(features_processed)

    top_individual_features = []
    for i in range(features_processed.shape[0]):
        x = np.array(features_processed.iloc[i, :])
        top_feature_names_raw = [colnames_processed2raw[c] for c in topK_features_logit(clf, x, features_processed.columns, topK=topK)]
        top_individual_features.append(top_feature_names_raw)
    top_risk_factor_names = ['risk_factor_'+str(i) for i in range(1, topK+1)]
    top_individual_features = pd.DataFrame(top_individual_features, 
                                           columns=top_risk_factor_names)

    # individual risk score, level & factors
    individual_scores_factors = pd.DataFrame()
    individual_scores_factors['student_lookup'] = features_raw.index

    # assign risk score & levels
    individual_scores_factors['risk_score'] =  risk_probas
    percentiles = individual_scores_factors.risk_score.quantile(q=threshold_percentiles)
    student_risk_levels = [risk_score2level(s, percentiles, risk_levels) for s in individual_scores_factors.risk_score]
    individual_scores_factors['risk_level'] = student_risk_levels
    individual_scores_factors = pd.concat([individual_scores_factors, top_individual_features], axis=1)

    # get top risk values
    top_feature_values = {'risk_factor_'+str(i):[] for i in range(1, topK+1)}
    for risk_i in top_feature_values:
        for student_i in range(features_processed.shape[0]):
            column_in_features_raw = individual_scores_factors.ix[student_i, risk_i]
            top_feature_values[risk_i].append(str(features_raw[column_in_features_raw].iloc[student_i]))
    top_feature_values = pd.DataFrame(top_feature_values)
    top_feature_values = top_feature_values.rename(columns={x:x+'_value' for x in top_feature_values.columns})
    individual_scores_factors = pd.concat([individual_scores_factors, top_feature_values], axis=1)
    
    # subset the data to only include current students and corrent grades
    individual_scores_factors = get_school_district(individual_scores_factors, grade)

    # model and its file name
    individual_scores_factors['model'] = model_name
    individual_scores_factors['model_file'] = filename
    individual_scores_factors = reorder_columns(individual_scores_factors, topK)
    individual_scores_factors.sort_values(by=['district', 'school_code', 'risk_score'],inplace=True, ascending=False)
    return individual_scores_factors

def reorder_columns(df, topK):
    """ Reorder columns names for readable
    :param pd.df: dataframe of individual scores
    :param int topK: int of topK feautres
    :return pd.df df: dataframe of new ordered df
    :rtype pd.df
    """
    new_colnames = ['student_lookup','grade', 'school_year', 'school_code', 'district', 'risk_score', 'risk_level']
    model_names = ['model', 'model_file']
    risk_names = []
    for i in range(1, topK+1):
        risk_names = risk_names+['risk_factor_'+str(i), 'risk_factor_'+str(i)+'_value']
    new_colnames = new_colnames + risk_names + model_names
    return df[new_colnames]


def generate_csv4mvesc(table = 'individual_risks_logit', csvfile = 'current_student_predictions_logit.csv'):
    """
    Generate and save a csv file of current student predictions
    :param str table: table name
    :param str csvfile: csvfile name
    :return None:
    """
    ### Generate a CSV for our partner
    schema = 'model'
    csvfile = 'current_student_predictions_logit.csv'
    with postgres_pgconnection_generator() as conn:
        with conn.cursor() as cursor:
            sql_select = """
            select student_lookup, grade, school_year, school_code, district,
            round(risk_score::numeric, 3) as risk_score, risk_level, risk_factor_1,risk_factor_1_value,  
            risk_factor_2, risk_factor_2_value, risk_factor_3, risk_factor_3_value
            from {s}.{t}
            order by grade, district, school_code, risk_score desc;
            """.format(s=schema, t=table)
            df = pd.read_sql_query(sql_select, conn)

    df.to_csv(csvfile, index=False)


def main():
    parser = OptionParser()
    parser.add_option('-t','--topK', dest='topK',
        help="topK features to retrieve", type="int")
    parser.add_option('-f','--filename', dest='filename_list',
        help="filename for model to generate predictions",
        action="append")
    (options, args) = parser.parse_args()

    filename_list = ['08_17_2016_grade_6_param_set_8_logit_jg_97',
                     '08_17_2016_grade_7_param_set_17_logit_jg_98',
                     '08_17_2016_grade_8_param_set_16_logit_jg_111',
                     '08_17_2016_grade_9_param_set_16_logit_jg_111',
                     '08_17_2016_grade_10_param_set_22_logit_jg_122']
    if options.filename_list:
        filename_list = options.filename_list
    topK = 3
    if options.topK:
        topK = int(options.topK)
        
    schema, table = 'model', 'individual_risks_logit'
    dir_pkls = '/mnt/data/mvesc/Models_Results/pkls'
    if_exists = 'append'
    with open('feature_name_mapping_to_human_readable.json', 'r') as f:
       names_mapping = json.load(f)

    for filename in filename_list:
        print("- Processing pkl: ", filename)

        # load saved model
        if 'logit' in filename.split('_'):
            model_name = 'logit'
            clf, options = read_in_model(filename, model_name)
            grade = options['prediction_grade_level']
            
            # fetch and process feature data
            features_processed, features_raw = build_test_feature_set(options, current_year=2016, return_raw=True)
            features_processed = test_impute_and_scale(features_processed, options)
            individual_scores_factors = build_individual_risk_df(clf, topK, grade, 
                                                                 features_processed, features_raw, model_name, 
                                                                 filename)
        else:
            individual_scores_factors = top_k(filename, students)

        # mapping feature names to human-readable names
        colnames = list(individual_scores_factors.columns)
        risk_factor_colnames = list(filter(lambda x: ('risk_factor' in x) and ('value' not in x), colnames))
        risk_factor_column_indice = [colnames.index(x) for x in risk_factor_colnames]
        for i in range(individual_scores_factors.shape[0]):
            for colind in risk_factor_column_indice:
                individual_scores_factors.iloc[i, colind] = names_mapping[individual_scores_factors.iloc[i, colind]]

        # output to postgres
        eng = postgres_engine_generator()
        individual_scores_factors.to_sql(table, eng, schema = schema, if_exists=if_exists, index=False)
        print('- Processed ', filename)
    csvfile = 'current_student_predictions_logit.csv'
    generate_csv4mvesc(table, csvfile)
    print("- current student predictions saved to", csvfile )

if __name__=='__main__':
    main()
