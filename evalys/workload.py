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
from evalys.utils import cut_workload
from evalys import visu


class Workload(object):
    '''
    This class is a derived from the SWF format. SWF is the default format
    for parallel workload defined here:
    http://www.cs.huji.ac.il/labs/parallel/workload/swf.html

    the data format is one line per job, with 18 fields:

    0) Job Number, a counter field, starting from 1

    1) Submit Time, seconds. submittal time
    2) Wait Time, seconds. diff between submit and begin to run
    3) Run Time, seconds. end-time minus start-time
    4) Number of Processors, number of allocated processors
    5) Average CPU Time Used, seconds. user+system. avg over procs
    6) Used Memory, KB. avg over procs.
    7) Requested Number of Processors, requested number of
       processors
    8) Requested Time, seconds. user runtime estimation
    9) Requested Memory, KB. avg over procs.
    10) status (1=completed, 0=killed), 0=fail; 1=completed; 5=canceled
    11) User ID, user id
    12) Group ID, group id
    13) Executable (Application) Number, [1,2..n] n = app#
        appearing in log
    14) Queue Number, [1,2..n] n = queue# in the system
    15) Partition Number, [1,2..n] n = partition# in the systems
    16) Preceding Job Number,  cur job will start only after ...
    17) Think Time from Preceding Job, seconds should elapse
        between termination of this preceding job. Together with the next
        field, this allows the workload to include feedback as described
        below.
    18) Think Time from Preceding Job -- this is the number of seconds that
        should elapse between the termination of the preceding job and the
        submittal of this one.

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
                try:
                    value = int(re.search(r'\d+', value).group())
                    setattr(self, key, value)
                except:
                    print("WARNING: unable to get \"{}\" integer value. Found"
                          " value: {}".format(key, value))
            else:
                setattr(self, key, value)

        # Initialise start time
        if hasattr(self, "UnixStartTime"):
            try:
                self.UnixStartTime = int(self.UnixStartTime)
            except:
                self.UnixStartTime = 0
        else:
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
        '''
        Import SWF CSV file.
        :param filename: SWF file path
        '''
        columns = ['jobID', 'submission_time', 'waiting_time',
                   'execution_time', 'proc_alloc', 'cpu_used', 'mem_used',
                   'proc_req', 'user_est', 'mem_req', 'status', 'uid',
                   'gid', 'exe_num', 'queue', 'partition', 'prev_jobs',
                   'think_time']
        df = pd.read_csv(filename, comment=';', names=columns,
                         header=0, delim_whitespace=True)
        # sanitize trace
        # - remove job checkpoint information (job status != 0 or 1)
        df = df[df['status'] <= 1]

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
        :param filename: exported SWF file path
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
        Calculate cluster queue size over time in number of procs.

        :returns:
            a time indexed serie that contain the number of used processors
            It is based on real time if UnixStartTime is defined
        '''
        # Do not re-compute everytime
        if self._queue is not None:
            return self._queue

        # sometimes "proc_req" is not provided
        if (self.df.proc_req == -1).any():
            proc = "proc_alloc"
        else:
            proc = "proc_req"
        self._queue = compute_load(self.df, 'submission_time', 'starting_time',
                                   proc, self.UnixStartTime)
        return self._queue

    @property
    def utilisation(self):
        '''
        Calculate cluster utilisation over time:
            nb procs used / nb procs available

        :returns:
            a time indexed serie that contain the number of used processors
            It is based on real time

        TODO: Add ID list of jobs running and ID list of jobs in queue to
            the returned dataframe
        '''
        # Do not re-compute everytime
        if self._utilisation is not None:
            return self._utilisation

        self._utilisation = compute_load(self.df,
                                         'starting_time',
                                         'finish_time',
                                         'proc_alloc', self.UnixStartTime)
        return self._utilisation

    def plot(self, normalize=False, with_details=False, time_scale=False):
        """
        Plot workload general informations.

        :args with_details:
            if True show the job submission, start and finish time
            (Warning: don't use this on large traces.
        """
        nrows = 2
        if with_details:
            nrows = nrows + 1
        _, axe = plt.subplots(nrows=nrows, sharex=True)
        visu.plot_load(self.utilisation, self.MaxProcs, time_scale=time_scale,
                       UnixStartTime=self.UnixStartTime,
                       TimeZoneString=self.TimeZoneString,
                       load_label="utilisation", ax=axe[0],
                       normalize=normalize)
        visu.plot_load(self.queue, self.MaxProcs, time_scale=time_scale,
                       UnixStartTime=self.UnixStartTime,
                       TimeZoneString=self.TimeZoneString,
                       load_label="queue", ax=axe[1], normalize=normalize)
        if with_details:
            visu.plot_job_details(self.df, self.MaxProcs, time_scale=time_scale,
                                  time_offset=self.UnixStartTime)

    def extract_periods_with_given_utilisation(self,
                                               period_in_hours,
                                               utilisation,
                                               variation=0.01,
                                               nb_max=None):
        '''
        This extract from the workload a period (in hours) with a given mean
        utilisation (between 0 and 1).

        :returns:
            a list of workload of the given periods, with the given
            utilisation, extracted from the this workload.
        '''
        norm_util = self.utilisation

        # resample the dataframe with the given period
        time_periods = np.arange(min(norm_util.index),
                                 max(norm_util.index),
                                 60 * 60 * period_in_hours)
        mean_df = pd.DataFrame()
        for index, val in enumerate(time_periods):
            if index == len(time_periods) - 1 or index == 0:
                continue
            begin = val
            end = time_periods[index + 1]

            mean_df = mean_df.append(
                {"begin": begin,
                 "end": end,
                 "mean_util": load_mean(norm_util,
                                        begin=begin,
                                        end=end)},
                ignore_index=True)

        mean_df["norm_mean_util"] = mean_df.mean_util / self.MaxProcs
        periods = mean_df.loc[
            lambda x: x.norm_mean_util >= (utilisation - variation)].loc[
                lambda x: x.norm_mean_util <= (utilisation + variation)
            ]

        # Only take nb_max periods if it is defined
        if nb_max:
            periods = periods[:nb_max]

        notes = ("Period of {} hours with a mean utilisation "
                 "of {}".format(period_in_hours, utilisation))
        return self.extract(periods, notes)

    def extract(self, periods, notes=""):
        """
        Extract workload periods from the given workload dataframe.
        Returns a list of extracted Workloads. Some notes can be added to
        the extracted workload. It will be stored in Notes attributs and
        it will appear in the SWF header if you extract it to a file with
        to_csv().

        For example:

        >>> from evalys.workload import Workload
        >>> w = Workload.from_csv("./examples/UniLu-Gaia-2014-2.swf")
        >>> periods = pd.DataFrame([{"begin": 200000, "end": 400000},
        ...                         {"begin": 400000, "end": 600000}])
        >>> extracted = w.extract(periods)
        """

        extracted = []

        def do_extract(period):
            to_export = cut_workload(self.df, period.begin, period.end)
            wl = Workload(to_export["workload"],
                          Conversion="Workload extracted using Evalys: "
                                     "https://github.com/oar-team/evalys",
                          Information=self.Information,
                          Computer=self.Computer,
                          Installation=self.Installation,
                          Note=notes,
                          MaxProcs=self.MaxProcs,
                          UnixStartTime=int(period.begin),
                          ExtractBegin=period.begin,
                          ExtractEnd=period.end)
            extracted.append(wl)

        periods.apply(do_extract, axis=1)
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
            {'jobs': lambda x: float(x.count())/len(self.df)})
        return self._fraction_jobs_by_job_size
