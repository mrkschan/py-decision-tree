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
    cluster = {}
    for idx in xrange(0, size):
        instance = dataset[idx]
        val = instance[attr]

        if not cluster.has_key(val):
            cluster[val] = []

        cluster[val].append(instance)

    gain = impurity

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

    return gain, cluster.keys(), cluster


def get_pivot_ordinal(idx, dataset, attr):
    return dataset[idx][attr]

def get_pivot_interval(idx, dataset, attr):
    return dataset[idx][attr]

def get_pivot_ratio(idx, dataset, attr):
    return float(dataset[idx][attr] - dataset[idx-1][attr]) / 2


def binary_partitioning(s_idx, e_idx, dataset, attr, cls_attr, measure, impurity, normalize, size, get_pivot):
    bg = .0
    bp = None
    bi = 1

    for idx in xrange(s_idx, e_idx):
        if dataset[idx - 1][attr] == dataset[idx][attr]:
            # skip same attribute value, consider the idx for last same value only
            continue

        pivot = get_pivot(idx, dataset, attr)

        head_ratio     = float(idx) / size
        head_impurity  = measure(dataset, cls_attr, xrange(0, idx))

        tail_ratio     = float(size - idx) / size
        tail_impurity  = measure(dataset, cls_attr, xrange(idx, size))

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
            bi = idx
    # End for: find partial best gain

    return bg, bp, bi

def partitioning_wrapper(args):
    return binary_partitioning(*args)

#~ import os, multiprocessing as mp
#~ PROCESSES = os.sysconf("SC_NPROCESSORS_CONF")
#~ PROCESSES = 1
#~ POOL = mp.Pool(processes=PROCESSES)
def partitioning(dataset, attr, cls_attr, measure, impurity, normalize, get_pivot):
    '''
    partitioning by multi-processes
    '''
    size = len(dataset)

    best_gain, best_pivot, best_idx = binary_partitioning(0, size, dataset, attr, cls_attr, measure, impurity, normalize, size, get_pivot)

    #~ args   = []
    #~ pos    = 1
    #~ offset = size / PROCESSES
    #~ for i in xrange(0, PROCESSES):
        #~ last = pos + offset
        #~ if pos + offset > size: last = size

        #~ args.append(
            #~ (pos, last, dataset, attr, cls_attr, measure, impurity, normalize, size, get_pivot)
        #~ )
        #~ pos = last


    #~ best_gain   = .0
    #~ best_pivot  = None
    #~ best_idx    = 1
    #~ result_iter = POOL.imap(partitioning_wrapper, args)
    #~ for g, p, i in result_iter:
        #~ if g > best_gain:
            #~ best_gain  = g
            #~ best_pivot = p
            #~ best_idx   = i

    return best_gain, best_pivot, {1: dataset[:best_idx], 0: dataset[best_idx:]}


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

    # create clone sorted by attr value
    dataset = sorted(dataset, cmp=_cmp)

    return partitioning(dataset, attr, cls_attr, measure, impurity, normalize, get_pivot_ordinal)

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

    # create clone sorted by attr value
    dataset = sorted(dataset, cmp=_cmp)

    return partitioning(dataset, attr, cls_attr, measure, impurity, normalize, get_pivot_interval)

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

    # create clone sorted by attr value
    dataset = sorted(dataset, cmp=_cmp)

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
