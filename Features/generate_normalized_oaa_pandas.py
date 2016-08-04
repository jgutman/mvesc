import os, sys
parentdir = os.path.abspath('/home/zzhang/mvesc/ETL')
sys.path.insert(0,parentdir)
from feature_utilities import *

import yaml

## Overall
## Makes normalization and corrections in Pandas and writes it to Postgres
## Note: This is relatively slow because of (1) for loop and (2) writing to Postgres

def df2postgres(df, table_name, nrows=-1, if_exists='fail', schema='raw'):
    """ dump dataframe object to postgres database
    
    :param pandas.DataFrame df: dataframe
    :param int nrows: number of rows to write to table;
    :return str table_name: table name of the sql table
    :rtype str: the name of the created table name
    """
    # create a postgresql engine to wirte to postgres
    engine = postgres_engine_generator()
    
    #write the data frame to postgres
    if nrows==-1:
        df.to_sql(table_name, engine, schema=schema, index=False, if_exists=if_exists)
    else:
        df.iloc[:nrows, :].to_sql(table_name, engine, schema=schema, index=False, if_exists=if_exists)
    return table_name

def get_table_of_student_in_grade_which_year(students_with_outcomes):
    """ Looks at clean.all_snapshots and gets which year each student was in a grade.
    There are ~14 columns, one for each grade level.
    In each column, the value is the year a student was in that grade.
    To get past years where we did not observe a student, we took -1 from the
    neighboring column. This repeats going backwards through all earlier years,
    unless an observation was recorded from clean.all_snapshots.

    :rtype DataFrame: a data frame with student_lookup index and a column for each grade level
    """

    with postgres_pgconnection_generator() as connection:
        # read in clean.oaaogt table
        # oaa_raw = read_table_to_df(connection, 'oaaogt_numeric', schema = 'clean', nrows = -1)
        all_snapshots = read_table_to_df(connection, 'all_snapshots', schema = 'clean', nrows = -1)
    
    # summarize all_snapshots to figure out the year for each student's test grade
    #   use max year to choose
    #   results in only one unique row for each {student_lookup x grade} combination
    year_took_oaa = all_snapshots.groupby(['student_lookup', 'grade']).agg({'school_year': 'max'})
    year_took_oaa = year_took_oaa.reset_index('grade')

    # reshape the DataFrame to get a column for each grade
    wide_year_took_oaa = year_took_oaa.pivot(columns='grade', values='school_year')
    wide_year_took_oaa.columns = ['was_in_grade_{}'.format(int(x)) for x in wide_year_took_oaa.columns]
    wide_year_took_oaa.reset_index(inplace=True)
    print('combinations of student_lookup and years table has been created')
    
    # set index on oaa_raw
    # copy the wide table to fill in null values
    wide_year_took_oaa.set_index('student_lookup', inplace = True)

    # merge with students_with_outcomes to reduce time cost
    wide_year_took_oaa = students_with_outcomes.merge(wide_year_took_oaa, 
                                                          left_index = 'student_lookup',
                                                          right_index = 'student_lookup', 
                                                          how = 'left')
    # now, work backwards to fill in empty rows
    # go one column at a time
    # for each column, loop through each row at a time
    # Hanna's suggested speedup code using `where`
        # cols = ['one','two','three']
        # for i,c in enumerate(cols[1:]):
        # df[c] = df[c].where(~df[c].isnull(), df[cols[i-1]]+1)
    for right_col in reversed(range(0, 13)):
        for index, row in wide_year_took_oaa.iterrows():
            if pd.isnull(row['was_in_grade_{}'.format(right_col-1)]):
                wide_year_took_oaa['was_in_grade_{}'.format(right_col-1)][index]\
                = wide_year_took_oaa['was_in_grade_{}'.format(right_col)][index] - 1
    print('filled in missing spaces using -1')

    return wide_year_took_oaa


def convert_oaa_ogt_to_numeric(students_with_outcomes):
    """ Gets the clean.oaaogt table and cleans it to numeric for normalization.
    This cleaning is required because some of the columns have string values denoting
    cheating or invalid scores. We also attempt to create a cheated indicator column.
    
    FUTURE: the cheating indicator has not been double-checked and not included yet
    FUTURE: Remove the tests that are old and not used for our current set of students

    :rtype DataFrame: the clean numeric oaa table
    """
    with postgres_pgconnection_generator() as connection:
        # read in clean.oaaogt table
        oaa_raw = read_table_to_df(connection, 'oaaogt', schema = 'clean', nrows = -1)
    
    # drop ogt columns
    oaa_raw = oaa_raw.loc[:, 'student_lookup':'eighth_socstudies_ss']

    # keep only the numeric rows where we have outcomes
    oaa_raw = students_with_outcomes.merge(oaa_raw, on = 'student_lookup', how = 'left')

    # get all the tests from oaa
    uniqueColNames = pd.Series(pd.Series([x[:-3] for x in oaa_raw.columns]).unique())
    # ignore these handful of tests
    #   fourth_write has weird values that are difficult to parse
    uniqueColNames = uniqueColNames[uniqueColNames.str.contains('fourth_write|fourth_ctz|fourth_science|sixth_write|sixth_ctz|sixth_science|seventh_write|eighth_socstudies') == False]

    # record test names to use later
    list_of_year_test_types = uniqueColNames[6:]
    print("List of Tests to Include")
    print(list_of_year_test_types)

    # mapping for converting the non-numeric values
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
            #   only occurs once
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
            oaa_raw[year_test_type+'_cheat'] = pd.to_numeric(oaa_raw[year_test_type+'_cheat'])

    # write table as oaaogt_numeric
    # df2postgres(oaa_raw, 'oaaogt_numeric', schema = 'clean', if_exists = 'replace')
    # print confirmation
    print('oaaogt_numeric has been created')
    # set index on oaa_raw
    oaa_raw.set_index('student_lookup', drop = False, inplace = True)
    # return list of columns
    return oaa_raw, list_of_year_test_types

def aggregate_rows_of_df_on_index(df, measure_col):
    # assume grouping by index
    idx = df.groupby(df.index)[measure_col].transform(max) == df[measure_col]
    return(df[idx])

def get_max_aggregate_oaa(oaa_numeric, list_of_year_test_types):
    """ Takes in cleaned oaa_numeric.
    Loops over tests to keep only one distinct for each student.
    :param oaa_numeric DataFrame:
    :param list_of_year_test_types list:
    :rtype DataFrame: only distinct
    """
    # start by getting distinct lookups only, indexed on lookup
    max_agg_oaa = pd.DataFrame({'student_lookup': pd.unique(oaa_numeric.index)}).set_index('student_lookup')
    
    for test in list_of_year_test_types:
        # grab the test and placement info
        test_only_and_pl = oaa_numeric[[test+'_ss', test+'_pl']]
        max_agg_test_only = aggregate_rows_of_df_on_index(test_only_and_pl, test+'_ss')
        max_agg_test_only.reset_index('student_lookup', inplace = True)
        max_agg_test_only = max_agg_test_only.drop_duplicates()
        max_agg_test_only.set_index('student_lookup', inplace = True)
        # concat with lookup_only
        max_agg_oaa = pd.concat([max_agg_oaa, max_agg_test_only], axis = 1, join_axes = [max_agg_oaa.index])
    
    # return the dataframe with only unique student lookups
    return(max_agg_oaa)

def generate_normalized_oaa_scores(grade_year_pairs, oaa_df, list_of_year_test_types,
                                   table_name):
    """ 
    Merges these two and then uses the grade_year_pairs info to group students together
    by year and get a year-normalized z-scores and percentile ranks for each year.
    These are recorded in a `oaa_normalized` column to write to postgres.

    :rtype None: (postgres table created)
    """

    # join these two tables to assign group memberships
    oaa_with_grade_year = oaa_df.merge(grade_year_pairs, left_index = 'student_lookup',
                                        right_on = 'student_lookup', how = 'left')
    
    # get `oaa_normalized`, the outcome table
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

    # SKIP. Because KRAL is missing for ~99% of our students with samples.
    # append kral placement and kral score info (un-normalized)
    #   FUTURE: normalize KRAL.
    # kindergarten_info = oaa_with_grade_year[['kral', 'kral_pl']]
    # oaa_normalized = pd.concat([oaa_normalized, kindergarten_info], axis = 1)

    for test in list_of_year_test_types:
        # get the corresponding grade_year column for the test
        corresponding_year = corresponding_grade_dict[test.split('_')[0]]
        # print(corresponding_year)

        # fill in with 3000 for observations with missing years (LOTS OF THESE)
        #   this allows for normalizing on unknown years
        #   this may not exist after our cleaning of grade_year_pairs
        oaa_with_grade_year[corresponding_year].fillna(value = 3000, inplace = True)
        
        # get and store column of normalized z-score transformed scores
        normalized_column = oaa_with_grade_year[[test+'_ss', corresponding_year]]\
            .groupby(corresponding_year).transform(zscore)
        normalized_column.columns = [test+"_normalized"]
        oaa_normalized = pd.concat([oaa_normalized, normalized_column], axis = 1)

        # get and store percentile column
        just_test_year = oaa_with_grade_year[[test+'_ss', corresponding_year]].dropna()
        percentile_column = just_test_year.groupby(corresponding_year).transform(lambda x: x.rank(pct = True))
        percentile_column.columns = [test+"_percentile"]
        oaa_normalized = pd.concat([oaa_normalized, percentile_column], axis = 1, join_axes=[oaa_normalized.index])
        
        # copy over the string rank assignment for each student
        test_score_categorical = oaa_with_grade_year[[test+'_pl']]
        oaa_normalized = pd.concat([oaa_normalized, test_score_categorical], axis = 1)

    # reset index
    oaa_normalized.reset_index('student_lookup', inplace = True)

    print("OAA Normalized and Placement Table Made")
    df2postgres(oaa_normalized, table_name, schema = 'model', if_exists = 'replace')
    print("OAA Normalized Uploaded to Postgres")
    return(oaa_normalized)

# def aggregate_duplicate_normalized_oaa_scores(cursor, table_name, schema = 'model',
#                                               agg_function = 'max'):
#     """ Takes the earlier created normalized oaa scores table
#     and collapses on student_lookup for all columns using the max function.
#     First creates a temp table and then renames it to the original table_name.

#     :rtype None: prints a success statement
#     """
#     list_of_columns = get_column_names(cursor, table_name, schema)
#     list_of_data_columns = [x for x in list_of_columns if x != 'student_lookup']

#     sql_individual_columns = """select student_lookup, """
#     for column in list_of_data_columns:
#         sql_individual_columns += """
#         {agg_func}({data_feature}) as {data_feature},""".format(agg_func = agg_function,
#                                                                 data_feature = column)

#     sql_collapse = """create temp table temp_collapsed as 
#     ({sql_individual_columns} 
#     from {schema}.{table_name} group by student_lookup);"""\
#     .format(sql_individual_columns = sql_individual_columns[:-2],
#             schema = schema, table_name = table_name)

#     cursor.execute(sql_collapse)

#     sql_rename = """drop table if exists model.oaa_normalized;
#     create table model.oaa_normalized as (select * from temp_collapsed);"""

#     cursor.execute(sql_rename)

#     print("Finished collapsing duplicate student_lookups in normalized oaa scores")


def main():
    # only keep students with outcomes
    with postgres_pgconnection_generator() as connection:
            # read in clean.oaaogt table
            students_with_outcomes = pd.read_sql_query("""select distinct student_lookup                                     
        from clean.wrk_tracking_students                                   
        where outcome_category is not null;""", connection, )
    # set index for merging
    students_with_outcomes.set_index('student_lookup', drop=False, inplace = True)

    # get the necessary data frames
    grade_year_pairs = get_table_of_student_in_grade_which_year(students_with_outcomes)
    oaa_numeric, list_of_year_test_types = convert_oaa_ogt_to_numeric(students_with_outcomes)
    
    # reduce duplicate student lookup scores
    oaa_numeric_no_dup = get_max_aggregate_oaa(oaa_numeric, list_of_year_test_types)

    # generate and upload table
    oaa_normalized = generate_normalized_oaa_scores(grade_year_pairs, oaa_numeric_no_dup, 
                                                    list_of_year_test_types,
                                                    table_name = 'oaa_normalized')

    # no longer neeed because we implemented aggregation in pandas
#     # fix the duplicate rows in SQL
#     with postgres_pgconnection_generator() as connection:
#         with connection.cursor() as cursor:
#             aggregate_duplicate_normalized_oaa_scores(cursor,
#                                                       table_name = 'oaa_normalized', schema = 'model')
#             connection.commit()

if __name__ == '__main__':
    main()
