# partitioning strategy for different kind of attribute

def nominal(dataset, attr, cls_attr, measure, impurity=None, _cmp=None):
    '''
    Distinct value without order
        - Multiway partitioning
        e.g. Color
    '''
    if impurity is None:
        impurity = measure(dataset, cls_attr)

# TODO: may try to pass index instead of a set to impurity measure
    cluster = {}
    for instance in dataset:
        cls = instance[attr]
        if not cluster.has_key(cls):
            cluster[cls] = []
        cluster[cls].append(instance)

    gain = impurity
    for c in cluster.values():
        gain -= measure(c, cls_attr)

    return None, gain


def ordinal(dataset, attr, cls_attr, measure, impurity=None, _cmp=None):
    '''
    Distinct value with order
        - Binary partitioning
        e.g. Grade {A, B, C, ..., F}
    '''
    if _cmp is None:
        _cmp = lambda x,y: cmp(x[attr], y[attr])

    if impurity is None:
        impurity = measure(dataset, cls_attr)

    dataset = dataset[:]    # create clone
    dataset = sorted(dataset, cmp=_cmp)

    best_gain  = -1
    best_pivot = None
    size       = len(dataset)
    for i in xrange(1, size):
        if dataset[i-1][attr] == dataset[i][attr]:
            # same value, skip
            continue
        else:
            pivot = dataset[i][attr]
# TODO: may try to pass index instead of a set to impurity measure
            head          = dataset[:i]
            head_ratio    = len(head)/size
            head_impurity = measure(head, cls_attr)

            tail          = dataset[i:]
            tail_ratio    = len(tail)/size
            tail_impurity = measure(tail, cls_attr)

            gain = impurity - head_impurity - tail_impurity
            if gain > best_gain:
                best_gain  = gain
                best_pivot = pivot

    return best_pivot, best_gain

def interval(dataset, attr, cls_attr, measure, impurity=None, _cmp=None):
    '''
    Numeric value where the differences between value is meaningful
    Measured along a scale in which each position is equidistant from another
        - Binary partitioning
        e.g. calendar date
    '''
    if _cmp is None:
        _cmp = lambda x,y: cmp(x[attr], y[attr])

    if impurity is None:
        impurity = measure(dataset, cls_attr)

    dataset = dataset[:]    # create clone
    dataset = sorted(dataset, cmp=_cmp)

    best_gain  = -1
    best_pivot = None
    size       = len(dataset)
    for i in xrange(1, size):
        if dataset[i-1][attr] == dataset[i][attr]:
            # same value, skip
            continue
        else:
            pivot = dataset[i][attr]
# TODO: may try to pass index instead of a set to impurity measure
            head          = dataset[:i]
            head_ratio    = len(head)/size
            head_impurity = measure(head, cls_attr)

            tail          = dataset[i:]
            tail_ratio    = len(tail)/size
            tail_impurity = measure(tail, cls_attr)

            gain = impurity - head_impurity - tail_impurity
            if gain > best_gain:
                best_gain  = gain
                best_pivot = pivot

    return best_pivot, best_gain

def ratio(dataset, attr, cls_attr, measure, impurity=None, _cmp=None):
    '''
    Numeric value where both the differences and the ratio are meaningful
    The number zero has meaning
        - Binary partitioning
        e.g. length, mass
    '''
    if _cmp is None:
        _cmp = lambda x,y: cmp(x[attr], y[attr])

    if impurity is None:
        impurity = measure(dataset, cls_attr)

    dataset = dataset[:]    # create clone
    dataset = sorted(dataset, cmp=_cmp)

    best_gain  = -1
    best_pivot = None
    size       = len(dataset)
    for i in xrange(1, size):
        if dataset[i-1][attr] == dataset[i][attr]:
            # same value, skip
            continue
        else:
            pivot = (dataset[i-1][attr] + dataset[i][attr]) / 2.0
# TODO: may try to pass index instead of a set to impurity measure
            head          = dataset[:i]
            head_ratio    = len(head)/size
            head_impurity = measure(head, cls_attr)

            tail          = dataset[i:]
            tail_ratio    = len(tail)/size
            tail_impurity = measure(tail, cls_attr)

            gain = impurity - head_impurity - tail_impurity
            if gain > best_gain:
                best_gain  = gain
                best_pivot = pivot

    return best_pivot, best_gain


def __test__():
    import measure, datetime

    data = [
        {'a': 2, 'b': datetime.date(2003, 12, 5), 'c': 'A', 'cls': 1},
        {'a': 7, 'b': datetime.date(2004, 12, 5), 'c': 'A', 'cls': 1},
        {'a': 1, 'b': datetime.date(2007, 12, 5), 'c': 'A', 'cls': 2},
        {'a': 9, 'b': datetime.date(2008, 12, 5), 'c': 'D', 'cls': 3},
        {'a': 3, 'b': datetime.date(2009, 12, 5), 'c': 'B', 'cls': 1},
        {'a': 2, 'b': datetime.date(2010, 12, 5), 'c': 'C', 'cls': 3},
    ]

    entropy_impurity = measure.entropy(data, 'cls')
    giniidx_impurity = measure.giniidx(data, 'cls')
    cls_err_impurity = measure.cls_err(data, 'cls')

    print ratio(data, 'a', 'cls', measure.entropy, entropy_impurity)
    print ratio(data, 'a', 'cls', measure.giniidx, giniidx_impurity)
    print ratio(data, 'a', 'cls', measure.cls_err, cls_err_impurity)

    print interval(data, 'b', 'cls', measure.entropy, entropy_impurity)
    print interval(data, 'b', 'cls', measure.giniidx, giniidx_impurity)
    print interval(data, 'b', 'cls', measure.cls_err, cls_err_impurity)

    print ordinal(data, 'c', 'cls', measure.entropy, entropy_impurity)
    print ordinal(data, 'c', 'cls', measure.giniidx, giniidx_impurity)
    print ordinal(data, 'c', 'cls', measure.cls_err, cls_err_impurity)

    print nominal(data, 'c', 'cls', measure.entropy, entropy_impurity)
    print nominal(data, 'c', 'cls', measure.giniidx, giniidx_impurity)
    print nominal(data, 'c', 'cls', measure.cls_err, cls_err_impurity)

if __name__ == '__main__':
    __test__()
