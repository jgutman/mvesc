from sklearn.metrics import make_scorer, get_scorer
from sklearn.metrics import precision_score, recall_score, roc_auc_score
import numpy as np
import pandas as pd

def precision_at_k(y_true, y_scores, k):
    """                                                                         
    Adapted from Rayid's magicloops code, this calculates precision on          
    the top k proportion of population                                          
                                                                                
    :param pd.Series y_true:                                                    
    :param pd.Series y_scores:                                                  
    :param int k:                                                               
    :returns: precision                                                         
    :rtype: float                                                               
    """
    if type(y_scores) == pd.core.frame.DataFrame:
        y_scores = y_scores[0]
    elif type(y_scores) != pd.core.series.Series:
        try:
            y_scores = pd.Series(y_scores)
        except:
            print('y_scores must be a Series or a DataFrame')
            sys.exit(1)
    pred = [int(a) for a in
            y_scores.rank(method='first',pct=True, ascending=False) < k]
    y_pred = pd.Series(pred, index=y_scores.index)
    return precision_score(y_true, y_pred)


def recall_at_k(y_true, y_scores, k):
    """                                                                         
    Adapted from Rayid's magicloops code, this calculates recall on             
    the top k proportion of population                                          
                                                                                
    :param pd.Series y_true:                                                    
    :param pd.Series y_scores:                                                  
    :param int k:                                                               
    :returns: recall                                                            
    :rtype: float                                                               
    """
    if type(y_scores) == pd.core.frame.DataFrame:
        y_scores = y_scores[0]
    elif type(y_scores) != pd.core.series.Series:
        try:
            y_scores = pd.Series(y_scores)
        except:
            print('y_scores must be a Series or a DataFrame')
            sys.exit(1)
    pred = [int(a) for a in
            y_scores.rank(method='first',pct=True, ascending=False) < k]
    y_pred = pd.Series(pred, index=y_scores.index)
    return recall_score(y_true, y_pred)

def precision_recall_range(y_true,  y_scores, min_k, max_k, metric = 'precision'):
    assert(min_k > 0.0 and min_k < 1.0), "min_k must be a percentage in decimal format"
    assert(max_k > 0.0 and max_k < 1.0), "max_k must be a percentage in decimal format"
    assert(min_k <= max_k), "min_k must be less than max_k"
    if (len(y_scores.shape) == 2):
        y_scores = y_scores[:,1]
    if (metric == 'precision'):
        scorer = precision_at_k
    elif (metric == 'recall'):
        scorer = recall_at_k
    else:
        print('unknown metric')
        return 0.0

    scores = []
    for k in np.linspace(min_k, max_k, 20):
        top_n = int(k*len(y_scores))
        scores.append(scorer(y_true, y_scores, k))
    return np.mean(scores)

def precision_recall_at_top_k(y_true, y_scores, k, metric = 'precision'):
    assert(k > 0.0 and k < 1.0), "k must be a percentage in decimal format"
    if (len(y_scores.shape) == 2):
        y_scores = y_scores[:,1]
    top_n = int(k*len(y_scores))

    if (metric == 'precision'):
        return precision_at_k(y_true, y_scores, k)
    elif (metric == 'recall'):
        return recall_at_k(y_true, y_scores, k)
    else:
        print('unknown metric')
        return 0.0

def scorer_range(min_k, max_k, metric):
    scorer = make_scorer(precision_recall_range,
                         min_k=min_k, max_k=max_k, metric=metric)
    return scorer

def scorer_at_top_k(k, metric):
    scorer = make_scorer(precision_recall_at_top_k,
                         k=k, metric=metric)
    return scorer

def build_tuple_scorer(criterion_list):
    scorer_list = [parse_criterion_string(x) for x in criterion_list]
    tuple_score = lambda estimator, X, y: (score_fn(estimator, X, y)
        for score_fn in scorer_list)
    return tuple_score

def parse_criterion_string(criterion):
    criterion = criterion.lower()
    if criterion.startswith('custom'):
        # return custom scorer object
        criterion_split = criterion.split("_")
        if len(criterion_split) == 4:
            min_k = float(criterion_split[2])
            max_k = float(criterion_split[3])
            metric = criterion_split[1]
            if (min_k >= 1.0):
                min_k = min_k / 100. 
            if (max_k >= 1.0):
                max_k = max_k / 100. 
            custom_scorer = scorer_range(min_k, max_k, metric)
        else:
            assert(len(criterion_split) == 3), "validation_criterion: custom_precision_10"
            k = float(criterion_split[2])
            metric = criterion_split[1]
            if (k >= 1.0):
                k = k / 100.
            custom_scorer = scorer_at_top_k(k, metric)
        return custom_scorer
    else:
        try:
            scorer_from_string = get_scorer(criterion)
            return scorer_from_string
        except ValueError:
            print('could not parse criterion')


def main():
    print('testing custom scorer')
    y_scores = np.array([0.1, 0.5, 0.5, 0.3, 0.7, 0.6, 0.8, 0.8])
    y_true = np.array([0, 1, 0, 0, 1, 0, 1, 1])
    k = 0.5
    print(precision_recall_at_top_k(y_true, y_scores, k))
    criterion = 'custom_precision_50'
    test_scorer = parse_criterion_string(criterion)
    print(test_scorer)

    print('testing average recall')
    print(precision_recall_range(y_true,  y_scores, .2, .25, 'recall'))

    print('testing average precision')
    print(precision_recall_range(y_true,  y_scores, .2, .25, 'precision'))

    criterion = 'custom_precision_20_50'
    test_scorer = parse_criterion_string(criterion)
    print(test_scorer)

if __name__ == '__main__':
    main()
