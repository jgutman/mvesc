import os, sys
parentdir = os.path.abspath('/home/zzhang/mvesc/ETL')
sys.path.insert(0,parentdir)
from feature_utilities import *

import yaml

def df2postgres(df, table_name, nrows=-1, if_exists='fail', schema='raw'):
    """ dump dataframe object to postgres database
    
    :param pandas.DataFrame df: dataframe
    :param int nrows: number of rows to write to table;
    :return str table_name: table name of the sql table
    :rtype str
    """
    # create a postgresql engine to wirte to postgres
    engine = postgres_engine_generator()
    
    #write the data frame to postgres
    if nrows==-1:
        df.to_sql(table_name, engine, schema=schema, index=False, if_exists=if_exists)
    else:
        df.iloc[:nrows, :].to_sql(table_name, engine, schema=schema, index=False, if_exists=if_exists)
    return table_name

def get_table_of_student_in_grade_which_year():
    """
    """

    # sql_agg_by_grade_year = """create table clean.grade_year_max_pairs as
    # (select student_lookup, grade, max(school_year) from clean.all_snapshots group by student_lookup, grade);"""

    with postgres_pgconnection_generator() as connection:
        # read in clean.oaaogt table
        # oaa_raw = read_table_to_df(connection, 'oaaogt_numeric', schema = 'clean', nrows = -1)
        all_snapshots = read_table_to_df(connection, 'all_snapshots', schema = 'clean', nrows = -1)
    
    # summarize all_snapshots to figure out the year for each student's test grade
    #   use max year to choose
    year_took_oaa = all_snapshots.groupby(['student_lookup', 'grade']).agg({'school_year': 'max'})
    year_took_oaa = year_took_oaa.reset_index('grade')

    wide_year_took_oaa = year_took_oaa.pivot(columns='grade', values='school_year')
    wide_year_took_oaa.columns = ['was_in_grade_{}'.format(int(x)) for x in wide_year_took_oaa.columns]
    wide_year_took_oaa.reset_index(inplace=True)
    print('appropriate table created in python')

    # write to postgres
    # df2postgres(wide_year_took_oaa, 'grade_year_max_pairs', schema = 'clean', if_exists = 'replace')
    # print confirmation
    print('grade_year_max_pairs has been created from dataframe')
    # return
    # set index on oaa_raw
    wide_year_took_oaa.set_index('student_lookup', inplace = True)
    return wide_year_took_oaa


def convert_oaa_ogt_to_numeric():
    """ creates clean.oaaogt_numeric

    """
    with postgres_pgconnection_generator() as connection:
        # read in clean.oaaogt table
        oaa_raw = read_table_to_df(connection, 'oaaogt', schema = 'clean', nrows = -1)
    
    # store original for debugging
    orig_oaa_raw = oaa_raw
    
    # drop ogt columns
    oaa_raw = oaa_raw.loc[:, 'student_lookup':'eighth_socstudies_ss']

    # get unique tests from oaa
    uniqueColNames = pd.Series(pd.Series([x[:-3] for x in oaa_raw.columns]).unique())
    uniqueColNames = uniqueColNames[uniqueColNames.str.contains('fourth_write') == False]
    list_of_year_test_types = uniqueColNames[6:]
    print(list_of_year_test_types)

    # mapping for the non-numeric values
    map_in_place_cheating_to_none = {'DNA':None, 'INV':None, 'DNS':None, '99':None, 'TOG':None}
    map_new_col_for_cheating_indicator = {'INV':'cheat', None:'missing'}
    
    for year_test_type in list_of_year_test_types:
        if (oaa_raw[year_test_type+'_ss'].dtype == np.float64 or oaa_raw[year_test_type+'_ss'].dtype == np.int64):
            print(year_test_type + ' is already a numeric')
        else:
            # make mapping replacements and
            # make a new indicator column for cheat/no-cheat
            oaa_raw[year_test_type+'_ss'].replace(map_in_place_cheating_to_none, inplace = True)
            oaa_raw[year_test_type + '_cheat'] = oaa_raw[year_test_type+'_ss'].map(map_new_col_for_cheating_indicator)

            # convert a weird backtick to a 1 (assumed) in strings
            #   debug by printing the weird values to make sure conversion is okay
            print(oaa_raw[year_test_type+'_ss'][oaa_raw[year_test_type+'_ss'].str.contains("`") == True])
            oaa_raw[year_test_type+'_ss'] = oaa_raw[year_test_type+'_ss'].str.replace('`', '1')
            
            # strip any leftover non-numeric characters
            oaa_raw[year_test_type+'_ss'] = oaa_raw[year_test_type+'_ss'].str.replace(pat = '[^0-9]+', repl = "")

            # make numeric switchover
            oaa_raw[year_test_type+'_ss'] = pd.to_numeric(oaa_raw[year_test_type+'_ss'])

            # need to replace the missing values in the newly created column
            oaa_raw[year_test_type+'_cheat'].fillna('not_a_num', inplace = True)
            oaa_raw[year_test_type+'_cheat'].replace({'not_a_num':0, 'cheat':1, 'missing':None}, inplace = True)

    # write table as oaaogt_numeric
    # df2postgres(oaa_raw, 'oaaogt_numeric', schema = 'clean', if_exists = 'replace')
    # print confirmation
    print('oaaogt_numeric has been created')
    # set index on oaa_raw
    oaa_raw.set_index('student_lookup', drop = False, inplace = True)
    # return list of columns
    return oaa_raw, list_of_year_test_types

def normalize_oaa_scores(cursor, list_of_year_test_types):
    """ makes a temporary table to perform the normalization for each test and joins it to a final table
    """

    grade_year_pairs = get_table_of_student_in_grade_which_year()
    oaa_numeric, list_of_year_test_types = convert_oaa_ogt_to_numeric()

    # join these two tables to assign group memberships
    oaa_with_grade_year = oaa_numeric.merge(grade_year_pairs, on = 'student_lookup', how = 'left')
    oaa_normalized = oaa_with_grade_year[['student_lookup']]

    oaa_with_grade_year.set_index('student_lookup', inplace = True)
    oaa_normalized.set_index('student_lookup', inplace = True)

    # prep zscore function
    zscore = lambda x: (x - x.mean()) / x.std()
    # and corresponding grade dict
    corresponding_grade_dict = {'third' : 'was_in_grade_3',
        'fourth' : 'was_in_grade_4',
        'fifth' : 'was_in_grade_5',
        'sixth' : 'was_in_grade_6',
        'seventh' : 'was_in_grade_7',
        'eighth' : 'was_in_grade_8'}

    for test in list_of_year_test_types:
        # corresponding
        corresponding_year = corresponding_grade_dict[test.split('_')[0]]
        print(corresponding_year)
        # fill in with 3000 for observations with missing years (LOTS OF THESE)
        oaa_with_grade_year[corresponding_year].fillna(value = 3000, inplace = True)
        # get column of normalized scores
        normalized_column = oaa_with_grade_year[[test+'_ss', corresponding_year]]\
            .groupby(corresponding_year).transform(zscore)
        normalized_column.columns = [test+"_normalized"]
        oaa_normalized = pd.concat([oaa_normalized, normalized_column], axis = 1)

        # percentile column
        percentile_column = oaa_with_grade_year[[test+'_ss', corresponding_year]]\
                .groupby(corresponding_year).transform(lambda x: x.rank() / len(x))
        percentile_column.columns = [test+"_percentile"]
        oaa_normalized = pd.concat([oaa_normalized, percentile_column], axis = 1)

        # get the string rank assignment for a student
        test_score_categorical = oaa_with_grade_year[[test+'_pl', test+'_cheat']]
        oaa_normalized = pd.concat([oaa_normalized, test_score_categorical], axis = 1)

    print("OAA Normalized and Placement Table Made")
    df2postgres(oaa_normalized, 'oaa_normalized', schema = 'features', if_exists = 'replace')
    print("OAA Normalized Uploaded to Postgres")


def generate_raw_snapshot_features(replace=False):
    schema, table = "model", "snapshots"
    with postgres_pgconnection_generator() as connection:
        with connection.cursor() as cursor:
            if replace:
                # make initial tables
                get_table_of_student_in_grade_which_year()
                list_of_year_test_types = convert_oaa_ogt_to_numeric()
            else:
                oaa_raw = read_table_to_df(connection, 'oaaogt', schema = 'clean', nrows = -1)
                # drop ogt columns
                oaa_raw = oaa_raw.loc[:, 'student_lookup':'eighth_socstudies_ss']
                # get unique tests from oaa
                uniqueColNames = pd.Series(pd.Series([x[:-3] for x in oaa_raw.columns]).unique())
                uniqueColNames = uniqueColNames[uniqueColNames.str.contains('fourth_write') == False]
                list_of_year_test_types = uniqueColNames[6:]

            print("Making aggregate OAA table in Clean Schema")
            print(list_of_year_test_types)
            create_aggregate_stats_table(cursor, list_of_year_test_types)
            connection.commit()

            # # merge in with snapshots
            # update_column_with_join(cursor, table, 
            #                         column_list = list_of_temp_cols, 
            #                         source_table = 'temp_snapshot_table')
            # print('Finished adding raw features from snapshots')

            # connection.commit()

            # # generate temp table for age-based snapshot features
            # list_of_temp_cols = blank(cursor)
            # # merge in with snapshots
            # update_column_with_join(cursor, table, 
            #                         column = list_of_temp_cols, 
            #                         source_table = 'temp_snapshot_table')
            # print 'Finished adding age-based features from snapshots'

            # optional parameters:
            #    source_column - if the source has a different name than desired
            #    source_schema - if the source is not a temporary table