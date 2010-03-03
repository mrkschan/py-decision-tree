# decision tree

class TreeNode:
    def __init__(self):
        self.branches = None
        self.pivot    = None
        self.attr     = None
        self.cls      = None

def majority(dataset, cls_attr):
    '''
    Return the class of the given dataset based on majority rule
    '''
    freq = {}

    for instance in dataset:
        cls = instance[cls_attr]
        if freq.has_key(cls):
            freq[cls] += 1
        else:
            freq[cls] = 1

    max_cls = None
    max_f   = .0
    for cls, f in freq.items():
        if f > max_f:
            max_cls = cls
            max_f   = f

    return max_cls

def build_tree(dataset, cls_attr, attr_strategy, measure=None, threshold=None, quiet=True):
    '''
    Build a tree of decisions based on given the dataset to carry classification
    Each tree node is a function to partition the dataset
    Each leave node is a class
        - attr_strategy is a list of tuple: [(attr, strategy, sorting fn), ...]
    '''
    if threshold is None:
        threshold = .0

    if measure is None:
        import measure as m
        measure = m.cls_err

    # if no more element for decision
    # return a leaf node for unclassified
    if len(dataset) == 0:
        leaf = TreeNode()
        leaf.cls = 'Un-classified'
        return leaf

    # if no more attribute for decision
    # return a leaf node by majority
    if len(attr_strategy) == 0:
        leaf = TreeNode()
        leaf.cls = majority(dataset, cls_attr)
        return leaf

    # compute impurity for further processing
    impurity = measure(dataset, cls_attr)

    # if impurity of dataset is 0 ==> all instances belong to same class
    # return a leaf node as of that class
    if impurity == 0:
        leaf = TreeNode()
        leaf.cls = dataset[0][cls_attr]
        return leaf

    # if impurity of dataset is below threshold
    # return a leaf node by majority
    elif impurity < threshold:
        leaf = TreeNode()
        leaf.cls = majority(dataset, cls_attr)
        return leaf

    # pick a partition strategy by the best purity gain
    else:
        # get all gains
        gain_pivot_pairs = {}
        for attr, strategy, _cmp in attr_strategy:
            gain_pivot_pairs[attr] = strategy(
                dataset, attr, cls_attr, measure, impurity, _cmp)

        # retrieve best gain
        best_gain = -1
        best_attr = None
        pivot     = None
        for attr, gain_pivot in gain_pivot_pairs.items():
            if gain_pivot[1] > best_gain:
                best_attr = attr
                best_gain = gain_pivot[1]
                pivot     = gain_pivot[0]

        if not quiet:
            if isinstance(pivot, list):
                print 'gain: %s, attr: %s, decision: by %s' \
                    % (best_gain, best_attr, pivot)
            else:
                print 'gain: %s, attr: %s, decision: val < %s' \
                    % (best_gain, best_attr, pivot)

        # remove best attribute from further levels of decision
        attr_strategy = [i for i in attr_strategy if i[0] != best_attr]

        # perform clustering for further levels of decision
        clusters = {}
        if isinstance(pivot, list):
            # multiway clustering
            for instance in dataset:
                val = instance[best_attr]
                if not clusters.has_key(val):
                    clusters[val] = []
                clusters[val].append(instance)
        else:
            # binary clustering
            for instance in dataset:
                val = instance[best_attr]
                if val < pivot:
                    if not clusters.has_key(1):
                        clusters[1] = []
                    clusters[1].append(instance)
                else:
                    if not clusters.has_key(0):
                        clusters[0] = []
                    clusters[0].append(instance)

        tree = TreeNode()
        tree.pivot    = pivot
        tree.attr     = best_attr
        tree.branches = {}

        if isinstance(pivot, list):
            # multi-branches
            for val, c in clusters.items():
                tree.branches[val] = build_tree(c, cls_attr, attr_strategy, measure, threshold, quiet)
        else:
            # binary-branches
            tree.branches[0] = build_tree(clusters[0], cls_attr, attr_strategy, measure, threshold, quiet)
            tree.branches[1] = build_tree(clusters[1], cls_attr, attr_strategy, measure, threshold, quiet)

        #~ if not quiet:
            #~ if isinstance(pivot, list):
                #~ for val in pivot:
                    #~ if tree.branches[val].pivot is None:
                        #~ print 'class: %s' % tree.branches[val].cls
                    #~ else:
                        #~ print 'class: decide!'
            #~ else:
                #~ if tree.branches[1].pivot is None:
                    #~ print 'class: %s' % tree.branches[1].cls
                #~ else:
                    #~ print 'class: decide!'
                #~ if tree.branches[0].pivot is None:
                    #~ print 'class: %s' % tree.branches[0].cls
                #~ else:
                    #~ print 'class: decide!'
            #~ print

        return tree


def make_decision(tree, instance):
    '''
    Make classification based on the TreeNode structure
    '''
    node = tree
    while node.pivot is not None:
        pivot = node.pivot
        attr  = node.attr
        val   = instance[attr]
        if isinstance(pivot, list):
            if node.branches.has_key(val):
                node = node.branches[val]
            else:
                node     = TreeNode()
                node.cls = 'Un-classified'
        else:
            if val < pivot:
                if node.branches.has_key(1):
                    node = node.branches[1]
                else:
                    node     = TreeNode()
                    node.cls = 'Un-classified'
            else:
                if node.branches.has_key(0):
                    node = node.branches[0]
                else:
                    node     = TreeNode()
                    node.cls = 'Un-classified'
    return node.cls


def __test__():
    import measure, strategy, datetime

    data = [
        {'a': 1, 'b': datetime.date(2007, 12, 5), 'c': 'A', 'd': 'A', 'cls': 2},
        {'a': 1, 'b': datetime.date(2007, 12, 5), 'c': 'E', 'd': 'A', 'cls': 2},
        {'a': 3, 'b': datetime.date(2009, 12, 5), 'c': 'B', 'd': 'A', 'cls': 1},
        {'a': 3, 'b': datetime.date(2009, 12, 5), 'c': 'D', 'd': 'A', 'cls': 1},
        {'a': 9, 'b': datetime.date(2008, 12, 5), 'c': 'D', 'd': 'A', 'cls': 3},
        {'a': 2, 'b': datetime.date(2003, 12, 5), 'c': 'A', 'd': 'C', 'cls': 1},
        {'a': 7, 'b': datetime.date(2004, 12, 5), 'c': 'A', 'd': 'C', 'cls': 1},
        {'a': 7, 'b': datetime.date(2004, 12, 5), 'c': 'E', 'd': 'C', 'cls': 1},
        {'a': 2, 'b': datetime.date(2010, 12, 5), 'c': 'C', 'd': 'C', 'cls': 3},
        {'a': 9, 'b': datetime.date(2010, 12, 5), 'c': 'D', 'd': 'B', 'cls': 3},
    ]

    tree = build_tree(data, 'cls', [
        ('a', strategy.ratio,    None),
        ('b', strategy.interval, None),
        ('c', strategy.ordinal,  None),
        ('d', strategy.nominal,  None),
    ], quiet=False)

    print 'Test tree:'
    print make_decision(tree, {'a': 5, 'b': datetime.date(2006, 12, 5), 'c': 'B', 'd': 'C'})
    print make_decision(tree, {'a': 1, 'b': datetime.date(2006, 12, 5), 'c': 'B', 'd': 'C'})
    print make_decision(tree, {'a': 5, 'b': datetime.date(2006, 12, 5), 'c': 'D', 'd': 'B'})
    print make_decision(tree, {'a': 5, 'b': datetime.date(2006, 12, 5), 'c': 'D', 'd': 'A'})
    print make_decision(tree, {'a': 5, 'b': datetime.date(2006, 12, 5), 'c': 'D', 'd': 'C'})

if __name__ == '__main__':
    __test__()
