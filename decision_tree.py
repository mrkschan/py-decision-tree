# decision tree

class TreeNode:
    cls_attr = None # shared

    def __init__(self):
        self.cls      = None # only leaf node contains class label
        self.cluster  = None # only leaf node contains cluster

        self.pivot    = None # only internal node contains pivot
        self.attr     = None # only internal node contains attr for decision
        self.branches = None # only internal node contains branches to TreeNode

        self.depth    = None


    def size(self):
        if self.cls is not None:
            return 1
        else:
            s = 0
            for b in self.branches.values():
                s += b.size()
            return s


    def majority(self):
        '''
        Interpret the class of self containted cluster, based on majority rule
        '''
        freq = {}

        for instance in self.cluster:
            cls = instance[self.cls_attr]
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


    def probe_deepest(self):
        if self.cls is not None:
            return self.depth
        else:
            deepest = 0
            for b in self.branches.values():
                deepest = max(deepest, b.probe_deepest())
            return deepest


    def merge_deepest(self, deepest):
        if self.depth + 1 == deepest:
            # do merge
            self.cluster = []
            for b in self.branches.values():
                self.cluster += b.cluster

            self.cls      = self.majority()
            self.pivot    = self.attr = None
            self.branches = None # gc branches
        else:
            self.merge_deepest(deepest)


    def trim_last_lvl(self):
        deepest = self.probe_deepest()
        self.merge_deepest(deepest)


def build_tree(dataset, cls_attr, attr_strategy, measure=None, threshold=.0, quiet=True, _depth=0):
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
        measure = m.entropy

    # if no more element for decision
    # return a leaf node for unclassified
    if len(dataset) == 0:
        leaf         = TreeNode()
        leaf.depth   = _depth
        leaf.cluster = []
        leaf.cls     = 'Un-classified'
        return leaf

    # if no more attribute for decision
    # return a leaf node by majority
    if len(attr_strategy) == 0:
        leaf          = TreeNode()
        leaf.depth    = _depth
        leaf.cluster  = dataset
        leaf.cls_attr = cls_attr
        leaf.cls      = leaf.majority()
        return leaf

    # compute impurity for further processing
    impurity = measure(dataset, cls_attr)

    # if impurity of dataset is 0 ==> all instances belong to same class
    # return a leaf node as of that class
    if impurity == 0:
        leaf          = TreeNode()
        leaf.depth    = _depth
        leaf.cluster  = dataset
        leaf.cls_attr = cls_attr
        leaf.cls      = dataset[0][cls_attr]
        return leaf

    # if impurity of dataset is below threshold
    # return a leaf node by majority
    elif impurity < threshold:
        leaf          = TreeNode()
        leaf.depth    = _depth
        leaf.cluster  = dataset
        leaf.cls_attr = cls_attr
        leaf.cls      = leaf.majority()
        return leaf

    # pick a partition strategy by the best purity gain
    else:
        # get all gains
        gain_pivot_pairs = {}
        for attr, strategy, _cmp in attr_strategy:
            gain_pivot_pairs[attr] = strategy(
                dataset, attr, cls_attr, measure, impurity, _cmp)

        # retrieve best gain
        best_gain = .0
        best_attr = None
        pivot     = None
        for attr, gain_pivot in gain_pivot_pairs.items():
            if gain_pivot[1] > best_gain:
                best_attr = attr
                best_gain = gain_pivot[1]
                pivot     = gain_pivot[0]

        if not quiet:
            if isinstance(pivot, list):
                print 'impurity: %s, gain: %s, attr: %s, decision: by %s' \
                    % (impurity, best_gain, best_attr, pivot)
            else:
                print 'impurity: %s, gain: %s, attr: %s, decision: val < %s' \
                    % (impurity, best_gain, best_attr, pivot)

        if best_gain - .0 < .0000001:
            # early return for gaining not much purity
            leaf          = TreeNode()
            leaf.depth    = _depth
            leaf.cluster  = dataset
            leaf.cls_attr = cls_attr
            leaf.cls      = leaf.majority()
            return leaf


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
        tree.depth    = _depth
        tree.pivot    = pivot
        tree.attr     = best_attr
        tree.branches = {}

        if isinstance(pivot, list):
            # multi-branches
            for val, c in clusters.items():
                tree.branches[val] = build_tree(c, cls_attr, attr_strategy, measure, threshold, quiet, _depth+1)
        else:
            # binary-branches
            tree.branches[0] = build_tree(clusters[0], cls_attr, attr_strategy, measure, threshold, quiet, _depth+1)
            tree.branches[1] = build_tree(clusters[1], cls_attr, attr_strategy, measure, threshold, quiet, _depth+1)

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


def build_postpruning_tree(testset, validset, cls_attr, attr_strategy, measure=None, penality=.5, quiet=True):
    '''
    Build a decision tree by post-pruning method
        Post-pruning by err-estimate on validation set
        err-estimate =
            err-instances + tree-size * size-penality / validation-set-size

        Stop pruning tree when lower-lvl-err-estimate < higher-lvl-err-estimate
    '''
    tree = build_tree(testset, cls_attr, attr_strategy, measure, .0, quiet)

    return tree


def __test__():
    import measure, strategy, datetime

    f = open('poker-hand-training.data')
    data = []
    for l in f.readlines():
        data.append(l.strip().split(','))
    f.close()


    tree = build_tree(data, 10, [
        (0, strategy.nominal,  None),
        (1, strategy.interval, None),
        (2, strategy.nominal,  None),
        (3, strategy.interval, None),
        (4, strategy.nominal,  None),
        (5, strategy.interval, None),
        (6, strategy.nominal,  None),
        (7, strategy.interval, None),
        (8, strategy.nominal,  None),
        (9, strategy.interval, None),
    ], quiet=False, threshold=.0)

    print 'Tree size: %d' % tree.size()

    #~ print 'Test tree:'
    #~ print make_decision(tree, {'a': 5, 'b': datetime.date(2006, 12, 5), 'c': 'B', 'd': 'C'})
    #~ print make_decision(tree, {'a': 1, 'b': datetime.date(2006, 12, 5), 'c': 'B', 'd': 'C'})
    #~ print make_decision(tree, {'a': 5, 'b': datetime.date(2006, 12, 5), 'c': 'D', 'd': 'B'})
    #~ print make_decision(tree, {'a': 5, 'b': datetime.date(2006, 12, 5), 'c': 'D', 'd': 'A'})
    #~ print make_decision(tree, {'a': 5, 'b': datetime.date(2006, 12, 5), 'c': 'D', 'd': 'C'})

    print

    #~ testset  = data[:len(data)/2]
    #~ validset = data[len(data)/2:]
    #~ tree = build_postpruning_tree(testset, validset, 10, [
        #~ (0, strategy.nominal,  None),
        #~ (1, strategy.interval, None),
        #~ (2, strategy.nominal,  None),
        #~ (3, strategy.interval, None),
        #~ (4, strategy.nominal,  None),
        #~ (5, strategy.interval, None),
        #~ (6, strategy.nominal,  None),
        #~ (7, strategy.interval, None),
        #~ (8, strategy.nominal,  None),
        #~ (9, strategy.interval, None),
    #~ ], quiet=False)

    #~ print 'Tree size: %d' % tree.size()

    #~ print 'Test tree:'
    #~ print make_decision(tree, {'a': 5, 'b': datetime.date(2006, 12, 5), 'c': 'B', 'd': 'C'})
    #~ print make_decision(tree, {'a': 1, 'b': datetime.date(2006, 12, 5), 'c': 'B', 'd': 'C'})
    #~ print make_decision(tree, {'a': 5, 'b': datetime.date(2006, 12, 5), 'c': 'D', 'd': 'B'})
    #~ print make_decision(tree, {'a': 5, 'b': datetime.date(2006, 12, 5), 'c': 'D', 'd': 'A'})
    #~ print make_decision(tree, {'a': 5, 'b': datetime.date(2006, 12, 5), 'c': 'D', 'd': 'C'})

if __name__ == '__main__':
    __test__()
