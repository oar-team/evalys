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
from evalys.visu import plot_gantt_general_shape, available_series, plot_series


def unique_file_name(file_dict, file_name, index=1):
    ''' check dict and return  a unique identifier for a file'''
    if file_dict.get(file_name) is None:
        return file_name
    file_name = file_name.replace(str(index - 1), "")
    return unique_file_name(file_dict, file_name + str(index), index=index + 1)


def main():
    parser = argparse.ArgumentParser(description='visualisation tool for scheduling trace and Batsim output file.')
    parser.add_argument('inputCSV', nargs='+', help='The input CSV file(s)')
    parser.add_argument('--gantt', '-g',
                        action='store_true',
                        default=False, help='Generate Gantt charts')
    parser.add_argument('--series', '-s',
                        nargs='?',
                        default=None,
                        const='all',
                        help='Generate timeseries on cumulative metrics.  Available metrics are: {}'.format(available_series))
    parser.add_argument('--output', '-o',
                        nargs='?',
                        help='The output Gantt chart file depending on the extension (PDF format is RECOMMENDED). For example: figure.pdf')
    parser.add_argument('--gantt_diff', '-d',
                        action='store_true',
                        default=False,
                        help='Generate a gantt diff comparison between inputs (no more than 3 recommended')

    args = parser.parse_args()
    if NO_GRAPHICS and not args.output:
        print("No available display: please provide an output using the -o,--output option")
        exit(1)

    # generate subplot
    nb_subplot = 0
    if args.gantt:
        nb_subplot += len(args.inputCSV)
    if args.gantt_diff:
        nb_subplot += 1
    if args.series:
        nb_subplot += 1
    if not args.gantt and not args.gantt_diff and not args.series:
        print("You must select at least one option (use -h to see available options)")
        exit(1)

    fig, ax_list = plt.subplots(nb_subplot, sharex=True,)
                                #sharey=True)

    # manage unique ax probleme
    try:
        iter(ax_list)
    except:
        ax_list = [ax_list]
    else:
        ax_list = list(ax_list)

    # backup all ax
    all_ax = list(ax_list)

    # reserve last plot for series
    if args.series:
        ax_series = ax_list[-1:][0]
        ax_list = ax_list[:-1]

    # reserve last remaining plot for gantt diff
    if args.gantt_diff:
        ax_shape = ax_list[-1:][0]
        ax_list = ax_list[:-1]

    # generate josets from CSV inputs
    jobsets = {}
    index = 0
    for inputCSV in sorted(args.inputCSV):
        js = JobSet.from_csv(inputCSV)
        file_name = os.path.basename(inputCSV)
        file_name = unique_file_name(jobsets, file_name)
        jobsets[file_name] = js
        if args.gantt:
            js.gantt(ax_list[index], file_name)
            index += 1

    if args.gantt_diff:
        plot_gantt_general_shape(jobsets, ax_shape)

    if args.series:
        plot_series(args.series, jobsets, ax_series)

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

    for ax in all_ax:
        ax.set_xlim((x_axes_min_value, x_axes_max_value))
        #ax.set_ylim((y_axes_min_value, y_axes_max_value))

    # Layout and cosmetic changes
    # plt.subplots_adjust(left=0.0, right=1.0, bottom=0.0, top=1.0)
    fig.set_tight_layout(True)
    y_inches = max(y_size * len(all_ax) * 0.15, 8)
    if args.gantt_diff:
        y_inches += y_size * 0.15
    fig.set_size_inches(y_inches * 1.7,
                        y_inches,
                        forward=True)

    if args.output is not None:
        plt.savefig(args.output)
    else:
        plt.show()

if __name__ == "__main__":
    print("WARNING: this command line interface is deprecated. Please, use "
          "evalys as a library instead.\nSee http://evalys.rtfd.io")
    main()
