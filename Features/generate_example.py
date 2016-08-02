from feature_utilities import *

def generate_x(replace = False):
    schema, table = "model", "x"
    with postgres_pgconnection_generator() as connection:
        with connection.cursor() as cursor:
            create_feature_table(cursor, table)
            
            # some code to generate the feature
            # in column new_col_1, new_col_2, etc in table new_table
            # following step will be more efficient
            # if new_table has an index
            
            update_column_with_join(cursor, table, 
                                    column = ['new_col_1', 'new_col_2'], 
                                    source_table = 'new_table')
            connection.commit()
            # optional parameters:
            #    source_schema - if the source is not a temporary table
            # note: there is no longer an optional parameter for new column
            # names - they will be the same in the feature table as 
            # they are in the table you feed in


