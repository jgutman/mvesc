import os, sys
parentdir = os.path.abspath('/home/zzhang/mvesc/ETL')
sys.path.insert(0,parentdir)
from feature_utilities import *()

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
    df2postgres(wide_year_took_oaa, 'grade_year_max_pairs', schema = 'clean', if_exists = 'replace')
    # print confirmation
    print('grade_year_max_pairs has been created from dataframe')


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
    df2postgres(oaa_raw, 'oaaogt_numeric', schema = 'clean', if_exists = 'replace')
    # print confirmation
    print('oaaogt_numeric has been created')

def create_aggregate_stats_table():
    grade_year_pairs = ['was_in_grade_{}'.format(x) for x in range(3,9)]
    grade_year_pairs = ', '.join(grade_year_pairs)

    sql_join_to_temp_table = """create temp table as oaa_with_grade_year as
    (select t1.*, {list_of_grades} from clean.oaaogt_numeric as t1 
    left join clean.grade_year_max_pairs as t2 
    on t1.student_lookup = t2.student_lookup);""".format(list_of_grades = grade_year_pairs)

def create_temp_table_of_raw_data_from_snapshots(cursor, grade_range = range(1,10)):
    """ Contains a manually made list of raw features from the snapshots
    to create a column for each grade level. It collapses the raw data from
    snapshots on student_lookup. The choice of aggregation/collapse is given to
    the user, though it usually uses the 'max' function in SQL.
    Performs this by creating one column for each feature*grade combination,
    and then collapsing on student_lookup.

    :param object cursor: a cursor to interact with the database
    :param list grade_range: a list of specific grades to capture
    :rtype list: a list of the columns created in the temp_snapshots_table
    """

    # list of the features we will just take the raw values from (for now)
    list_of_raw_time_snapshot_features = ['days_absent', 'days_absent_excused', 
                        'days_absent_unexcused',
                        'days_present', 'disability', 'disadvantagement',
                        'discipline_incidents', 'district', 'gifted',
                        'iss', 'limited_english', 'oss', 'section_504_plan',
                        'special_ed', 'status']

    agg_func_dict = {'days_absent' : 'max',
    'days_absent_excused' : 'max',
    'days_absent_unexcused' : 'max',
    'days_present' : 'max',
    'disability' : 'max',
    'disadvantagement': 'max',
    'discipline_incidents' : 'max',
    'district' : 'max',
    'gifted' : 'max',
    'iss' : 'max',
    'limited_english' : 'max',
    'oss' : 'max',
    'section_504_plan' : 'max',
    'special_ed' : 'max',
    'status' : 'max'
    }

    with open('hard_code_imputation.yaml', 'r') as f:
        hard_code_imputation = yaml.load(f)

    # this initiates a list to store the created column names in the temp table
    list_of_created_grade_specific_columns = []

    print('Starting to join raw features per grade from snapshots')

    # loop through the given features
    sql_query_individual_columns = 'select student_lookup, '
    for raw_feature in list_of_raw_time_snapshot_features:
        # grab the feature value for each grade level for students
        # and aggregate that across all grade levels
        for grade_level in grade_range:
            # create string for new column name
            new_column_name = '{}_gr_{}'.format(raw_feature, grade_level)

            # check for coalesce value
            if raw_feature in hard_code_imputation:
                if type(hard_code_imputation[raw_feature]) is int:
                    coalesce_value = ', {}'.format(hard_code_imputation[raw_feature])
                else:
                    coalesce_value = ", '{}'".format(hard_code_imputation[raw_feature])
            else:
                coalesce_value = ''

            # generate query for this grade level
            sql_query_individual_columns += """
            coalesce({agg_func}(case when grade = {grade_level} then {raw_feature} end){coalesce_value}) as
            {new_column_name}, """.format(agg_func = 'max',
                                          grade_level = grade_level,
                                          coalesce_value = coalesce_value,
                                          raw_feature = raw_feature,
                                          new_column_name = new_column_name)

        print(raw_feature + ' is finished in temp table.')
        list_of_created_grade_specific_columns.extend(
                ['{}_gr_{}'.format(raw_feature, x) for x in grade_range])

    # use the generated sql cases and insert it as a subtable for
    # creating a temp table for snapshots data
    # note that this aggregates by student_lookup
    sql_create_temp_table = """drop table if exists temp_snapshot_table;
    create temp table temp_snapshot_table as
        ({sql_query_individual_columns}
        from clean.all_snapshots group by student_lookup);""".\
        format(sql_query_individual_columns = sql_query_individual_columns[:-2]) # the -2 is for the last comma

    cursor.execute(sql_create_temp_table)
    sql_create_index = "create index lookup_index on temp_snapshot_table(student_lookup)"
    cursor.execute(sql_create_index)

    return list_of_created_grade_specific_columns

def generate_raw_snapshot_features(replace=False):
    schema, table = "model", "snapshots"
    with postgres_pgconnection_generator() as connection:
        with connection.cursor() as cursor:
            create_feature_table(cursor, table, replace=replace)
            
            # generate temp table for raw snapshot features
            list_of_temp_cols = create_temp_table_of_raw_data_from_snapshots(cursor)
            
            # merge in with snapshots
            update_column_with_join(cursor, table, 
                                    column_list = list_of_temp_cols, 
                                    source_table = 'temp_snapshot_table')
            print('Finished adding raw features from snapshots')

            connection.commit()

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


def derive_per_year_normalized_oaa_scores(connection):
    """ reads in table and adds new columns
    """

    with postgres_pgconnection_generator() as connection:
        # read in clean.oaaogt table
        oaa_raw = read_table_to_df(connection, 'oaaogt', 'clean', nrows = -1)
        all_snapshots = read_table_to_df(connection, 'all_snapshots', 'clean', nrows = -1)

    # summarize all_snapshots to figure out the year for each student's test grade
    #   use max year to choose
    year_took_oaa = all_snapshots.groupby(['student_lookup', 'grade']).agg({'school_year': 'max'})
    year_took_oaa = year_took_oaa.reset_index('grade')

    wide_year_took_oaa = year_took_oaa.pivot(columns='grade', values='school_year')
    wide_year_took_oaa.columns = ['was_in_grade_{}'.format(int(x)) for x in wide_year_took_oaa.columns]

    # also adjust the oaa raw scores to be numeric
    list_of_year_test_types = ['third_read', 'third_math', 'fourth_read', 'fourth_math']

    map_in_place_cheating_to_none = {'DNA':None, 'INV':None, 'DNS':None, '99':None}
    map_new_col_for_cheating_indicator = {'INV':'cheat', None:'missing'}
    for year_test_type in list_of_year_test_types:
        if (oaa_raw[year_test_type+'_ss'].dtype == np.float64 or oaa_raw[year_test_type+'_ss'].dtype == np.int64):
            print(year_test_type + ' is already a numeric')
        else:
            oaa_raw[year_test_type+'_ss'].replace(map_in_place_cheating_to_none, inplace = True)
            oaa_raw[year_test_type + '_cheat'] = oaa_raw[year_test_type+'_ss'].map(map_new_col_for_cheating_indicator)
            # convert a weird backtick to a 1 (assumed)
            oaa_raw[year_test_type+'_ss'] = oaa_raw[year_test_type+'_ss'].str.replace('`', '1')
            oaa_raw[year_test_type+'_ss'] = pd.to_numeric(oaa_raw[year_test_type+'_ss'])

            # need to replace the missing values in the new column
            oaa_raw[year_test_type+'_cheat'].fillna('not_a_num', inplace = True)
            oaa_raw[year_test_type+'_cheat'].replace({'not_a_num':0, 'cheat':1, 'missing':None}, inplace = True)


    # after oaa_raw is converted, merge with the year of students
    oaa_with_grade_year = oaa_raw.join(wide_year_took_oaa, on = 'student_lookup')

    oaa_summary_df = pd.DataFrame(data = {'year_of_test' : range(2006, 2016)})
    # create another table with grade level averages
    for year_test_type in list_of_year_test_types:
        # get the mean and std and count
        agg_by_year_of_test = oaa_with_grade_year.groupby(corresponding_col).agg({year_test_type:['mean', 'std', 'count']})
        agg_by_year_of_test.reset_index().reset_index()
        agg_by_year_of_test.rename(columns = {corresponding_col : 'year_of_test'}, inplace = True)
        # join with oaa_summary_df
        oaa_summary_df = oaa_summary_df.join(agg_by_year_of_test, on = 'year_of_test')



        # make percentile function also

    oaa_with_grade_year.groupby


def create_temp_table_of_oaa_test_scores(cursor, grade_range = range(1,10)):
    """ Contains a manually made list of raw features from the snapshots
    to create a column for each grade level. It collapses the raw data from
    snapshots on student_lookup. The choice of aggregation/collapse is given to
    the user, though it usually uses the 'max' function in SQL.
    Performs this by creating one column for each feature*grade combination,
    and then collapsing on student_lookup.

    :param object cursor: a cursor to interact with the database
    :param list grade_range: a list of specific grades to capture
    :rtype list: a list of the columns created in the temp_snapshots_table
    """

    # list of the features we will just take the raw values from (for now)
    list_of_raw_time_snapshot_features = ['kral', 'kral_pl', 'third_read_pl']

    agg_func_dict = {'days_absent' : 'max',
    'days_absent_excused' : 'max',
    'days_absent_unexcused' : 'max',
    'days_present' : 'max',
    'disability' : 'max',
    'disadvantagement': 'max',
    'discipline_incidents' : 'max',
    'district' : 'max',
    'gifted' : 'max',
    'iss' : 'max',
    'limited_english' : 'max',
    'oss' : 'max',
    'section_504_plan' : 'max',
    'special_ed' : 'max',
    'status' : 'max'
    }

    # this initiates a list to store the created column names in the temp table
    list_of_created_grade_specific_columns = []

    print 'Starting to join raw features per grade from snapshots'

    # loop through the given features
    sql_query_individual_columns = 'select student_lookup, '
    for raw_feature in list_of_raw_time_snapshot_features:
        # grab the feature value for each grade level for students
        # and aggregate that across all grade levels
        for grade_level in grade_range:
            # create string for new column name
            new_column_name = '{}_gr_{}'.format(raw_feature, grade_level)

            # generate query for this grade level
            sql_query_individual_columns += """
            {agg_func}(case when grade = {grade_level} then {raw_feature} end) as
            {new_column_name}, """.format(agg_func = 'max',
                                          grade_level = grade_level,
                                          raw_feature = raw_feature,
                                          new_column_name = new_column_name)

        list_of_created_grade_specific_columns.extend(
                ['{}_gr_{}'.format(raw_feature, x) for x in grade_range])

    # use the generated sql cases and insert it as a subtable for
    # creating a temp table for snapshots data
    # note that this aggregates by student_lookup
    sql_create_temp_table = """drop table if exists temp_snapshot_table;
    create temp table temp_snapshot_table as
        ({sql_query_individual_columns}
        from clean.all_snapshots group by student_lookup);""".\
        format(sql_query_individual_columns = sql_query_individual_columns[:-2]) # the -2 is for the last comma

    cursor.execute(sql_create_temp_table); connection.commit()
    sql_create_index = "create index lookup_index on temp_snapshot_table(student_lookup)"
    cursor.execute(sql_create_index); connection.commit()
    
    # get list of created columns in temp table
    list_of_created_grade_specific_columns = []

    return list_of_created_grade_specific_columns

def generate_x(replace=False):
    schema, table = "model", "test_scores"
    with postgres_pgconnection_generator() as connection:
        with connection.cursor() as cursor:
            create_feature_table(cursor, table, replace=replace)
            
            # generate temp table for raw snapshot features
            list_of_temp_cols = create_temp_table_of_raw_test_scores(cursor)
            # merge in with snapshots
            update_column_with_join(cursor, table, 
                                    column = list_of_temp_cols, 
                                    source_table = 'temp_test_table')
            print 'Finished adding raw features from test scores'
                
            # optional parameters:
            #    source_column - if the source has a different name than desired
            #    source_schema - if the source is not a temporary table