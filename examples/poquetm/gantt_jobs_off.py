#!/usr/bin/env python3

import argparse

from evalys import *
from evalys.pstates import *
from evalys.visu import *
from evalys.jobset import *

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def main():
    # Argument parsing
    parser = argparse.ArgumentParser(description='Draws a Gantt composed of "usual" jobs and switched-off nodes')
    parser.add_argument('--jobsCSV', '-j', required=True,
                        help='The name of the CSV file which contains jobs information')
    parser.add_argument('--pstatesCSV', '-p', required=True,
                        help='The name of the CSV file which contains pstate information')
    parser.add_argument('--off', nargs='+',
                        help='The power states which correspond to OFF machine states')
    parser.add_argument('--switchon', nargs='+',
                        help='The power states which correspond to a switching ON machine state')
    parser.add_argument('--switchoff', nargs='+',
                        help='The power states which correspond to switching OFF machine state')
    parser.add_argument('--output', '-o',
                        help='The output file (format depending on the given extension, pdf is RECOMMENDED). For example: figure.pdf')
    parser.add_argument('--title', default = 'Gantt chart',
                        help="Sets the subplot title")

    args = parser.parse_args()

    # Create data structures from input args
    j = JobSet.from_csv(args.jobsCSV)
    c = PowerStatesChanges(args.pstatesCSV)

    off_pstates = set()
    son_pstates = set()
    soff_pstates = set()

    if args.off:
        off_pstates = set([int(x) for x in args.off])
    if args.switchon:
        son_pstates = set([int(x) for x in args.switchon])
    if args.switchoff:
        soff_pstates = set([int(x) for x in args.switchoff])

    assert((off_pstates & son_pstates) == set()), "pstate collision"
    assert((off_pstates & soff_pstates) == set()), "pstate collision"
    assert((son_pstates & soff_pstates) == set()), "pstate collision"

    # Figure creation
    nb_subplots = 1
    fig, ax_list = plt.subplots(nb_subplots, sharex = True, sharey = True)
    if nb_subplots < 2:
        ax_list = [ax_list]

    # Gantt plotting
    plot_gantt_pstates(j, c, ax_list[0], str(args.title), labels=False,
                       off_pstates=off_pstates,
                       son_pstates=son_pstates,
                       soff_pstates=soff_pstates)

    legend_job = mpatches.Patch(color='#8960b3', label="Job", alpha=0.3)
    legend_off = mpatches.Patch(color='#000000', label="OFF", alpha=0.6)
    legend_son = mpatches.Patch(color='#56ae6c', label="Switching ON", alpha=1)
    legend_soff = mpatches.Patch(color='#ba495b', label="Switching OFF", alpha=1)

    ax_list[0].legend(handles=[legend_job, legend_off, legend_son, legend_soff],
                      loc='center left', bbox_to_anchor=(1, 0.5))

    # Figure outputting
    if args.output is not None:
        plt.savefig(args.output)
    else:
        plt.show()

if __name__ == "__main__":
    main()
