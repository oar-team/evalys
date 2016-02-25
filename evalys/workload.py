# coding: utf-8
from __future__ import unicode_literals, print_function
import pandas as pd
import re


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

    def swf_log_describe(self):
        ''' will '''
        pass

    def plot_arriving_each_day_by_week(self):
        pass
