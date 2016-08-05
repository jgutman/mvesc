import pandas as pd
from mvesc_utility_functions import postgres_pgconnection_generator, \
postgres_engine_generator
from save_reports import precision_at_k, Top_features
from sklearn.metrics import precision_recall_curve, roc_curve, f1_score, \
    confusion_matrix, precision_score, average_precision_score, accuracy_score

def next_id(user):
    """
    returns the next id number for a particualar user by query

    :param str user: initials of the user for a particular run
    :rtype int:
    """
    with postgres_pgconnection_generator() as connection: 
        with connection.cursor() as cursor:
            cursor.execute("""
            select count(*) from information_schema.tables
            where table_schema = 'model' and table_name = 'reports'
            """)
            table_exists = cursor.fetchall()[0][0] 
            if table_exists:
                cursor.execute("""
                select max(substring(filename from '{user}_(\d+)$')::int) 
                from model.reports;""".format(user=user))
                last_id = cursor.fetchall()[0][0]
            else:
                last_id = -1
        connection.commit()  
    return last_id + 1

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
        cursor.execute("drop table if exists model.reports")
        results_table_query = "create table model.reports ("         
        for c, c_type in columns:
            results_table_query += "{0} {1}, ".format(c, c_type)
        results_table_query+="timestamp timestamp default current_timestamp);"
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
    Note: if you add more values, make sure to add it both to the values 
    dictionary and to the list of column names and types
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
    model_name = values['model_name']
    try:
        get_top_features = getattr(Top_features, model_name)
    except AttributeError:
        top_features = [['NULL', 0],['NULL', 0],['NULL', 0]]
        print('top features not implemented for {}'.format(model_name))
    else:
        top_features = get_top_features(saved_outputs['estimator'], 
                                        saved_outputs['features'], 3)
    
    values['feature_1'] = top_features[0][0]
    values['feature_2'] = top_features[1][0]
    values['feature_3'] = top_features[2][0]
    values['feature_1_weight'] = top_features[0][1]
    values['feature_2_weight'] = top_features[1][1]
    values['feature_3_weight'] = top_features[2][1]
    values['filename'] = saved_outputs['file_name']
    values['random_seed'] = model_options['random_seed']
    values['debug'] = model_options['debug']
    values['time'] = saved_outputs['time']
    columns = [('model_name', 'text'),
               ('filename', 'text'),
               ('random_seed', 'int'),
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
               ('time', 'float'),
               ('debug', 'bool')]

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
    # scores and predictions for each student
    test_label = pd.Series('test', index=saved_outputs['test_y'].index)
    train_label = pd.Series('train', index=saved_outputs['train_y'].index)
    test = saved_outputs['test_y'].to_frame('true_label')
    test['predicted_score'] = saved_outputs['test_set_soft_preds']
    test['predicted_label'] = saved_outputs['test_set_preds']
    test['split'] = test_label
    train = saved_outputs['train_y'].to_frame('true_label')
    train['predicted_score'] = saved_outputs['train_set_soft_preds']
    train['predicted_label'] = saved_outputs['train_set_preds']
    train['split'] = train_label
    results = pd.concat([test,train])

    filename = saved_outputs['file_name']

    engine = postgres_engine_generator()
    results.to_sql(filename,  engine, 
                   schema='predictions', if_exists = 'replace')
    print('student predictions written to database')

    # importance scores for each feature
    model_name = saved_outputs['model_name']
    try:
        get_top_features = getattr(Top_features, model_name)
    except AttributeError:
        print('top features not implemented for {}'.format(model_name))
    else:
        top_features = get_top_features(saved_outputs['estimator'], 
                                        saved_outputs['features'], -1)
        features = pd.DataFrame(top_features, columns=['feature','importance'])
        features.to_sql(filename, engine, schema='feature_scores',
                        if_exists = 'replace')
        print('feature importances written to database')
            
