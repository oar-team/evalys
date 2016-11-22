#!/usr/bin/python3

import argparse

import seaborn
from evalys import *
from evalys.jobset import *
from evalys.mstates import *
from evalys.pstates import *
from evalys.visu import *
import pandas as pd

import matplotlib.pyplot as plt

def main():
    # Argument parsing
    parser = argparse.ArgumentParser(description='Draws the states the machines are in over time')
    parser.add_argument('--mstatesCSV', '-m', required=True,
                        help='The name of the CSV file which contains pstate information')
    parser.add_argument('--jobsCSV', '-j', required=True,
                        help='The name of the CSV file which contains jobs information')
    parser.add_argument('--pstatesCSV', '-p', required=True,
                        help='The name of the CSV file which contains pstate information')
    parser.add_argument('--energyCSV', '-e',
                        help='The name of the CSV file which contains energy consumption information')
    parser.add_argument('--llhCSV', '-l',
                        help='The name of the CSV file which contains LLH information')
    parser.add_argument('pstatesOFF', nargs='+',
                        help='The power states which correspond to OFF machine states')
    parser.add_argument('--output', '-o',
                        help='The output file (format depending on the given extension, pdf is RECOMMENDED). For example: figure.pdf')

    args = parser.parse_args()

    # Create data structures from input args
    j = JobSet.from_csv(args.jobsCSV)
    c = PowerStatesChanges(args.pstatesCSV)
    m = MachineStatesChanges(args.mstatesCSV)

    off_pstates = [int(x) for x in args.pstatesOFF]

    # Figure creation
    nb_subplots = 2
    if args.energyCSV:
        nb_subplots = nb_subplots + 1
    if args.llhCSV:
        nb_subplots = nb_subplots + 2

    fig, ax_list = plt.subplots(nb_subplots, sharex = True, sharey = False)
    if nb_subplots < 2:
        ax_list = [ax_list]

    # Plotting
    plot_gantt_pstates(j, c, ax_list[0], str(args.jobsCSV), labels=False,
                       off_pstates = off_pstates)

    plot_mstates(m.df, ax_list[1], title=args.mstatesCSV)
    ax_list[1].legend(loc='center left', bbox_to_anchor=(1, 0.5))

    ax_id = 2
    if args.energyCSV:
        e = pd.read_csv(args.energyCSV)
        #e['energy'] = e['energy'].diff(-1)
        ax_list[ax_id].plot(e['time'], e['energy'])
        ax_list[ax_id].set_title(args.energyCSV)
        ax_id = ax_id + 1

    if args.llhCSV:
        llh = pd.read_csv(args.llhCSV)

        # LLH
        ax_list[ax_id].plot(llh['date'], llh['liquid_load_horizon'], label="Liquid load horizon (s)")
        ax_list[ax_id].set_title(args.llhCSV)
        ax_list[ax_id].legend(loc='center left', bbox_to_anchor=(1, 0.5))
        ax_id = ax_id + 1

        # Load in queue
        ax_list[ax_id].plot(llh['date'], llh['load_in_queue'], label="Load in queue (s*r)")
        ax_list[ax_id].set_title(args.llhCSV)
        ax_list[ax_id].legend(loc='center left', bbox_to_anchor=(1, 0.5))
        ax_id = ax_id + 1

    # Figure outputting
    if args.output is not None:
        plt.savefig(args.output)
    else:
        plt.show()

if __name__ == "__main__":
    main()
