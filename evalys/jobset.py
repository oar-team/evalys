# coding: utf-8
from __future__ import unicode_literals, print_function
import pandas as pd
from evalys.visu import plot_gantt
from evalys.interval_set import \
        union, difference, intersection, string_to_interval_set, \
        interval_set_to_string, total


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

    columns = ['jobID',
               'submission_time',
               'requested_number_of_processors',
               'requested_time',
               'success',
               'starting_time',
               'execution_time',
               'finish_time',
               'waiting_time',
               'turnaround_time',
               'stretch',
               'allocated_processors']

    @classmethod
    def from_csv(cls, filename):
        df = pd.read_csv(filename, converters=cls.__converters)
        return cls(df)

    def gantt(self, ax, title):
        plot_gantt(self, ax, title)

    def utilisation(self):
        return total([self.res_bounds]) \
                - self.free_intervals()['proc_alloc'].apply(total)

    def free_intervals(self):
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
        first_row = [0, [self.res_bounds]]
        free_interval_serie = pd.DataFrame(columns=event_columns)
        free_interval_serie.loc[0] = first_row
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

    def free_slots(self):
        # slots_time contains tuple of
        # (slot_begin_time,free_resources_intervals)
        free_interval_serie = self.free_intervals()
        slots_time = [(free_interval_serie.time[0],
                      [self.res_bounds])]
        columns = ['jobID', 'allocated_processors',
                   'starting_time', 'finish_time', 'execution_time',
                   'submission_time']
        free_slots_df = pd.DataFrame(columns=columns)
        prev_free_itvs = [self.res_bounds]
        slots = 0

        for _, curr_row in free_interval_serie.iterrows():
            new_slots_time = []
            curr_time = curr_row.time
            taken_resources = difference(prev_free_itvs,
                                         curr_row.proc_alloc)
            freed_resources = difference(curr_row.proc_alloc,
                                         prev_free_itvs)
            assert not (freed_resources and taken_resources)
            if taken_resources:
                # slot ends: store it and update free slot
                for begin_time, itvs in slots_time:
                    to_update = intersection(itvs, taken_resources)
                    if to_update != []:
                        # store new slots
                        slots = slots + 1
                        new_slot = [str(slots),
                                    interval_set_to_string(to_update),
                                    begin_time,
                                    curr_time,
                                    curr_time - begin_time,
                                    begin_time]
                        free_slots_df.loc[slots] = new_slot
                        # remove free slots
                        free_res = difference(itvs, to_update)
                        if free_res != []:
                            new_slots_time.append((begin_time, free_res))
                    else:
                        new_slots_time.append((begin_time, itvs))

            if freed_resources:
                # slots begin: udpate free slot
                if not new_slots_time:
                    new_slots_time = slots_time
                new_slots_time.append((curr_time, freed_resources))

            # update previous
            prev_free_itvs = curr_row.proc_alloc
            # clean slots_free
            slots_time = new_slots_time
        return free_slots_df
