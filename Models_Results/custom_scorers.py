from sklearn.metrics import make_scorer, get_scorer
from sklearn.metrics import precision_score, recall_score, roc_auc_score
import numpy as np

def precision_recall_at_top_k(y_true, y_scores, k, metric = 'precision'):
    assert(k > 0.0 and k < 1.0), "k must be a percentage in decimal format"
    if (len(y_scores.shape) == 2):
        y_scores = y_scores[:,1]
    top_n = int(k*len(y_scores))
    threshold = np.sort(y_scores)[::-1][top_n]
    if (type(threshold)==np.ndarray):
        threshold = threshold[0]
    y_pred = 1.0 * (y_scores >= threshold)

    if (metric == 'precision'):
        return precision_score(y_true, y_pred)
    elif (metric == 'recall'):
        return recall_score(y_true, y_pred)
    else:
        print('unknown metric')
        return 0.0

def scorer_at_top_k(k, metric):
    scorer = make_scorer(precision_recall_at_top_k,
        # needs_proba = False, needs_threshold = False,
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

if __name__ == '__main__':
    main()
