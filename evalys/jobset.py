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


class JobSet(object):
    def __init__(self, filename):
        # self.load_cvs(filename)
        self.res_set = {}
        self.df = pd.read_csv(filename)

        # compute resources intervals
        for i, row in self.df.iterrows():
            res_str = row['allocated_processors'].split(' ')
            if '-' in (' ').join(res_str):
                intervals = []
                # it is already intervals so get it directly
                for inter in res_str:
                    try:
                        (begin, first) = inter.split('-')
                        intervals.append((int(begin), int(first)))
                    except ValueError:
                        intervals.append((int(inter), int(inter)))
                self.res_set[row['jobID']] = intervals

            else:
                res = sorted([int(x) for x in res_str])
                self.res_set[row['jobID']] = ids2itvs(res)
        # compute resources bounds (+1 for max because of visu alignment
        # over the job number line
        self.res_bounds = (
            min([b for x in self.res_set.values() for (b, e) in x]),
            max([e for x in self.res_set.values() for (b, e) in x]) + 1)

    def gantt(self, ax, title):
        plot_gantt(self, ax, title)
