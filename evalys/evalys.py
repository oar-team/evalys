#!/usr/bin/python3
'''
This script provides gantt chart view of one or
several CSV job file from Batsim using *evalys*
module.
'''

import argparse
import os
import matplotlib

NO_GRAPHICS = False
# Manage the case where the system as no display
if not os.environ.get('DISPLAY'):
    NO_GRAPHICS = True
    matplotlib.use('Agg')

import matplotlib.pyplot as plt
from evalys.jobset import JobSet


def main():
    parser = argparse.ArgumentParser(description='Generate Gantt charts '
                                     'from Batsim CSV job file.')
    parser.add_argument('inputCSV', nargs='+', help='The input CSV file(s)')
    parser.add_argument('-o', '--output', nargs='?',
                        help='The output Gantt chart file depending on the extension. For example: figure.svg')

    args = parser.parse_args()
    if NO_GRAPHICS and not args.output:
        print("No available display: please provide an output using the -o,--output option")
        exit(1)

    fig, ax_list = plt.subplots(len(args.inputCSV), sharex=True,
                                sharey=True)
    try:
        iter(ax_list)
    except:
        ax_list = [ax_list]
    else:
        ax_list = list(ax_list)

    jobsets = {}
    for ax, inputCSV in zip(ax_list, sorted(args.inputCSV)):
        js = JobSet(inputCSV)
        js.gantt(ax, os.path.basename(inputCSV))
        jobsets[inputCSV] = js

    ax.set_xlim((min({m.df.submission_time.min() for m in
                      jobsets.values()}),
                 max({m.df.finish_time.max() for m in jobsets.values()})))
    ax.set_ylim((min([js.res_bounds[0] for js in jobsets.values()]),
                    max([js.res_bounds[1] for js in jobsets.values()])))

    if args.output is not None:
        plt.savefig(args.output)
    else:
        plt.show()

if __name__ == "__main__":
    main()
