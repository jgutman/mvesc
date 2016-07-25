import os, sys
parentdir = os.path.abspath('/home/zzhang/mvesc/ETL')
sys.path.insert(0,parentdir)
from feature_utilities import *()

import yaml

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