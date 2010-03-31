# utility function for computing impurity of a given dataset

def __accumulate_freq(freq, cls_label):
    #~ if freq.has_key(cls_label): freq[cls_label] += 1
    if cls_label in freq.keys():
        freq[cls_label] += 1
    else:
        freq[cls_label] = 1

def entropy(dataset, cls_attr):
    '''
    Infomation Theory - Entropy
        -Sum( Pi * log_2(Pi) )
        dataset  - the data set to compute the impurity
        cls_attr - the attribute that determines the class of instance
    '''
    import math

    freq = {}   # class freq holder

    # for each instance,
    # accumlates the freq of the class of that instance belongs to
    size = float(len(dataset))
    for instance in dataset:
        __accumulate_freq(freq, instance[cls_attr])

    # compute -Sum( Pi * log_2(Pi) )
    sum  = .0
    for f in freq.values():
        sum += (-f / size) * math.log(f / size, 2)

    return sum


def giniidx(dataset, cls_attr, indices=None):
    '''
    Gini Index
        1 - Sum( P(Class_k)^2 )
    '''
    freq = {}   # class freq holder

    # for each instance,
    # accumlates the freq of the class of that instance belongs to
    size = float(len(dataset))
    for instance in dataset:
        __accumulate_freq(freq, instance[cls_attr])

    # compute Sum( P(Class_k)^2 )
    sum = .0
    for f in freq.values():
        sum += (f / size) ** 2

    return 1 - sum


def cls_err(dataset, cls_attr, indices=None):
    '''
    Classification Error
        1 - Max( P(Class_k) )
    '''
    freq = {}   # class freq holder

    # for each instance,
    # accumlates the freq of the class of that instance belongs to
    size = float(len(dataset))
    for instance in dataset:
        __accumulate_freq(freq, instance[cls_attr])

    # find max prob
    max_prob = .0
    for f in freq.values():
        max_prob = max(max_prob, f/size)

    return 1 - max_prob
