# coding: utf-8
'''
This module contains the data and metadata given in the headers of the SWF
format.

SWF is the default format for parallel workload defined here:
see: http://www.cs.huji.ac.il/labs/parallel/workload/swf.html
'''
from __future__ import unicode_literals, print_function
from collections import OrderedDict
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import datetime
from evalys.metrics import compute_load, load_mean


class Workload(object):
    '''
    This class is a derived from the SWF format. SWF is the default format
    for parallel workload defined here:
    see: http://www.cs.huji.ac.il/labs/parallel/workload/swf.html

    the data format is one line per job, with 18 fields:
     0 - Job Number, a counter field, starting from 1
     1 - Submit Time, seconds. submittal time
     2 - Wait Time, seconds. diff between submit and begin to run
     3 - Run Time, seconds. end-time minus start-time
     4 - Number of Processors, number of allocated processors
     5 - Average CPU Time Used, seconds. user+system. avg over procs
     6 - Used Memory, KB. avg over procs.
     7 - Requested Number of Processors, requested number of
         processors
     8 - Requested Time, seconds. user runtime estimation
     9 - Requested Memory, KB. avg over procs.
    10 - status (1=completed, 0=killed), 0=fail; 1=completed;
         5=canceled
    11 - User ID, user id
    12 - Group ID, group id
    13 - Executable (Application) Number, [1,2..n] n = app#
         appearing in log
    14 - Queue Number, [1,2..n] n = queue# in the system
    15 - Partition Number, [1,2..n] n = partition# in the systems
    16 - Preceding Job Number,  cur job will start only after ...
    17 - Think Time from Preceding Job, seconds should elapse
         between termination of
    '''
    metadata = {
     'Version': '''
        Version number of the standard format the file uses. The format
        described here is version 2.''',
     'Computer': '''
        Brand and model of computer''',
     'Installation': '''
        Location of installation and machine name''',
     'Acknowledge': '''
        Name of person(s) to acknowledge for creating/collecting the
        workload.''',
     'Information': '''
        Web site or email that contain more information about the
        workload or installation.''',
     'Conversion': '''
        Name and email of whoever converted the log to the standard
        format.''',
     'MaxJobs': '''
        Integer, total number of jobs in this workload file.''',
     'MaxRecords': '''
        Integer, total number of records in this workload file. If no
        checkpointing/swapping information is included, there is one record
        per job, and this is equal to MaxJobs. But with
        chekpointing/swapping there may be multiple records per job. ''',
     'Preemption': '''
        Enumerated, with four possible values. 'No' means that jobs run to
        completion, and are represented by a single line in the file. 'Yes'
        means that the execution of a job may be split into several parts, and
        each is represented by a separate line. 'Double' means that jobs
        may be split, and their information appears twice in the file: once
        as a one-line summary, and again as a sequence of lines
        representing the parts, as suggested above. 'TS' means time slicing
        is used, but no details are available.''',
     'UnixStartTime': '''
        When the log starts, in Unix time (seconds since the epoch)''',
     'TimeZone': '''*DEPRECATED* and replaced by TimeZoneString.
        A value to add to times given as seconds since the epoch. The sum can
        then be fed into gmtime (Greenwich time function) to get the correct
        date and hour of the day. The default is 0, and then gmtime can be used
        directly.
        Note:
          do not use localtime, as then the results will depend on the
          difference between your time zone and the installation time zone.''',
     'TimeZoneString': '''
        Replaces the buggy and now deprecated TimeZone. TimeZoneString is a
        standard UNIX string indicating the time zone in which the log was
        generated; this is actually the name of a zoneinfo file, e.g.
        ``Europe/Paris''. All times within the SWF file are in this time
        zone. For more details see the usage note below.''',
     'StartTime': '''
        When the log starts, in human readable form, in this
        standard format: Tue Feb 21 18:44:15 IST 2006 (as printed by the UNIX
        'date' utility).  EndTime: When the log ends (the last termination),
        formatted like StartTime.''',
     'MaxNodes': '''
         Integer, number of nodes in the computer. List the number of
         nodes in different partitions in parentheses if applicable.''',
     'MaxProcs': '''
         Integer, number of processors in the computer. This is different
         from MaxNodes if each node is an SMP. List the number of processors
         in different partitions in parentheses if applicable.''',
     'MaxRuntime': '''
         Integer, in seconds. This is the maximum that the system allowed, and
         may be larger than any specific job's runtime in the workload.''',
     'MaxMemory': '''
         Integer, in kilobytes. Again, this is the maximum the system
         allowed.''',
     'AllowOveruse': '''
         Boolean. 'Yes' if a job may use more than it requested for any
         resource, 'No' if it can't.''',
     'MaxQueues': '''
         Integer, number of queues used.''',
     'Queues': '''
         A verbal description of the system's queues. Should explain the queue
         number field (if it has known values). As a minimum it should be
         explained how to tell between a batch and interactive job.  Queue: A
         description of a single queue in the following format: queue-number
         queue-name (optional-details). This should be repeated for all the
         queues.''',
     'MaxPartitions': '''
         Integer, number of partitions used.''',
     'Partitions': '''
         A verbal description of the system's partitions, to explain the
         partition number field. For example, partitions can be distinct
         parallel machines in a cluster, or sets of nodes with different
         attributes (memory configuration, number of CPUs, special attached
         devices), especially if this is known to the scheduler. ''',
     'Partition': '''
         Description of a single partition.''',
     'Note': '''
         There may be several notes, describing special features of the log.
         For example, ``The runtime is until the last node was freed; jobs may
         have freed some of their nodes earlier''. '''
    }

    # clean metadata layout
    metadata = {k: ' '.join(v.split()) for k, v in metadata.items()}

    def __init__(self, dataframe, **kwargs):
        ''' dataframe should be an swf imported format and metadata can be
        provided in kargs.'''

        self.df = dataframe
        for key, value in kwargs.items():
            # cast integer
            if key.startswith('Max'):
                value = int(value)
            setattr(self, key, value)

        # Initialise start time
        if not hasattr(self, "UnixStartTime"):
            self.UnixStartTime = 0

        # property initialization
        self._utilisation = None
        self._queue = None
        self._jobs_per_week_per_users = None
        self._fraction_jobs_by_job_size = None
        self._arriving_each_day = None
        self._arriving_each_hour = None

    @classmethod
    def from_csv(cls, filename):
        columns = ['jobID', 'submission_time', 'waiting_time',
                   'execution_time', 'proc_alloc', 'cpu_used', 'mem_used',
                   'proc_req', 'user_est', 'mem_req', 'status', 'uid',
                   'gid', 'exe_num', 'queue', 'partition', 'prev_jobs',
                   'think_time']
        df = pd.read_csv(filename, comment=';', names=columns,
                         header=0, delim_whitespace=True)
        # sanitize trace
        # - remove job checkpoint information (job status != 0 or 1)
        df = df[lambda x: x['status'] <= 1]

        # process header
        header_file = open(filename, 'r')
        header = ''
        metadata = {}
        for line in header_file:
            if re.match("^;", line):
                header += line
                m = re.search("^;\s(.*):\s(.*)", line)
                if m:
                    metadata[m.group(1).strip()] = m.group(2).strip()
            else:
                # header is finished
                break

        return cls(df, **metadata)

    def to_csv(self, filename):
        '''
        Export the workload as SWF format CSV file
        '''
        # Write metadata
        metadata = ""
        for elem in Workload.metadata.keys():
            if hasattr(self, elem):
                metadata += "; {}: {}\n".format(elem, getattr(self, elem))
        if metadata:
            with open(filename, 'w') as f:
                f.writelines(metadata)
                self.df.to_csv(f, index=False, header=False,
                               sep="\t")

    @property
    def queue(self):
        '''
        Calculate cluster queue size over time in number of procs
        returns:
            a time indexed serie that contain the number of used processors
            It is based on real time if UnixStartTime is defined
        '''
        # Do not re-compute everytime
        if self._queue is not None:
            return self._queue

        self._queue = compute_load(self.df, 'submission_time', 'starting_time',
                                   'proc_req', self.UnixStartTime)
        return self._queue

    @property
    def utilisation(self):
        '''
        Calculate cluster utilisation over time:
            nb procs used / nb procs available
        returns:
            a time indexed serie that contain the number of used processors
            It is based on real time
        TODO: Add ID list of jobs running and ID list of jobs in queue to
        the returned dataframe
        '''
        # Do not re-compute everytime
        if self._utilisation is not None:
            return self._utilisation

        self._utilisation = compute_load(self.df, 'starting_time', 'stop',
                                         'proc_alloc', self.UnixStartTime)
        return self._utilisation

    def plot_utilisation(self, ax=None, normalize=False):
        '''
        Plots the number of used resources against time
        opt:
            - normalize (bool) : normalize by the number of procs
        '''
        u = self.utilisation

        # convert timestamp to datetime
        u.index = pd.to_datetime(u['time'] +
                                 int(self.UnixStartTime), unit='s')
        # leave room to have better view
        plt.margins(x=0.1, y=0.1)

        if normalize:
            u = u / self.MaxProcs

        # plot utilisation
        u.plot(drawstyle="steps", ax=ax)

        # plot a line for the number of procs
        if hasattr(self, "MaxProcs"):
            plt.plot([u.index[0], u.index[-1]],
                     [self.MaxProcs, self.MaxProcs],
                     color='k', linestyle='-', linewidth=2, ax=ax)

    def resources_free_time(self):
        '''
        go through the utilisation series to find resources that are free
        for a certaine amount of time
        '''

        free = self.MaxProcs - self.utilisation
        # normalize by max procs
        free = free / self.MaxProcs

        # Init data structure
        free_ratio = range(1, 10)
        free_slots_arrays = {}
        for ratio in free_ratio:
            free_slots_arrays[ratio] = []
        resource_used = np.zeros(9, dtype=bool)

        for time, value in free.iteritems():
            for ratio, i in zip(free_ratio, range(len(resource_used))):
                # if state free > used
                if not resource_used[i] and value <= ratio/10:
                    resource_used[i] = True
                    free_slots_arrays[ratio].append(time)
                # if state used > free
                if resource_used[i] and value > ratio/10:
                    resource_used[i] = False
                    begin_time_slot = free_slots_arrays[ratio][-1]
                    slot = time - begin_time_slot
                    slot_sec = (slot.microseconds + (slot.seconds +
                                                     slot.days * 24 * 3600)
                                * 10**6) / 10**6
                    free_slots_arrays[ratio][-1] = slot_sec
        return free_slots_arrays

    def resources_free_time_plot(self):

        free_slots_arrays = self.resources_free_time()
        fig, axes = plt.subplots(nrows=len(free_slots_arrays), ncols=1,
                                 sharex=True)
        # generate histogram
        i = 0
        for ratio, array in self.resources_free_time().items():
            serie = pd.Series(array)
            serie.plot(kind='hist',
                       ax=axes[i],
                       title="free resources {}%".format(ratio*10))
            i = i + 1

    def plot_free_resources(self, normalize=False):
        '''
        Plots the number of free resources against time
        opt:
            - normalize (bool) : normalize by the number of procs
        '''
        free = self.MaxProcs - self.utilisation

        if normalize:
            free = free / self.MaxProcs

        free.index = pd.to_datetime(free['time'] +
                                    int(self.UnixStartTime), unit='s')
        free.plot()
        # plot a line for the number of procs
        plt.plot([free.index[0], free.index[-1]],
                 [self.MaxProcs, self.MaxProcs],
                 color='k', linestyle='-', linewidth=2)

    def extract_periods_with_given_utilisation(self,
                                               period_in_hours,
                                               utilisation,
                                               variation=0.001):
        '''
        This extract from the workload a period (in hours) with a given mean
        utilisation (between 0 and 1).
        returns:
            a list of workload of the given periods, with the given
            utilisation, extracted from the this workload.
        '''
        norm_util = self.utilisation.area / self.MaxProcs

        # convert timestamp to datetime
        norm_util.index = pd.to_datetime(norm_util.index +
                                         int(self.UnixStartTime), unit='s')
        resampled_df = norm_util.resample(str(period_in_hours) + 'H')
        periods = resampled_df.apply(load_mean)\
            .loc[lambda x: x >= (utilisation - variation)]\
            .loc[lambda x: x <= (utilisation + variation)]

        # reindex workload by start time to extract easily
        df = self.df
        df['starting_time'] = \
            self.df['submission_time'] + self.df['waiting_time']
        df = df.sort_values(by='starting_time').set_index(['starting_time'])
        df.index = pd.to_datetime(df.index + int(self.UnixStartTime), unit='s')

        extracted = []
        for period_begin in periods.index:
            start = df.index.searchsorted(period_begin)
            end = df.index.searchsorted(
                period_begin + pd.to_timedelta(period_in_hours, unit='H'))
            # Create a Workload object from extracted dataframe
            wl = Workload(df[start:end].reset_index(drop=True),
                          Conversion="Workload extracted using Evalys: "
                                     "https://github.com/oar-team/evalys",
                          Information=self.Information,
                          Computer=self.Computer,
                          Installation=self.Installation,
                          Note="Period of {} hours with a mean utilisation "
                               "of {}".format(period_in_hours, utilisation),
                          MaxProcs=self.MaxProcs,
                          UnixStartTime=int(
                              period_begin.to_datetime().timestamp()))
            extracted.append(wl)

        return extracted

    @property
    def arriving_each_day(self):
        # Do not re-compute everytime
        if self._arriving_each_day is not None:
            return self._arriving_each_day

        df = self.df
        df['day'] = df.apply(lambda x: datetime.datetime.fromtimestamp(
            int(self.UnixStartTime)+x['submission_time']).strftime('%u'),
            axis=1)
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

        grouped = df.groupby('day')
        df1 = grouped['jobID'].agg(
            {'jobs': lambda x: float(x.count())/self.MaxJobs})
        nb_procs = df['proc_req'].sum()
        df2 = grouped['proc_req'].agg(
            {'procs': lambda x: float(x.sum())/nb_procs})

        df1['procs'] = df2['procs']
        df1.index = days
        self._arriving_each_day = df1
        return df1

    @property
    def arriving_each_hour(self):
        # Do not re-compute everytime
        if self._arriving_each_hour is not None:
            return self._arriving_each_hour

        df = self.df
        df['hour'] = df.apply(lambda x: datetime.datetime.fromtimestamp(
            int(self.UnixStartTime)+x['submission_time']).strftime('%H'),
            axis=1)

        grouped = df.groupby('hour')
        df1 = grouped['jobID'].agg(
            {'jobs': lambda x: float(x.count())/self.MaxJobs})
        nb_procs = df['proc_req'].sum()
        df2 = grouped['proc_req'].agg(
            {'procs': lambda x: float(x.sum())/nb_procs})

        df1['procs'] = df2['procs']
        self._arriving_each_hour = df1
        return self._arriving_each_hour

    @property
    def jobs_per_week_per_user(self, nb=6):
        # Do not re-compute everytime
        if self._jobs_per_week_per_user is not None:
            return self._jobs_per_week_per_user

        df = self.df
        df['week'] = df.apply(lambda x: datetime.datetime.fromtimestamp(
            int(self.UnixStartTime)+x['submission_time']).strftime('%W'),
            axis=1)
        grouped = df.groupby(['week', 'uid'])

        da = grouped['jobID'].agg({'count': 'count'})
        nb_weeks = len(da.index.levels[0])

        # identify nb largest contributors (uid), 0 uid is for others)
        job_nlargest_uid = list(
            df.groupby('uid')['jobID'].count().nlargest(nb).index)
        # [ 0, reversed list ]
        job_nlargest_uid_0 = [0] + job_nlargest_uid[::-1]

        # jobs_week_uid_dict = {i: [0]*nb_weeks for i in job_nlargest_uid_0}
        jobs_week_uid_dict = OrderedDict(
            (i, [0]*nb_weeks) for i in job_nlargest_uid_0)
        idx = 0
        for i, g in da.groupby(level=0):
            df_j = g.xs(i, level='week')  # dataframe uid / nb_jobs(count)
            for uid, row in df_j.iterrows():
                if uid in job_nlargest_uid_0:
                    jobs_week_uid_dict[uid][idx] = row['count']
                else:
                    jobs_week_uid_dict[0][idx] += row['count']
            idx += 1

        self._jobs_per_week_per_users = pd.DataFrame(jobs_week_uid_dict)
        return self._jobs_per_week_per_users

    @property
    def fraction_jobs_by_job_size(self):
        # Do not re-compute everytime
        if self._fraction_jobs_by_job_size is not None:
            return self._fraction_jobs_by_job_size

        grouped = self.df.groupby('proc_alloc')
        self._fraction_jobs_by_job_size = grouped['jobID'].agg(
            {'jobs': lambda x: float(x.count())/self.nb_jobs})
        return self._fraction_jobs_by_job_size
