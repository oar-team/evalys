# coding: utf-8
from __future__ import unicode_literals, print_function
import pandas as pd
import re
from intsetwrap import string_to_interval_set, interval_set_to_set, \
                          set_to_interval_set, interval_set_to_string

class PowerStatesChanges(object):
    def __init__(self, filename):
        df = pd.read_csv(filename)

        for col_name in ['time', 'new_pstate', 'machine_id']:
            assert(col_name in df), "Invalid input file: should contain a '{}' "\
                                    "column".format(col_name)
        assert(df['time'].count() > 0), "Invalid input file: should contain at least 1 row"

        init = df.loc[df['time'] == 0]

        # Let's initialize the pstate of each machine
        current_pstate = {}
        assert(init['time'].count() > 0), "Invalid input file: no init row (one at time = 0)"

        r = re.compile(r"(\d+)\.0+")

        for index, row in init.iterrows():
            time = float(row['time'])
            pstate = int(row['new_pstate'])
            res_str = str(row['machine_id'])

            # Pandas/Python/Anything else may use 0.0 instead of 0...
            res_str = r.sub(r"\1", res_str)

            res_intervals = string_to_interval_set(res_str)
            res_set = interval_set_to_set(res_intervals)

            for res in res_set:
                if res in current_pstate:
                    print("Warning : multiple initialization of machine {}".format(res))
                current_pstate[res] = (pstate, time)

        # Let's add a finish row
        all_machines = set([res for res in current_pstate])
        all_machines_str = interval_set_to_string(set_to_interval_set(all_machines))

        finish_df = pd.DataFrame(index=[0], columns=['time', 'machine_id', 'new_pstate'])
        finish_df.iloc[0] = [float('inf'), all_machines_str, 42]
        df = df.append(finish_df)

        # Let's traverse the dataframe to create rectangles
        after_init = df.loc[df['time'] > 0]
        jobs = []
        after_init = after_init.sort_values(by = 'time')

        for index, row in after_init.iterrows():
            time = float(row['time'])
            pstate = int(row['new_pstate'])
            res_str = str(row['machine_id'])

            # Pandas/Python/Anything else may use 0.0 instead of 0...
            res_str = r.sub(r"\1", res_str)

            res_intervals = string_to_interval_set(res_str)
            res_set = interval_set_to_set(res_intervals)

            # All resources of this row had their pstate changed
            # Let's group them by previous pstate and by time to create 'jobs'
            previous_pstates = {}

            for res in res_set:
                previous_pstate, previous_time = current_pstate[res]
                if (previous_pstate, previous_time) in previous_pstates:
                    previous_pstates[(previous_pstate, previous_time)].add(res)
                else:
                    previous_pstates[(previous_pstate, previous_time)] = set([res])

            # Let's create the different 'jobs'
            for (previous_pstate, previous_time) in previous_pstates:
                res_set = previous_pstates[(previous_pstate, previous_time)]
                res_str = ' '.join(str(x) for x in res_set)
                res_intervals = string_to_interval_set(res_str)

                job = [previous_time, time, previous_pstate, res_intervals]
                jobs.append(job)

                # Let's update current pstate
                for res in res_set:
                    current_pstate[res] = (pstate, time)

        # Let's create a 'jobs' dataframe
        self.pseudo_jobs = pd.DataFrame(index = range(len(jobs)),
                                        columns = ['begin', 'end', 'pstate',
                                                   'interval_id'])
        # Let's traverse all the jobs:
        #   1. Let's put resource intervals in another field
        #   2. Let's use a resource_id instead
        #   3. Let's add it into the dataframe
        self.intervals = {}

        for i in range(len(jobs)):
            (begin, end, pstate, res_intervals) = jobs[i]
            self.intervals[i] = res_intervals
            self.pseudo_jobs.loc[i] = [begin, end, pstate, i]

        # compute resources bounds
        # (+1 for max because of visu alignment over the job number line)
        self.res_bounds = (
            min(all_machines),
            max(all_machines) + 1)

'''
time,machine_id,new_pstate
0,0-31,0
6.1,1-31,13
205.716,1-3,0
305.026,4-7,0
392.394,8-15,0
16486.4,4-5,13
16486.4,10-11,13
16559.3,9,13
16665.8,6,13
16739.7,12-13,13
16752.2,7-8,13
16752.2,2-3,13
17067.5,14-15,13
17080,0-1,13
'''
