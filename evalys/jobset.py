# coding: utf-8
from __future__ import unicode_literals, print_function
import pandas as pd
from evalys.visu import plot_gantt
from evalys.interval_set import \
        union, difference, string_to_interval_set


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
            max([e for x in self.res_set.values() for (b, e) in x]))

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

    def free_slots(self):
        import numpy as np
        df = self.df

        # Create a list of start and stop event associated to the proc
        # allocation:
        # Free -> Used : grab = 1
        # Used -> Free : grab = 0
        event_columns = ['time', 'proc_alloc', 'grab']
        start_event_df = pd.concat([df['starting_time'],
                                    df['allocated_processors'],
                                    pd.Series(np.ones(len(df), dtype=bool))],
                                   axis=1)
        start_event_df.columns = event_columns
        # Stop event have zero in grab
        stop_event_df = pd.concat([df['finish_time'],
                                   df['allocated_processors'],
                                   pd.Series(np.zeros(len(df), dtype=bool))],
                                  axis=1)
        stop_event_df.columns = event_columns

        # merge events and sort them
        event_df = start_event_df.append(
            stop_event_df,
            ignore_index=True).sort_values(by='time').reset_index(drop=True)

        # All resources are free at the beginning
        event_columns = ['time', 'proc_alloc']
        first_row = event_df.time[0], [self.res_bounds]
        free_interval_serie = pd.DataFrame(
            [first_row], index=['0'], columns=event_columns)
        for index, row in event_df.iterrows():
            current_itv = free_interval_serie.ix[index]['proc_alloc']
            if row.grab:
                new_itv = difference(current_itv,
                                     string_to_interval_set(row.proc_alloc))
            else:
                new_itv = union(current_itv,
                                string_to_interval_set(row.proc_alloc))
            new_row = [row.time, new_itv]
            free_interval_serie.loc[index + 1] = new_row
        return free_interval_serie
