from mvesc_utility_functions import postgres_pgconnection_generator, \
postgres_engine_generator
from save_reports import precision_at_k, Top_features
from sklearn.metrics import precision_recall_curve, roc_curve, f1_score, \
    confusion_matrix, precision_score, average_precision_score, accuracy_score

def build_results_table(cursor,columns,replace=False):
    """                                                                        
    builds the results table if it does not already exist
    :param pg_cursor cursor:
    :param list columns: list of column names to create
    :param bool replace: if true, existing table is deleted and replaced
    """                                             
    cursor.execute("""
    select count(*) from information_schema.tables
    where table_schema = 'model' and table_name = 'reports'
    """)
    table_exists = cursor.fetchall()[0][0]
    if not table_exists or replace:
        cursor.execute("drop table model.reports")
        results_table_query = "create table model.reports ("         
        for c, c_type in columns:
            results_table_query += "{0} {1}, ".format(c, c_type)
        results_table_query = results_table_query[:-2] + ");"
        cursor.execute(results_table_query)

def add_row(cursor, columns, values): 
    """             
    adds a row to the results table consisting of the values given
    :param pg_cursor cursor:
    :param list columns: list of column names to update                        
    :param dict values: a dictionary with keys corresponding the col names
    """                                                                        
    add_row_query = "insert into model.reports ( "
    for c, t in columns:                  
        add_row_query += "{}, ".format(c)                                      
    add_row_query = add_row_query[:-2] + " ) values ("
    for c, t in columns:
        add_row_query += "%({})s, ".format(c)
    add_row_query = add_row_query[:-2] + ");"
    cursor.execute(add_row_query, values)  

def summary_to_db(saved_outputs):
    """
    doc string!
    """
    model_options = saved_outputs['model_options']
    test_y = saved_outputs['test_y']
    train_y = saved_outputs['train_y']
    test_scores = saved_outputs['test_set_soft_preds']
    train_scores = saved_outputs['train_set_soft_preds']
    test_preds = saved_outputs['test_set_preds']
    train_preds = saved_outputs['train_set_preds']
    
    values = dict()
    values['model_name'] = saved_outputs['model_name']
    values['label'] = model_options['outcome_name']
    features = list(model_options['features_included'].keys())
    features.remove('grades')
    features = ", ".join(features)
    feature_grades = ", ".join([str(a) for a 
                                in model_options['feature_grade_range']])
    values['feature_categories'] = features
    values['feature_grades'] = feature_grades
    train = model_options['cohorts_training']
    test = model_options['cohorts_held_out']
    values['train_set'] = ", ".join([str(a) for a in train])
    values['test_set'] = ", ".join([str(a) for a in test])
    params = saved_outputs['parameter_grid']
    model = saved_outputs['estimator'].best_estimator_
    param_list = []
    for param in params.keys():
        param_list.append("{} = {}".format(param, getattr(model,param)))
    values['parameters'] = "; ".join(param_list)
    values['train_acc'] = accuracy_score(train_y, train_preds)
    values['test_acc'] = accuracy_score(test_y, test_preds)
    values['train_precision_5'] = precision_at_k(train_y, train_scores, .05)
    values['train_precision_10'] = precision_at_k(train_y, train_scores, .1)
    values['test_precision_5'] = precision_at_k(test_y, test_scores, .05)
    values['test_precision_10'] = precision_at_k(test_y, test_scores, .1)
    values['average_precision'] = average_precision_score(test_y, test_scores)
    try:
        get_top_features = getattr(Top_features, values['model_name'])
    except AttributeError:
        top_features = [['NULL', 0],['NULL', 0],['NULL', 0]]
        print('top features not implemented for {}'.format(model_name))
        pass
    else:
        top_features = get_top_features(saved_outputs['estimator'], 
                                        saved_outputs['features'], 3)
    values['feature_1'] = top_features[0][0]
    values['feature_2'] = top_features[1][0]
    values['feature_3'] = top_features[2][0]
    values['feature_1_weight'] = top_features[0][1]
    values['feature_2_weight'] = top_features[1][1]
    values['feature_3_weight'] = top_features[2][1]
    values['filename'] = model_options['file_save_name']
    columns = [('model_name', 'text'),
               ('label', 'text'),
               ('feature_categories', 'text'),
               ('feature_grades', 'text'),
               ('train_set', 'text'),
               ('test_set', 'text'),
               ('parameters', 'text'),
               ('train_acc', 'float'),
               ('test_acc', 'float'),
               ('train_precision_5','float'),
               ('train_precision_10','float'),
               ('test_precision_5','float'),
               ('test_precision_10','float'),
               ('average_precision','float'),
               ('feature_1', 'text'),
               ('feature_1_weight','float'),
               ('feature_2', 'text'),
               ('feature_2_weight','float'),
               ('feature_3', 'text'),
               ('feature_3_weight', 'float'),
               ('filename', 'text')]

    with postgres_pgconnection_generator() as connection: 
        with connection.cursor() as cursor:
            build_results_table(cursor, columns)
            add_row(cursor, columns, values)
        connection.commit()  
    print('row added')                                                 

def write_scores_to_db(saved_outputs):
    """
    doc string!
    """
    df = 
    filename = saved_outputs['model_options']['file_save_name']
    engine = postgres_engine_generator()
    df.to_sql(filename, engine, schema='scores')

    # with postgres_pgconnection_generator() as connection: 
    #     with connection.cursor() as cursor:    
    #         cursor.execute("drop table if exists scores.{}".format(filename))
    #         create_table_query = """create table scores.{} 
    #         (student_lookup int, split text, score float, confusion text);
    #         """.format(filename))
    #         cursor.execute(create_table_query)
            
