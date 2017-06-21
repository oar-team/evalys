# coding: utf-8
from __future__ import unicode_literals, print_function
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from evalys import visu
from procset import ProcInt, ProcSet
from evalys.metrics import compute_load, load_mean, fragmentation_reis


class JobSet(object):
    '''
    A JobSet is a set of jobs with it state, its time properties and
    the resources it is associated with.

    It takes a dataframe in input that are intended to have the columns
    defined in :py::`JobSet.columns`.

    The `allocated_processors` one should contain the string representation
    of an interval set of the allocated resources for the given job, i.e.
    for this interval::

        # interval_set representation
        [(1, 2), (5, 5), (10, 50)]
        # strinf representation
        1-2 5 10-50

    .. warning:: Floating point precision is set to
        :py:attr:`self.float_precision` so all floating point values are
        rounded with this number of digits. Defalut set to 6

    For example:

    >>> from evalys.jobset import JobSet
    >>> js = JobSet.from_csv("./examples/jobs.csv")
    >>> js.plot(with_details=True)
    >>> # to show the graph
    >>> # import matplotlib.pyplot as plt
    >>> # plt.show()

    You can also specify the the resource_bounds like this:

    >>> js = JobSet.from_csv("./examples/jobs.csv",
    ...                      resource_bounds=(0, 63))
    '''
    def __init__(self, df, resource_bounds=None, float_precision=6):
        # set float round precision
        self.float_precision = float_precision
        self.df = np.round(df, float_precision)

        if resource_bounds:
            self.res_bounds = ProcInt(*resource_bounds)
        else:
            self.res_bounds = ProcInt(
                min(pset.min for pset in self.df.allocated_processors),
                max(pset.max for pset in self.df.allocated_processors)
            )

        self.MaxProcs = len(self.res_bounds)

        self.df['proc_alloc'] = self.df.allocated_processors.apply(len)

        # Add missing columns if possible
        fillable_relative = all(
            col in self.df.columns
            for col in ['submission_time', 'waiting_time', 'execution_time']
        )
        fillable_absolute = all(
            col in self.df.columns
            for col in ['submission_time', 'starting_time', 'finish_time']
        )
        if fillable_relative:
            if 'starting_time' not in self.df.columns:
                self.df['starting_time'] = \
                    self.df['submission_time'] + self.df['waiting_time']
            if 'finish_time' not in self.df.columns:
                self.df['finish_time'] = \
                    self.df['starting_time'] + self.df['execution_time']
        elif fillable_absolute:
            if 'waiting_time' not in self.df.columns:
                self.df['waiting_time'] = \
                    self.df['starting_time'] - self.df['submission_time']
            if 'execution_time' not in self.df.columns:
                self.df['execution_time'] = \
                    self.df['finish_time'] - self.df['starting_time']

        if 'job_id' in self.df.columns:
            self.df.rename(columns={'job_id': 'jobID'}, inplace=True)

        # TODO check consistency on calculated columns...

        # init cache
        self._utilisation = None
        self._queue = None

    __converters = {
        'jobID': str,
        'job_id': str,
        'allocated_processors': ProcSet.from_str,
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
    def from_csv(cls, filename, resource_bounds=None):
        df = pd.read_csv(filename, converters=cls.__converters)
        return cls(df, resource_bounds=resource_bounds)

    def to_csv(self, filename):
        """ Export this jobset to a csv file with a ',' as separator.

        Example:

        >>> from evalys.jobset import JobSet
        >>> js = JobSet.from_csv("./examples/jobs.csv")
        >>> js.to_csv("/tmp/jobs.csv")
        """
        df = self.df.copy()
        df.allocated_processors = df.allocated_processors.apply(str)
        with open(filename, 'w') as f:
            df.to_csv(f, index=False, sep=",",
                      float_format='%.{}f'.format(self.float_precision))

    def gantt(self, ax=None, title="Gantt chart", time_scale=False):
        visu.plot_gantt(self, ax, title, time_scale=time_scale)

    @property
    def utilisation(self):
        if self._utilisation is not None:
            return self._utilisation
        self._utilisation = compute_load(self.df,
                                         col_begin='starting_time',
                                         col_end='finish_time',
                                         col_cumsum='proc_alloc')
        return self._utilisation

    @property
    def queue(self):
        '''
        Calculate cluster queue size over time in number of procs.

        :returns:
            a time indexed serie that contain the number of used processors
        '''
        # Do not re-compute everytime
        if self._queue is not None:
            return self._queue

        proc = "requested_number_of_processors"
        self._queue = compute_load(self.df, 'submission_time', 'starting_time',
                                   proc)
        return self._queue

    def reset_time(self, to=0):
        '''
        Reset the time index by giving the first submission time as 0
        '''
        df = self.df
        for col in ['starting_time', 'submission_time', 'finish_time']:
            df[col] = df[col] - df['submission_time'].min() + to

        self._queue = None
        self._utilisation = None

    def plot(self, normalize=False, with_details=False, time_scale=False,
             title=None):
        nrows = 2
        if with_details:
            nrows = nrows + 2
        fig, axe = plt.subplots(nrows=nrows, sharex=True)
        if title:
            fig.suptitle(title, fontsize=16)
        visu.plot_load(self.utilisation, self.MaxProcs,
                       load_label="utilisation", ax=axe[0],
                       normalize=normalize, time_scale=time_scale)
        visu.plot_load(self.queue, self.MaxProcs,
                       load_label="queue", ax=axe[1], normalize=normalize,
                       time_scale=time_scale)
        if with_details:
            visu.plot_job_details(self.df, self.MaxProcs, ax=axe[2],
                                  time_scale=time_scale)
            visu.plot_gantt(self, ax=axe[3], time_scale=time_scale)

    def detailed_utilisation(self):
        df = self.free_intervals()
        df['total'] = len(self.res_bounds) - df.free_itvs.apply(len)
        df.set_index("time", drop=True, inplace=True)
        return df

    def mean_utilisation(self, begin_time=None, end_time=None):
        return load_mean(self.utilisation, begin=begin_time, end=end_time)

    def free_intervals(self, begin_time=0, end_time=None):
        '''
        :returns: a dataframe with the free resources over time. Each line
            corespounding to an event in the jobset.
        '''
        df = self.df

        # Create a list of start and stop event associated to the proc
        # allocation:
        # Free -> Used : grab = 1
        # Used -> Free : grab = 0
        event_columns = ['time', 'free_itvs', 'grab']
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
            ignore_index=True).sort_values(
                by=['time', 'grab']).reset_index(drop=True)

        # cut events if necessary
        # reindex event_df
        event_df = event_df.sort_values(by='time').set_index(['time'],
                                                             drop=False)
        # find closest index
        begin = event_df.index.searchsorted(begin_time)
        if end_time is not None:
            end = event_df.index.searchsorted(end_time)
        else:
            end = len(event_df.index) - 1

        event_df = event_df.iloc[begin:end].reset_index(drop=True)

        # All resources are free at the beginning
        event_columns = ['time', 'free_itvs']
        first_row = [begin_time, ProcSet(self.res_bounds)]
        free_interval_serie = pd.DataFrame(columns=event_columns)
        free_interval_serie.loc[0] = first_row
        for index, row in event_df.iterrows():
            current_itv = free_interval_serie.ix[index]['free_itvs']
            if row.grab:
                new_itv = current_itv - row.free_itvs
            else:
                new_itv = current_itv | row.free_itvs
            new_row = [row.time, new_itv]
            free_interval_serie.loc[index + 1] = new_row

        if end_time is not None:
            last_row = [end_time, ProcSet()]
            free_interval_serie.loc[len(free_interval_serie)] = last_row
        return free_interval_serie

    def free_slots(self, begin_time=0, end_time=None):
        '''
        :returns: a DataFrame (compatible with a JobSet) that contains all
            the not overlapping square free slots of this JobSet maximzing the
            time. It can be transform to a JobSet to be plot as gantt chart.
        '''
        # slots_time contains tuple of
        # (slot_begin_time,free_resources_intervals)
        free_interval_serie = self.free_intervals(begin_time, end_time)
        slots_time = [(free_interval_serie.time[0], ProcSet(self.res_bounds))]
        new_slots_time = slots_time
        columns = ['jobID', 'allocated_processors',
                   'starting_time', 'finish_time', 'execution_time',
                   'submission_time']
        free_slots_df = pd.DataFrame(columns=columns)
        prev_free_itvs = ProcSet(self.res_bounds)
        slots = 0
        for i, curr_row in free_interval_serie.iterrows():
            if i == 0:
                continue
            new_slots_time = []
            curr_time = curr_row.time
            taken_resources = prev_free_itvs - curr_row.free_itvs
            freed_resources = curr_row.free_itvs - prev_free_itvs
            if i == len(free_interval_serie) - 1:
                taken_resources = ProcSet(self.res_bounds)
            if taken_resources:
                # slot ends: store it and update free slot
                for begin_time, itvs in slots_time:
                    to_update = itvs & taken_resources
                    if to_update:
                        # store new slots
                        slots = slots + 1
                        new_slot = [str(slots),
                                    to_update,
                                    begin_time,
                                    curr_time,
                                    curr_time - begin_time,
                                    begin_time]
                        free_slots_df.loc[slots] = new_slot
                        # remove free slots
                        free_res = itvs - to_update
                        if free_res:
                            new_slots_time.append((begin_time, free_res))
                    else:
                        new_slots_time.append((begin_time, itvs))

            if freed_resources:
                # slots begin: udpate free slot
                if not new_slots_time:
                    new_slots_time = slots_time
                new_slots_time.append((curr_time, freed_resources))

            # update previous
            prev_free_itvs = curr_row.free_itvs
            # clean slots_free
            slots_time = new_slots_time
        return free_slots_df

    def fragmentation(self,
                      p=2,
                      resource_intervals=None,
                      begin_time=0,
                      end_time=None):
        # return fragmentation(
        #    self.free_resources_gaps(resource_intervals,
        #                             begin_time, end_time),
        #    p=p)

        return fragmentation_reis(
            self.free_resources_gaps(resource_intervals,
                                     begin_time, end_time),
            end_time - begin_time, p=p)

    def free_resources_gaps(self, resource_intervals=None,
                            begin_time=0, end_time=None):
        """
        :param resource_intervals: An interval set on which compute the
            free resources gaps, Default: self.res_bounds
        :returns: a resource indexed list where each element is a numpy
            array of free slots.
        """
        js = self
        fs = js.free_slots(begin_time, end_time)
        free_resources_gaps = []
        if resource_intervals is None:
            resource_intervals = self.res_bounds
        for _ in range(resource_intervals[0], resource_intervals[1] + 1):
            free_resources_gaps.append([])

        def get_free_slots_by_resources(x):
            for res in range(resource_intervals[0], resource_intervals[1] + 1):
                if res in x.allocated_processors:
                    free_resources_gaps[res].append(x.execution_time)

        # compute resource gaps
        fs.apply(get_free_slots_by_resources, axis=1)
        # format each gap list in numpy array
        for i, fi in enumerate(free_resources_gaps):
            free_resources_gaps[i] = np.asarray(fi)

        return free_resources_gaps
