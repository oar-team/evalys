#!/usr/bin/python3
'''
This script provides gantt chart view of one or
several CSV job file from Batsim using *evalys*
module.
'''

import argparse
import os
import matplotlib.pyplot as plt
from evalys.jobset import JobSet


def main():
    parser = argparse.ArgumentParser(description='Generate Gantt charts '
                                     'from Batsim CSV job file.')
    parser.add_argument('inputCSV', nargs='+', help='The input CSV file(s)')

    args = parser.parse_args()

    fig, ax_list = plt.subplots(len(args.inputCSV), sharex=True,
                                sharey=True)
    if not isinstance(ax_list, list):
        ax_list = [ax_list]

    jobsets = {}
    for ax, inputCSV in zip(ax_list, sorted(args.inputCSV)):
        js = JobSet(inputCSV)
        js.gantt(ax, os.path.basename(inputCSV))
        jobsets[inputCSV] = js

    #import ipdb; ipdb.set_trace()
    # ax.set_xlim((min({m.df.submission_time.min() for m in
    #                   jobsets.values()}),
    #              max({m.df.finish_time.max() for m in jobsets.values()})))
    # ax.set_ylim((min([js.res_bounds for js in jobsets.values()],
    #                     key=lambda x: (x, y)),
    #                 max([(x, y) = js.res_bounds for js in jobsets.values()],
    #                     key=lambda y: (x, y))))

    plt.show()

if __name__ == "__main__":
    main()
