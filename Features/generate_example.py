from feature_utilities import *

def generate_x(model_schema, replace = False):
    with postgres_pgconnection_generator() as connection:
        with connection.cursor() as cursor:
            create_feature_table(cursor, "table_name")

            # some code to generate the feature
            # in column new_col_1, new_col_2, etc in table new_table
            # following step will be more efficient
            # if new_table has an index

            update_column_with_join(cursor, table, model_schema,
                                    column = ['new_col_1', 'new_col_2'],
                                    source_table = 'new_table')
            connection.commit()
            # optional parameters:
            #    source_schema - if the source is not a temporary table
