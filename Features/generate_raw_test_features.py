import os, sys
parentdir = os.path.abspath('/home/zzhang/mvesc/ETL')
sys.path.insert(0,parentdir)
from mvesc_utility_functions import *

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