"""
Functions to manage and convert and intervals set.

An interval is tuple (begin, end). An interval of 1 element where eID is the
element ID is formated (eID, eID).

An interval set is a list of not overlapping intervals.
"""

#
# Conversion operations
#

#
# String conversion
#


def interval_set_to_string(intervals):
    return ' '.join(['{}-{}'.format(begin, end) for (begin, end) in intervals])


def _ids_to_itervals(ids):
    """Convert list of ID (int) to list of intervals"""
    itvs = []
    if ids:
        b = ids[0]
        e = ids[0]
        for i in ids:
            if i > (e + 1):  # end itv and prepare new itv
                itvs.append((b, e))
                b = i
            e = i
        itvs.append((b, e))

    return itvs


def string_to_interval_set(s):
    """Transforms a string like "1 2 3 7-9 13" into interval sets like
       [(1,3), (7,9), (13,13)]"""
    intervals = []
    if not s:
        print("Warning: Interval set is empty")
        return []
    try:
        res_str = s.split(' ')
        if '-' in (' ').join(res_str):
            # it is already intervals so get it directly
            for inter in res_str:
                try:
                    (begin, end) = inter.split('-')
                    intervals.append((int(begin), int(end)))
                except ValueError:
                    intervals.append((int(inter), int(inter)))
        else:
            res = sorted([int(x) for x in res_str])
            intervals = _ids_to_itervals(res)
    except ValueError:
        print("Bad interval format. Parsed string is: {}".format(s))

    return intervals

#
# Set conversion
#


def interval_set_to_set(intervals):
    s = set()

    for (begin, end) in intervals:
        for x in range(begin, end+1):
            s.add(x)

    return s


def set_to_interval_set(s):
    intervals = []
    l = list(s)
    l.sort()

    if len(l) > 0:
        i = 0
        current_interval = [l[i], l[i]]
        i += 1

        while i < len(l):
            if l[i] == current_interval[1] + 1:
                current_interval[1] = l[i]
            else:
                intervals.append(current_interval)
                current_interval = [l[i], l[i]]
            i += 1

        if current_interval not in intervals:
            intervals.append(tuple(current_interval))

    return intervals


#
# Ensemble operations
#


def difference(itvs1, itvs2):
    """ returns the difference between an interval set and an other

    >>> difference([(1, 1), (3, 4)], [(1, 2), (4, 7)])
    [(3, 3)]
    """
    lx = len(itvs1)
    ly = len(itvs2)
    i = 0
    k = 0
    itvs = []

    while (i < lx) and (lx > 0):
        x = itvs1[i]
        if (k == ly):
            itvs.append(x)
            i += 1
        else:
            y = itvs2[k]
            # y before x w/ no overlap
            if (y[1] < x[0]):
                k += 1
            else:
                # x before y w/ no overlap
                if (y[0] > x[1]):
                    itvs.append(x)
                    i += 1
                else:
                    if (y[0] > x[0]):
                        if (y[1] < x[1]):
                            # x overlap totally y
                            itvs.append((x[0], y[0] - 1))
                            itvs1[i] = (y[1] + 1, x[1])
                            k += 1
                        else:
                            # x overlap partially
                            itvs.append((x[0], y[0] - 1))
                            i += 1
                    else:
                        if (y[1] < x[1]):
                            # x overlap partially
                            itvs1[i] = (y[1] + 1, x[1])
                            k += 1
                        else:
                            # y overlap totally x
                            i += 1

    return itvs


def aggregate(itvs):
    """Aggregate not overlapping intervals (intersect must be empty) to remove gap.

    >>> aggregate([(1, 2), (3, 4)])
    [(1, 4)]
    """
    if itvs is []:
        return itvs

    # TODO check overlapping

    res = []
    lg = len(itvs)
    i = 1
    a, b = itvs[i - 1]
    while True:
        if i == lg:
            res.append((a, b))
            return res
        else:
            x, y = itvs[i]
            if x == (b + 1):
                b = y
            else:
                res.append((a, b))
                a, b = x, y
            i += 1


def intersection(itvs1, itvs2):
    """Returns an interval set that is an intersection of itvs1 and itvs2.

    >>> intersect([(1, 2), (4, 5)], [(1, 3), (5, 7)])
    [(1, 2), (5, 5)]
    >>> intersect([(2, 3), (5, 7)], [(1, 1), (4, 4)])
    []
    """

    lx = len(itvs1)
    ly = len(itvs2)
    i = 0
    k = 0
    itvs = []

    while (i < lx) and (lx > 0) and (ly > 0):
        x = itvs1[i]
        if (k == ly):
            break
        else:
            y = itvs2[k]

        # y before x w/ no overlap
        if (y[1] < x[0]):
            k += 1
        else:

            # x before y w/ no overlap
            if (y[0] > x[1]):
                i += 1
            else:

                if (y[0] >= x[0]):
                    if (y[1] <= x[1]):
                        itvs.append(y)
                        k += 1
                    else:
                        itvs.append((y[0], x[1]))
                        i += 1
                else:
                    if (y[1] <= x[1]):
                        itvs.append((x[0], y[1]))
                        k += 1
                    else:
                        itvs.append(x)
                        i += 1
    return itvs


def union(itvs1, itvs2):
    """ Returns the union of two interval sets

    >>> union([(1, 1), (3, 4)], [(1, 2), (4, 7)])
    [(1, 7)]
    """

    intersect = intersection(itvs1, itvs2)
    diff12 = difference(itvs1, itvs2)
    diff21 = difference(itvs2, itvs1)
    union = aggregate(sorted(intersect + diff12 + diff21))
    return union
