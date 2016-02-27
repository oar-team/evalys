# coding: utf-8
from __future__ import unicode_literals, print_function
from collections import OrderedDict
import pandas as pd
import re
import datetime


class Workload(object):
    def __init__(self, **kwargs):
        if 'file' in kwargs:
            # swf is the default format
            # see: http://www.cs.huji.ac.il/labs/parallel/workload/swf.html
            #
            # the data format is one line per job, with 18 fields:
            #  0 - Job Number, a counter field, starting from 1
            #  1 - Submit Time, seconds. submittal time
            #  2 - Wait Time, seconds. diff between submit and begin to run
            #  3 - Run Time, seconds. end-time minus start-time
            #  4 - Number of Processors, number of allocated processors
            #  5 - Average CPU Time Used, seconds. user+system. avg over procs
            #  6 - Used Memory, KB. avg over procs.
            #  7 - Requested Number of Processors, requested number of processors
            #  8 - Requested Time, seconds. user runtime estimation
            #  9 - Requested Memory, KB. avg over procs.
            # 10 - status (1=completed, 0=killed), 0=fail; 1=completed; 5=canceled
            # 11 - User ID, user id
            # 12 - Group ID, group id
            # 13 - Executable (Application) Number, [1,2..n] n = app# appearing in log
            # 14 - Queue Number, [1,2..n] n = queue# in the system
            # 15 - Partition Number, [1,2..n] n = partition# in the systems
            # 16 - Preceding Job Number,  cur job will start only after ...
            # 17 - Think Time from Preceding Job, seconds should elapse between termination of
            #
            columns = ['job', 'submit', 'wait', 'runtime', 'proc_alloc', 'cpu_used', 'mem_used', 'proc_req',
                       'user_est', 'mem_req', 'status', 'uid', 'gid', 'exe_num', 'queue', 'partition',
                       'prev_jobs', 'think_time']
            # columns_1 = ['Job', 'Submit Time', 'Wait Time', 'Run Time', 'Nb Alloc Proc', 'Average CPU',
            #             'Used Memory', 'Req Nb Proc', 'Req Time', 'Req Memory', 'Status', 'User',
            #             'Group', 'Application', 'Queue', 'Partition', 'Preceding Job', 'Think Time']

            self.df = pd.read_csv(kwargs['file'], comment=';', names=columns, header=0, delim_whitespace=True)

            self.nb_jobs = len(self.df)
            # process header
            header_file = open(kwargs['file'], 'r')
            self.header = ''
            for line in header_file:
                if re.match("^;", line):
                    print(line)
                    self.header += line

                    m = re.search(".*UnixStartTime:\s(\d+)", line)
                    if m:
                        self.unix_start_time = int(m.group(1))
                        self.str_start_time = datetime.datetime.fromtimestamp(
                            self.unix_start_time).strftime('%Y-%m-%d %H:%M:%S')

                    m = re.search(".*MaxNodes:\s(\d+)", line)
                    if m:
                        self.max_nodes = int(m.group(1))

                    m = re.search(".*MaxProcs:\s(\d+)", line)
                    if m:
                        self.max_procs = int(m.group(1))

                    m = re.search(".MaxQueues*:\s(\d+)", line)
                    if m:
                        self.max_queues = int(m.group(1))

                else:
                    # header is finished
                    break

    def gene_arriving_each_day(self):
        df = self.df
        df['day'] = df.apply(lambda x: datetime.datetime.fromtimestamp(
            self.unix_start_time+x['submit']).strftime('%u'), axis=1)
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

        grouped = df.groupby('day')
        df1 = grouped['job'].agg({'jobs': lambda x: float(x.count())/self.nb_jobs})
        nb_procs = df['proc_req'].sum()
        df2 = grouped['proc_req'].agg({'procs': lambda x: float(x.sum())/nb_procs})

        df1['procs'] = df2['procs']
        df1.index = days
        self.arriving_each_day = df1

    def gene_arriving_each_hour(self):
        df = self.df
        df['hour'] = df.apply(lambda x: datetime.datetime.fromtimestamp(
            self.unix_start_time+x['submit']).strftime('%H'), axis=1)

        grouped = df.groupby('hour')
        df1 = grouped['job'].agg({'jobs': lambda x: float(x.count())/self.nb_jobs})
        nb_procs = df['proc_req'].sum()
        df2 = grouped['proc_req'].agg({'procs': lambda x: float(x.sum())/nb_procs})

        df1['procs'] = df2['procs']
        self.arriving_each_hour = df1

    def gene_jobs_per_week_per_user(self, nb=6):
        df = self.df
        df['week'] = df.apply(lambda x: datetime.datetime.fromtimestamp(
            self.unix_start_time+x['submit']).strftime('%W'), axis=1)
        grouped = df.groupby(['week', 'uid'])

        da = grouped['job'].agg({'count': 'count'})
        nb_weeks = len(da.index.levels[0])

        # identify nb largest contributors (uid), 0 uid is for others)
        job_nlargest_uid = list(df.groupby('uid')['job'].count().nlargest(nb).index)
        job_nlargest_uid_0 = [0] + job_nlargest_uid[::-1]  # [ 0, reversed list ]

        # jobs_week_uid_dict = {i: [0]*nb_weeks for i in job_nlargest_uid_0}
        jobs_week_uid_dict = OrderedDict((i, [0]*nb_weeks) for i in job_nlargest_uid_0)
        idx = 0
        for i, g in da.groupby(level=0):
            df_j = g.xs(i, level='week')  # dataframe uid / nb_jobs(count)
            for uid, row in df_j.iterrows():
                if uid in job_nlargest_uid_0:
                    print('uid:', uid)
                    jobs_week_uid_dict[uid][idx] = row['count']
                else:
                    jobs_week_uid_dict[0][idx] += row['count']
            idx += 1

        self.jobs_per_week_per_users = pd.DataFrame(jobs_week_uid_dict)

    def gene_procs_per_week_per_user(self):
        pass

    def generate_swf_log_dfs(self):
        '''Generate dataframes usable to plot swf log graphs'''
        print("Generate arriving_each_day dataframe")
        self.gene_arriving_each_day()
        print("Generate arriving_each_hour dataframe")
        self.gene_arriving_each_hour()
