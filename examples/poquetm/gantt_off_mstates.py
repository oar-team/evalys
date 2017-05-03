#!/usr/bin/env python3

import sys
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
    parser.add_argument('--mstatesCSV', '-m',
                        help='The name of the CSV file which contains pstate information')
    parser.add_argument('--jobsCSV', '-j',
                        help='The name of the CSV file which contains jobs information')
    parser.add_argument('--pstatesCSV', '-p',
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

    parser.add_argument("--gantt", action='store_true',
                        help="If set, the gantt chart will be outputted. Requires jobs, pstates and probably machine values (--off, --switchon, --switchoff)")
    parser.add_argument("--ru", action='store_true',
                        help="If set, the resource usage will be outputted. Required machine states")

    args = parser.parse_args()


    # Figure creation
    nb_subplots = 0

    if args.gantt:
        nb_subplots = nb_subplots + 1
        assert(args.jobsCSV), "Jobs must be given to compute the gantt chart!"
        assert(args.pstatesCSV), "Pstates must be given to compute the gantt chart!"

    if args.ru:
        nb_subplots = nb_subplots + 1
        assert(args.mstatesCSV), "Mstates must be given to compute the resource usage!"

    if args.energyCSV:
        nb_subplots = nb_subplots + 1

    if args.llhCSV:
        #nb_subplots = nb_subplots + 2
        nb_subplots = nb_subplots + 1

    if nb_subplots == 0:
        print('There is nothing to plot!')
        sys.exit(0)

    fig, ax_list = plt.subplots(nb_subplots, sharex = True, sharey = False)
    if nb_subplots < 2:
        ax_list = [ax_list]


    # Create data structures from input args
    jobs = None
    if args.jobsCSV and args.gantt:
        jobs = JobSet.from_csv(args.jobsCSV)

    pstates = None
    if args.pstatesCSV and args.gantt:
        pstates = PowerStatesChanges(args.pstatesCSV)

    machines = None
    if args.mstatesCSV and args.ru:
        machines = MachineStatesChanges(args.mstatesCSV)

    llh = None
    if args.llhCSV:
        llh = pd.read_csv(args.llhCSV)

    energy = None
    if args.energyCSV:
        energy = pd.read_csv(args.energyCSV)

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


    # Plotting
    ax_id = 0
    if args.gantt:
        plot_gantt_pstates(jobs, pstates, ax_list[ax_id],
                           title="Gantt chart",
                           labels=False,
                           off_pstates = off_pstates,
                           son_pstates = son_pstates,
                           soff_pstates = soff_pstates)
        ax_id = ax_id + 1

    if args.ru:
        plot_mstates(machines.df, ax_list[ax_id], title="Resources state")
        ax_list[ax_id].legend(loc='center left', bbox_to_anchor=(1, 0.5))
        ax_id = ax_id + 1

    if args.energyCSV:
        energy.dropna(axis=0, how='any', subset=['epower'], inplace=True)
        energy.sort_values(inplace=True, by='time')
        ax_list[ax_id].plot(energy['time'], energy['epower'],
                            label='Power (W)', drawstyle="steps-pre")
        #ax_list[ax_id].scatter(e['time'], e['epower'], label='Electrical power (W)')
        ax_list[ax_id].set_title(args.energyCSV)
        ax_list[ax_id].legend(loc='center left', bbox_to_anchor=(1, 0.5))
        ax_id = ax_id + 1

    if args.llhCSV:
        # LLH
        ax_list[ax_id].plot(llh['date'], llh['liquid_load_horizon'], label="Liquid load horizon (s)")
        ax_list[ax_id].scatter(jobs.df['submission_time'],
                               jobs.df['waiting_time'], label="Waiting time (s)")
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
