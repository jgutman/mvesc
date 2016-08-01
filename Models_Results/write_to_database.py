def build_results_table(cursor,columns):
    """                                                                        
    builds the results table if it does not already exist
    :param pg_cursor cursor:
    :param list columns: list of column names to create
    """                                                                        
    results_table_query = "create table if not exists model.reports ("         
    for c in columns:                                                          
        results_table_query += "{} text, ".format(c)                           
    results_table_query = results_table_query[:-2] + ");"                      
    #print(results_table_query)                                                
    cursor.execute(results_table_query)                                        

def add_row(cursor, columns, values): 
    """             
    adds a row to the results table consisting of the values given
    :param pg_cursor cursor:
    :param list columns: list of column names to update                        
    :param dict values: a dictionary with keys corresponding the col names
    """                                                                        
    add_row_query = "insert into model.reports ( "
    for c in columns:                  
        add_row_query += "{}, ".format(c)                                      
    add_row_query = add_row_query[:-2] + " ) values ("
    for c in columns:
        add_row_query += "%(c)s, ".format(c)
    add_row_query += ");"
    print(add_row_query)
    print(values)
    cursor.execute(add_row_query, values)  

def main():
    with postgres_pgconnection_generator() as connection:                      
        with connection.cursor() as cursor:                                    
            columns = ['model_name','label','feature_categories',
                       'train_set','test_set',
                       'parameters', 'train_f1', 'test_f1', 
                       'train_precision_0.05', 'test_precision_0.05',
                       'train_precision_0.1', 'test_precision_0.1', 
                       'feature_1','feature_2','feature_3']
            values = dict()
            values['model_name'] = saved_outputs['model_name']
            values['label'] = model_options['outcome_name']
            features = model_options['features_included'].keys()
            features.remove('grades')
            features = ", ".join(features)
            feature_grades = ", ".join(model_options['features_included']\
                                       ['grades'])
            values['feature_categories'] = features
            values['feature_grades'] = feature_grades
            values['train_set'] = ", ".join(model_options['cohorts_training'])
            # not finished
            build_results_table(cursor)                                        
            add_row(cursor,db_saved_outputs)                                   
            print('row added')                                                 
        connection.commit()  

if __name__ = "__main__":
    main()
