# coding: utf-8
from __future__ import unicode_literals, print_function
import pandas as pd


class Workload(object):
    def __init__(self, **kwargs):
        if 'file' in kwargs:
            # swf is the default format
            # see: http://www.cs.huji.ac.il/labs/parallel/workload/swf.html
            #
            # the data format is one line per job, with 18 fields:
            #  0 - Job Number
            #  1 - Submit Time
            #  2 - Wait Time
            #  3 - Run Time
            #  4 - Number of Processors
            #  5 - Average CPU Time Used
            #  6 - Used Memory
            #  7 - Requested Number of Processors
            #  8 - Requested Time
            #  9 - Requested Memory
            # 10 - status (1=completed, 0=killed)
            # 11 - User ID
            # 12 - Group ID
            # 13 - Executable (Application) Number
            # 14 - Queue Number
            # 15 - Partition Number
            # 16 - Preceding Job Number
            # 17 - Think Time from Preceding Job
            #
            columns = ['Job', 'Submit Time', 'Wait Time', 'Run Time', 'Nb Alloc Proc', 'Average CPU',
                       'Used Memory', 'Req Nb Proc', 'Req Time', 'Req Memory', 'Status', 'User',
                       'Group', 'Application', 'Queue', 'Partition', 'Preceding Job', 'Think Time']
            self.df = pd.read_csv(kwargs['file'], comment=';', names=columns, header=0, delim_whitespace=True)

    def swf_log_describe():
        ''' will '''
        pass
