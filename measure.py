# utility function for computing impurity of a given dataset

def entropy(dataset, cls_attr):
    '''
    Infomation Theory - Entropy
        -Sum( Pi * log_2(Pi) )
        dataset  - the data set to compute the impurity
        cls_attr - the attribute that determines the class of tuple
    '''
    import math

    freq = {}   # class freq holder

    # for each tuple,
    # accumlates the freq of the class of that tuple belongs to
    for tuple in dataset:
        cls_label = tuple[cls_attr]
        if freq.has_key(cls_label):
            freq[cls_label] += 1
        else:
            freq[cls_label] = 1.0

    # compute -Sum( Pi * log_2(Pi) )
    size = len(dataset)
    sum = .0
    for f in freq.values():
        sum += (-f / size) * math.log(f / size, 2)

    return sum


def gini(dataset, cls_attr):
    '''
    Gini Index
        1 - Sum( P(Class_k)^2 )
    '''
    freq = {}   # class freq holder

    # for each tuple,
    # accumlates the freq of the class of that tuple belongs to
    for tuple in dataset:
        cls_label = tuple[cls_attr]
        if freq.has_key(cls_label):
            freq[cls_label] += 1
        else:
            freq[cls_label] = 1.0

    # compute Sum( P(Class_k)^2 )
    size = len(dataset)
    sum = .0
    for f in freq.values():
        sum += (f / size) ** 2

    return 1 - sum


def cls_err(dataset, cls_attr):
    '''
    Classification Error
        1 - Max( P(Class_k) )
    '''
    freq = {}   # class freq holder

    # for each tuple,
    # accumlates the freq of the class of that tuple belongs to
    for tuple in dataset:
        cls_label = tuple[cls_attr]
        if freq.has_key(cls_label):
            freq[cls_label] += 1
        else:
            freq[cls_label] = 1.0

    # find max prob
    size = len(dataset)
    max_prob = .0
    for f in freq.values():
        max_prob = max(max_prob, f/size)

    return 1 - max_prob
