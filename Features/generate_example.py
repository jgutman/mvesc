from feature_utilities import *

def generate_x():
    schema, table = "model", "x"
    with postgres_pgconnection_generator() as connection:
        with connection.cursor() as cursor:
            create_feature_table(cursor, table)

            # for each feature, each grade level:
            
                # some code to generate the feature
                # in column new_col, table new_table
                # following step will be more efficient
                # if new_table has an index

                update_column_with_join(cursor, table, column = 'new_col', 
                                        source_table = 'new_table')
                # optional parameters:
                #    source_column - if the source has a different name than desired
                #    source_schema - if the source is not a temporary table


