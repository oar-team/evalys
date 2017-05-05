# coding: utf-8
from __future__ import unicode_literals, print_function
import pandas as pd
from intsetwrap import string_to_interval_set, interval_set_to_set, \
                          set_to_interval_set, interval_set_to_string

class MachineStatesChanges(object):
    def __init__(self, filename, time_min=None, time_max=None):
        self.df = pd.read_csv(filename)
        self.check(filename)
        self.df.drop_duplicates(keep='last', subset='time', inplace=True)

        # Drop values outside the time window
        if time_min is not None:
            self.df = self.df.loc[self.df['time'] >= time_min]
        if time_max is not None:
            self.df = self.df.loc[self.df['time'] <= time_max]

    def check(self, filename):
        expected_columns = ['time', 'nb_sleeping', 'nb_switching_on',
                            'nb_switching_off', 'nb_idle', 'nb_computing']

        # A few checks about the file format
        for col_name in expected_columns:
            assert(col_name in self.df), \
            "Invalid input file '{}': should contain a '{}' column".format(filename, col_name)

        assert(self.df['time'].count() > 0), \
            "Invalid input file '{}': should contain at least 1 row".format(filename)

        # The number of machines should be consistent
        self.df['total'] = self.df['nb_sleeping'] + self.df['nb_switching_on'] + \
                           self.df['nb_switching_off'] + self.df['nb_idle'] + \
                           self.df['nb_computing']

        assert(len(set(self.df['total'])) == 1), \
            "Invalid input file '{}': the sum of all values should be the same " \
            "for all rows, but these values are found: {}".format(filename, set(self.df['total']))



'''
time,nb_sleeping,nb_switching_on,nb_switching_off,nb_idle,nb_computing
0,0,0,0,31,1
4.70916,0,0,0,29,3
16.0039,0,0,0,28,4
38.8363,0,0,0,24,8
54.1959,0,0,0,23,9
70.3507,0,0,0,22,10
74.7683,0,0,0,26,6
88.51,0,0,0,27,5
95.4489,0,0,0,23,9
'''
