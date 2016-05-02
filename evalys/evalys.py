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
from evalys.visu import plot_gantt_general_shape


def main():
    parser = argparse.ArgumentParser(description='Generate Gantt charts '
                                     'from Batsim CSV job file.')
    parser.add_argument('inputCSV', nargs='+', help='The input CSV file(s)')
    parser.add_argument('-o', '--output', nargs='?',
                        help='The output Gantt chart file depending on the extension (PDF format is RECOMMENDED). For example: figure.pdf')
    parser.add_argument('-s', '--draw_shape',
                        dest='draw_shape',
                        action='store_true',
                        default=False,
                        help='Generate a general shape gantt comparison between inputs')

    args = parser.parse_args()
    if NO_GRAPHICS and not args.output:
        print("No available display: please provide an output using the -o,--output option")
        exit(1)

    # generate subplot
    if args.draw_shape:
        fig, ax_list = plt.subplots(len(args.inputCSV) + 1, sharex=True,
                                    sharey=True)
        ax_shape = ax_list[-1:][0]
        ax_list = ax_list[:-1]
    else:
        fig, ax_list = plt.subplots(len(args.inputCSV), sharex=True,
                                sharey=True)

    # manage unique ax probleme
    try:
        iter(ax_list)
    except:
        ax_list = [ax_list]
    else:
        ax_list = list(ax_list)

    # generate gantt chart from CSV inputs
    jobsets = {}
    for ax, inputCSV in zip(ax_list, sorted(args.inputCSV)):
        js = JobSet(inputCSV)
        js.gantt(ax, os.path.basename(inputCSV))
        jobsets[inputCSV] = js

    if args.draw_shape:
        plot_gantt_general_shape(jobsets, ax_shape)

    # set axes and resources
    x_axes_min_value = min({m.df.submission_time.min()
                            for m in jobsets.values()})
    x_axes_max_value = max({m.df.finish_time.max() for m in jobsets.values()})
    y_axes_min_value = min([js.res_bounds[0] for js in jobsets.values()])
    y_axes_max_value = max([js.res_bounds[1] for js in jobsets.values()])
    x_size = x_axes_max_value - x_axes_min_value
    y_size = y_axes_max_value - y_axes_min_value

    print("x = ({},{})".format(x_axes_min_value, x_axes_max_value))
    print("y = ({},{})".format(y_axes_min_value, y_axes_max_value))
    print("x size = {}".format(x_size))
    print("y size = {}".format(y_size))

    for ax in ax_list:
        ax.set_xlim((x_axes_min_value, x_axes_max_value))
        ax.set_ylim((y_axes_min_value, y_axes_max_value))

    # Cosmetic changes
    # plt.subplots_adjust(left=0.0, right=1.0, bottom=0.0, top=1.0)
    fig.set_tight_layout(True)
    y_inches = max(y_size * len(ax_list) * 0.15, 8)
    if args.draw_shape:
        y_inches += y_size * 0.15
    fig.set_size_inches(y_inches * 1.7,
                        y_inches,
                        forward=True)

    if args.output is not None:
        plt.savefig(args.output)
    else:
        plt.show()

if __name__ == "__main__":
    main()
