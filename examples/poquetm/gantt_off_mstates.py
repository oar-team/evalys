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
    parser.add_argument('--off', nargs='+',
                        help='The power states which correspond to OFF machine states')
    parser.add_argument('--switchon', nargs='+',
                        help='The power states which correspond to a switching ON machine state')
    parser.add_argument('--switchoff', nargs='+',
                        help='The power states which correspond to switching OFF machine state')
    parser.add_argument('--output', '-o',
                        help='The output file (format depending on the given extension, pdf is RECOMMENDED). For example: figure.pdf')
    parser.add_argument("--no_gantt", action='store_true',
                        help="If set, the gantt chart will NOT be outputted")
    parser.add_argument("--no_ru", action='store_true',
                        help="If set, the resource usage will NOT be outputted")

    args = parser.parse_args()

    # Create data structures from input args
    j = JobSet.from_csv(args.jobsCSV)
    c = PowerStatesChanges(args.pstatesCSV)
    m = MachineStatesChanges(args.mstatesCSV)

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
    nb_subplots = 0

    if not args.no_gantt:
        nb_subplots = nb_subplots + 1

    if not args.no_ru:
        nb_subplots = nb_subplots + 1

    if args.energyCSV:
        nb_subplots = nb_subplots + 1
    if args.llhCSV:
        #nb_subplots = nb_subplots + 2
        nb_subplots = nb_subplots + 1

    fig, ax_list = plt.subplots(nb_subplots, sharex = True, sharey = False)
    if nb_subplots < 2:
        ax_list = [ax_list]

    # Plotting
    ax_id = 0
    if not args.no_gantt:
        plot_gantt_pstates(j, c, ax_list[ax_id],
                           title="Gantt chart",
                           labels=False,
                           off_pstates = off_pstates,
                           son_pstates = son_pstates,
                           soff_pstates = soff_pstates)
        ax_id = ax_id + 1

    if not args.no_ru:
        plot_mstates(m.df, ax_list[ax_id], title="Resources state")
        ax_list[ax_id].legend(loc='center left', bbox_to_anchor=(1, 0.5))
        ax_id = ax_id + 1

    if args.energyCSV:
        e = pd.read_csv(args.energyCSV)
        e.dropna(axis=0, how='any', subset=['epower'], inplace=True)
        e.sort_values(inplace=True, by='time')
        ax_list[ax_id].plot(e['time'], e['epower'], label='Power (W)', drawstyle="steps-pre")
        #ax_list[ax_id].scatter(e['time'], e['epower'], label='Electrical power (W)')
        ax_list[ax_id].set_title(args.energyCSV)
        ax_list[ax_id].legend(loc='center left', bbox_to_anchor=(1, 0.5))
        ax_id = ax_id + 1

    if args.llhCSV:
        llh = pd.read_csv(args.llhCSV)

        # LLH
        ax_list[ax_id].plot(llh['date'], llh['liquid_load_horizon'], label="Liquid load horizon (s)")
        ax_list[ax_id].scatter(j.df['submission_time'], j.df['waiting_time'], label="Waiting time (s)")
        ax_list[ax_id].set_title(args.llhCSV)
        ax_list[ax_id].legend(loc='center left', bbox_to_anchor=(1, 0.5))
        ax_id = ax_id + 1

        # Load in queue
        # ax_list[ax_id].plot(llh['date'], llh['load_in_queue'], label="Load in queue (s*r)")
        # ax_list[ax_id].set_title(args.llhCSV)
        # ax_list[ax_id].legend(loc='center left', bbox_to_anchor=(1, 0.5))
        # ax_id = ax_id + 1

    # Figure outputting
    if args.output is not None:
        plt.savefig(args.output)
    else:
        plt.show()

if __name__ == "__main__":
    main()
