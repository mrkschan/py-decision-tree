# utility function for computing impurity of a given dataset

def entropy(dataset, cls_attr):
    '''
    Infomation Theory - Entropy
        Sum( Pi * log_2(Pi) )
        dataset  - the data set to compute the impurity
        cls_attr - the attribute that determines the class of tuple
    '''
    import math

    freq = {}       # class freq holder

    # for each tuple,
    # accumlates the freq of the class of that tuple belongs to
    for tuple in data:
        cls = tuple[cls_attr]
        if freq.has_key(cls): freq[cls] += 1
        else: freq[cls] = 1.0

    # compute Sum( Pi * log_2(Pi) )
    size = len(dataset)
    __entropy = .0
    for f in freq.values():
        __entropy += (-f / size) * math.log(f / size, 2)

    return __entropy

def gini(dataset, attribute):
    '''
    Gini Index
        1 - Sum( P(Class_k)^2 )
    '''

def cls_err(dataset, attribute):
    '''
    Classification Error
        1 - Max( P(Class_k) )
    '''
