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

    size    = len(dataset)
    size_f  = float(size)
    cluster = {}
    #~ for idx in xrange(0, size):
    for idx in range(0, size):
        instance = dataset[idx]
        val = instance[attr]

        #~ if not cluster.has_key(val):
        if val not in cluster.keys():
            cluster[val] = []

        cluster[val].append(instance)

    gain = impurity

    if normalize:
        split = .0

    for c in cluster.values():
        ratio = len(c) / size_f
        gain -= ratio * measure(c, cls_attr)
        if normalize:
            # compute split info for normalization
            split += -ratio * math.log(ratio, 2)

    if normalize:
        # normalize as gain ratio
        gain /= split

    #~ return gain, cluster.keys(), cluster
    return gain, list(cluster.keys()), cluster


def get_pivot_ordinal(idx, dataset, attr):
    return dataset[idx][attr]

def get_pivot_interval(idx, dataset, attr):
    return dataset[idx][attr]

def get_pivot_ratio(idx, dataset, attr):
    return (dataset[idx][attr] - dataset[idx-1][attr]) / 2.0


def partitioning(dataset, attr, cls_attr, measure, impurity, normalize, get_pivot):
    '''
    binary partitioning
    '''
    size   = len(dataset)
    size_f = float(size)

    bg = .0
    bp = None
    bc = None

    #~ for idx in xrange(0, size):
    for idx in range(0, size):
        if dataset[idx - 1][attr] == dataset[idx][attr]:
            # skip same attribute value, consider the idx for last same value only
            continue

        pivot = get_pivot(idx, dataset, attr)

        head_partition = dataset[:idx]
        head_ratio     = idx / size_f
        head_impurity  = measure(head_partition, cls_attr)

        tail_partition = dataset[idx:]
        tail_ratio     = (size - idx) / size_f
        tail_impurity  = measure(tail_partition, cls_attr)

        gain = impurity - (head_ratio * head_impurity) - (tail_ratio * tail_impurity)

        if normalize:
            # compute split info
            split  = .0
            split += -head_ratio * math.log(head_ratio, 2)
            split += -tail_ratio * math.log(tail_ratio, 2)
            gain /= split

        if gain > bg:
            bg = gain
            bp = pivot
            bc = { 1: head_partition, 0: tail_partition }
    # End for: finding best gain

    return bg, bp, bc


def ordinal(dataset, attr, cls_attr, measure, impurity=None, normalize=True, _cmp=None):
    '''
    Distinct value with order
        - Binary partitioning
        e.g. Grade {A, B, C, ..., F}
    '''
    #~ if _cmp is None:
        #~ _cmp = lambda x,y: cmp(x[attr], y[attr])

    if impurity is None:
        impurity = measure(dataset, cls_attr)

    # create clone sorted by attr value
    #~ dataset = sorted(dataset, cmp=_cmp)
    dataset = sorted(dataset, key=lambda x: x[attr])

    return partitioning(dataset, attr, cls_attr, measure, impurity, normalize, get_pivot_ordinal)

def interval(dataset, attr, cls_attr, measure, impurity=None, normalize=True, _cmp=None):
    '''
    Numeric value where the differences between value is meaningful
    Measured along a scale in which each position is equidistant from another
        - Binary partitioning
        e.g. calendar date
    '''
    #~ if _cmp is None:
        #~ _cmp = lambda x,y: cmp(x[attr], y[attr])

    if impurity is None:
        impurity = measure(dataset, cls_attr)

    # create clone sorted by attr value
    #~ dataset = sorted(dataset, cmp=_cmp)
    dataset = sorted(dataset, key=lambda x: x[attr])

    return partitioning(dataset, attr, cls_attr, measure, impurity, normalize, get_pivot_interval)

def ratio(dataset, attr, cls_attr, measure, impurity=None, normalize=True, _cmp=None):
    '''
    Numeric value where both the differences and the ratio are meaningful
    The number zero has meaning
        - Binary partitioning
        e.g. length, mass
    '''
    #~ if _cmp is None:
        #~ _cmp = lambda x,y: cmp(x[attr], y[attr])

    if impurity is None:
        impurity = measure(dataset, cls_attr)

    # create clone sorted by attr value
    #~ dataset = sorted(dataset, cmp=_cmp)
    dataset = sorted(dataset, key=lambda x: x[attr])

    return partitioning(dataset, attr, cls_attr, measure, impurity, normalize, get_pivot_ratio)



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

    #~ print 'split'
    #~ print ratio(data, 'a', 'cls', measure.entropy, entropy_impurity)
    #~ print ratio(data, 'a', 'cls', measure.giniidx, giniidx_impurity)
    #~ print ratio(data, 'a', 'cls', measure.cls_err, cls_err_impurity)
    #~ print 'nosplit'
    #~ print ratio(data, 'a', 'cls', measure.entropy, entropy_impurity, False)
    #~ print ratio(data, 'a', 'cls', measure.giniidx, giniidx_impurity, False)
    #~ print ratio(data, 'a', 'cls', measure.cls_err, cls_err_impurity, False)
    #~ print

    #~ print 'split'
    #~ print interval(data, 'b', 'cls', measure.entropy, entropy_impurity)
    #~ print interval(data, 'b', 'cls', measure.giniidx, giniidx_impurity)
    #~ print interval(data, 'b', 'cls', measure.cls_err, cls_err_impurity)
    #~ print 'nosplit'
    #~ print interval(data, 'b', 'cls', measure.entropy, entropy_impurity, False)
    #~ print interval(data, 'b', 'cls', measure.giniidx, giniidx_impurity, False)
    #~ print interval(data, 'b', 'cls', measure.cls_err, cls_err_impurity, False)
    #~ print

    #~ print 'split'
    #~ print ordinal(data, 'c', 'cls', measure.entropy, entropy_impurity)
    #~ print ordinal(data, 'c', 'cls', measure.giniidx, giniidx_impurity)
    #~ print ordinal(data, 'c', 'cls', measure.cls_err, cls_err_impurity)
    #~ print 'nosplit'
    #~ print ordinal(data, 'c', 'cls', measure.entropy, entropy_impurity, False)
    #~ print ordinal(data, 'c', 'cls', measure.giniidx, giniidx_impurity, False)
    #~ print ordinal(data, 'c', 'cls', measure.cls_err, cls_err_impurity, False)
    #~ print

    #~ print 'split'
    #~ print nominal(data, 'c', 'cls', measure.entropy, entropy_impurity)
    #~ print nominal(data, 'c', 'cls', measure.giniidx, giniidx_impurity)
    #~ print nominal(data, 'c', 'cls', measure.cls_err, cls_err_impurity)
    #~ print 'nosplit'
    #~ print nominal(data, 'c', 'cls', measure.entropy, entropy_impurity, False)
    #~ print nominal(data, 'c', 'cls', measure.giniidx, giniidx_impurity, False)
    #~ print nominal(data, 'c', 'cls', measure.cls_err, cls_err_impurity, False)
    #~ print

if __name__ == '__main__':
    __test__()
