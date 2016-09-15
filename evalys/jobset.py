# coding: utf-8
from __future__ import unicode_literals, print_function
import pandas as pd
from evalys.visu import plot_gantt


def ids2itvs(ids):
    """Convert list of int to list of intervals"""
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
        intervals = ids2itvs(res)

    return intervals


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


def interval_set_to_string(intervals):
    return ' '.join(['{}-{}'.format(begin, end) for (begin, end) in intervals])


class JobSet(object):
    def __init__(self, df):
        self.res_set = {}
        self.df = df

        # compute resources intervals
        for i, row in self.df.iterrows():
            raw_res_str = row['allocated_processors']
            self.res_set[row['jobID']] = string_to_interval_set(
                str(raw_res_str))

        # compute resources bounds (+1 for max because of visu alignment
        # over the job number line
        self.res_bounds = (
            min([b for x in self.res_set.values() for (b, e) in x]),
            max([e for x in self.res_set.values() for (b, e) in x]) + 1)

    __converters = {
        'jobID': str,
        'allocated_processors': str,
    }

    @classmethod
    def from_csv(cls, filename):
        df = pd.read_csv(filename, converters=cls.__converters)
        return cls(df)

    def gantt(self, ax, title):
        plot_gantt(self, ax, title)
