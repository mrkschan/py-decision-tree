# partitioning strategy for different kind of attribute

# for normalization of (the effect of splitting too much) purity gain :
# use gain ratio instead of gain
# gain ratio = gain / split info
# split info = Sum( split ratio * log_2(split ratio) )

import math

def nominal(dataset, attr, cls_attr, measure, impurity=None, normalize=True, _cmp=None):
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
        val = instance[attr]
        if not cluster.has_key(val):
            cluster[val] = []
        cluster[val].append(instance)

    gain = impurity
    size = len(dataset)

    if normalize:
        split = .0

    for c in cluster.values():
        ratio = float(len(c)) / size
        gain -= ratio * measure(c, cls_attr)
        if normalize:
            # compute split info for normalization
            split += -ratio * math.log(ratio, 2)

    if normalize:
        # normalize as gain ratio
        gain /= split

    return cluster.keys(), gain, cluster


def ordinal(dataset, attr, cls_attr, measure, impurity=None, normalize=True, _cmp=None):
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

    best_gain  = .0
    best_pivot = None
    cluster    = None
    size       = len(dataset)
    for i in xrange(1, size):
        if dataset[i-1][attr] == dataset[i][attr]:
            # same value, skip
            continue
        else:
            pivot = dataset[i][attr]
# TODO: may try to pass index instead of a set to impurity measure
            head_partition = dataset[:i]
            head_ratio     = float(len(head_partition)) / size
            head_impurity  = measure(head_partition, cls_attr)

            tail_partition = dataset[i:]
            tail_ratio     = float(len(tail_partition)) / size
            tail_impurity  = measure(tail_partition, cls_attr)

            gain = impurity - (head_ratio * head_impurity) - (tail_ratio * tail_impurity)

            if normalize:
                # compute split info
                split  = .0
                split += -head_ratio * math.log(head_ratio, 2)
                split += -tail_ratio * math.log(tail_ratio, 2)

                gain /= split

            if gain > best_gain:
                best_gain  = gain
                best_pivot = pivot
                cluster    = {0: tail_partition, 1: head_partition}

    return best_pivot, best_gain, cluster

def interval(dataset, attr, cls_attr, measure, impurity=None, normalize=True, _cmp=None):
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

    best_gain  = .0
    best_pivot = None
    cluster    = None
    size       = len(dataset)
    for i in xrange(1, size):
        if dataset[i-1][attr] == dataset[i][attr]:
            # same value, skip
            continue
        else:
            pivot = dataset[i][attr]
# TODO: may try to pass index instead of a set to impurity measure
            head_partition = dataset[:i]
            head_ratio     = float(len(head_partition)) / size
            head_impurity  = measure(head_partition, cls_attr)

            tail_partition = dataset[i:]
            tail_ratio     = float(len(tail_partition)) / size
            tail_impurity  = measure(tail_partition, cls_attr)

            gain = impurity - (head_ratio * head_impurity) - (tail_ratio * tail_impurity)

            if normalize:
                # compute split info
                split  = .0
                split += -head_ratio * math.log(head_ratio, 2)
                split += -tail_ratio * math.log(tail_ratio, 2)

                gain /= split

            if gain > best_gain:
                best_gain  = gain
                best_pivot = pivot
                cluster    = {0: tail_partition, 1: head_partition}

    return best_pivot, best_gain, cluster

def ratio(dataset, attr, cls_attr, measure, impurity=None, normalize=True, _cmp=None):
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

    best_gain  = .0
    best_pivot = None
    cluster    = None
    size       = len(dataset)
    for i in xrange(1, size):
        if dataset[i-1][attr] == dataset[i][attr]:
            # same value, skip
            continue
        else:
            pivot = (dataset[i-1][attr] + dataset[i][attr]) / 2.0
# TODO: may try to pass index instead of a set to impurity measure
            head_partition = dataset[:i]
            head_ratio     = float(len(head_partition)) / size
            head_impurity  = measure(head_partition, cls_attr)

            tail_partition = dataset[i:]
            tail_ratio     = float(len(tail_partition)) / size
            tail_impurity  = measure(tail_partition, cls_attr)

            gain = impurity - (head_ratio * head_impurity) - (tail_ratio * tail_impurity)

            if normalize:
                # compute split info
                split  = .0
                split += -head_ratio * math.log(head_ratio, 2)
                split += -tail_ratio * math.log(tail_ratio, 2)

                gain /= split

            if gain > best_gain:
                best_gain  = gain
                best_pivot = pivot
                cluster    = {0: tail_partition, 1: head_partition}

    return best_pivot, best_gain, cluster


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

    print 'split'
    print ratio(data, 'a', 'cls', measure.entropy, entropy_impurity)
    print ratio(data, 'a', 'cls', measure.giniidx, giniidx_impurity)
    print ratio(data, 'a', 'cls', measure.cls_err, cls_err_impurity)
    print 'nosplit'
    print ratio(data, 'a', 'cls', measure.entropy, entropy_impurity, False)
    print ratio(data, 'a', 'cls', measure.giniidx, giniidx_impurity, False)
    print ratio(data, 'a', 'cls', measure.cls_err, cls_err_impurity, False)
    print

    print 'split'
    print interval(data, 'b', 'cls', measure.entropy, entropy_impurity)
    print interval(data, 'b', 'cls', measure.giniidx, giniidx_impurity)
    print interval(data, 'b', 'cls', measure.cls_err, cls_err_impurity)
    print 'nosplit'
    print interval(data, 'b', 'cls', measure.entropy, entropy_impurity, False)
    print interval(data, 'b', 'cls', measure.giniidx, giniidx_impurity, False)
    print interval(data, 'b', 'cls', measure.cls_err, cls_err_impurity, False)
    print

    print 'split'
    print ordinal(data, 'c', 'cls', measure.entropy, entropy_impurity)
    print ordinal(data, 'c', 'cls', measure.giniidx, giniidx_impurity)
    print ordinal(data, 'c', 'cls', measure.cls_err, cls_err_impurity)
    print 'nosplit'
    print ordinal(data, 'c', 'cls', measure.entropy, entropy_impurity, False)
    print ordinal(data, 'c', 'cls', measure.giniidx, giniidx_impurity, False)
    print ordinal(data, 'c', 'cls', measure.cls_err, cls_err_impurity, False)
    print

    print 'split'
    print nominal(data, 'c', 'cls', measure.entropy, entropy_impurity)
    print nominal(data, 'c', 'cls', measure.giniidx, giniidx_impurity)
    print nominal(data, 'c', 'cls', measure.cls_err, cls_err_impurity)
    print 'nosplit'
    print nominal(data, 'c', 'cls', measure.entropy, entropy_impurity, False)
    print nominal(data, 'c', 'cls', measure.giniidx, giniidx_impurity, False)
    print nominal(data, 'c', 'cls', measure.cls_err, cls_err_impurity, False)
    print

if __name__ == '__main__':
    __test__()
