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
    parser.add_argument('--mstatesCSV', '-m', nargs='+',
                        help='The name of the CSV file which contains pstate information')
    parser.add_argument('--jobsCSV', '-j', nargs='+',
                        help='The name of the CSV file which contains jobs information')
    parser.add_argument('--pstatesCSV', '-p', nargs='+',
                        help='The name of the CSV file which contains pstate information')
    parser.add_argument('--energyCSV', '-e', nargs='+',
                        help='The name of the CSV file which contains energy consumption information')
    parser.add_argument('--llhCSV', '-l', nargs='+',
                        help='The name of the CSV file which contains LLH information')

    parser.add_argument('--llh-bound',
                        type=float,
                        help='If set, draws a LLH horizontal line on this bound')

    parser.add_argument('--time-window', nargs='+',
                        type=float,
                        help="If set, limits the time window of study. Example: '0 4200'")

    parser.add_argument('--off', nargs='+',
                        help='The power states which correspond to OFF machine states')
    parser.add_argument('--switchon', nargs='+',
                        help='The power states which correspond to a switching ON machine state')
    parser.add_argument('--switchoff', nargs='+',
                        help='The power states which correspond to switching OFF machine state')

    parser.add_argument('--names', nargs='+',
                         default=['Unnamed'],
                         help='When multiple instances must be plotted, their names must be given via this parameter.')

    parser.add_argument('--output', '-o',
                        help='The output file (format depending on the given extension, pdf is RECOMMENDED). For example: figure.pdf')

    parser.add_argument("--gantt", action='store_true',
                        help="If set, the gantt chart will be outputted. Requires jobs, pstates and probably machine values (--off, --switchon, --switchoff)")
    parser.add_argument("--ru", action='store_true',
                        help="If set, the resource usage will be outputted. Required machine states")

    args = parser.parse_args()


    ###################
    # Figure creation #
    ###################
    nb_instances = None
    nb_subplots = 0

    if args.gantt:
        assert(args.jobsCSV), "Jobs must be given to compute the gantt chart!"
        assert(args.pstatesCSV), "Pstates must be given to compute the gantt chart!"

        nb_jobs_csv = len(args.jobsCSV)
        nb_pstates_csv = len(args.pstatesCSV)
        assert(nb_jobs_csv == nb_pstates_csv), "The number of jobs_csv ({}) should equal the number of pstates_csv ({})".format(nb_jobs_csv, nb_pstates_csv)
        nb_gantt = nb_jobs_csv

        nb_subplots += nb_gantt
        nb_instances = nb_gantt

    if args.ru:
        assert(args.mstatesCSV), "Mstates must be given to compute the resource usage!"

        nb_ru = len(args.mstatesCSV)
        nb_subplots += nb_ru

        if nb_instances is not None:
            assert(nb_instances == nb_ru), 'Inconsistent number of instances (nb_ru={} but already got nb_instances={})'.format(nb_ru, nb_instances)
        else:
            nb_instances = nb_ru

    if args.energyCSV:
        nb_energy_csv = len(args.energyCSV)
        nb_subplots += 1

        if nb_instances is not None:
            assert(nb_instances == nb_ru), 'Inconsistent number of instances (nb_energy_csv={} but already got nb_instances={})'.format(nb_energy_csv, nb_instances)
        else:
            nb_instances = nb_energy_csv

    if args.llhCSV:
        nb_llh_csv = len(args.llhCSV)
        nb_subplots += 1

        if nb_instances is not None:
            assert(nb_instances == nb_ru), 'Inconsistent number of instances (nb_llh_csv={} but already got nb_instances={})'.format(nb_llh_csv, nb_instances)
        else:
            nb_instances = nb_llh_csv

    if nb_subplots == 0:
        print('There is nothing to plot!')
        sys.exit(0)

    names = args.names
    assert(nb_instances == len(names)), 'The number of names ({} in {}) should equal the number of instances ({})'.format(len(names), names, nb_instances)

    fig, ax_list = plt.subplots(nb_subplots, sharex = True, sharey = False)
    if nb_subplots < 2:
        ax_list = [ax_list]

    ##########################################
    # Create data structures from input args #
    ##########################################
    time_min = None
    time_max = None
    if args.time_window:
        time_min, time_max = [float(f) for f in args.time_window]

    jobs = list()
    if args.jobsCSV and (args.gantt or args.llhCSV):
        for csv_filename in args.jobsCSV:
            jobs.append(JobSet.from_csv(csv_filename))

    pstates = list()
    if args.pstatesCSV and args.gantt:
        for csv_filename in args.pstatesCSV:
            pstates.append(PowerStatesChanges(csv_filename))

    machines = list()
    if args.mstatesCSV and args.ru:
        for csv_filename in args.mstatesCSV:
            machines.append(MachineStatesChanges(csv_filename, time_min, time_max))

    llh = list()
    if args.llhCSV:
        for csv_filename in args.llhCSV:
            llh_data = pd.read_csv(csv_filename)
            # Drop values outside the time window
            if time_min is not None:
                llh_data = llh_data.loc[llh_data['date'] >= time_min]
            if time_max is not None:
                llh_data = llh_data.loc[llh_data['date'] <= time_max]
            llh.append(llh_data)

    energy = list()
    if args.energyCSV:
        for csv_filename in args.energyCSV:
            energy_data = pd.read_csv(csv_filename)

            # Drop values outside the time window
            if time_min is not None:
                energy_data = energy_data.loc[energy_data['time'] >= time_min]
            if time_max is not None:
                energy_data = energy_data.loc[energy_data['time'] <= time_max]
            energy.append(energy_data)

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

    ############
    # Plotting #
    ############
    ax_id = 0
    # Gantt charts
    if args.gantt:
        for i,name in enumerate(names):
            plot_gantt_pstates(jobs[i], pstates[i], ax_list[ax_id],
                               title="Gantt chart: {}".format(name),
                               labels=False,
                               off_pstates = off_pstates,
                               son_pstates = son_pstates,
                               soff_pstates = soff_pstates)
            ax_id = ax_id + 1

    # Aggregated resource states
    if args.ru:
        for i,name in enumerate(names):
            plot_mstates(machines[i].df, ax_list[ax_id],
                         title="Resources state: {}".format(name))
            ax_list[ax_id].legend(loc='center left', bbox_to_anchor=(1, 0.5))
            ax_id = ax_id + 1

    # Power
    if args.energyCSV:
        for i,energy_data in enumerate(energy):
            energy_data.dropna(axis=0, how='any', subset=['epower'],
                               inplace=True)
            energy_data.sort_values(inplace=True, by='time')

            ax_list[ax_id].plot(energy_data['time'], energy_data['epower'],
                                label=names[i],
                                drawstyle="steps-pre")

        ax_list[ax_id].set_title('Power (W)')
        ax_list[ax_id].legend(loc='center left', bbox_to_anchor=(1, 0.5))
        ax_id = ax_id + 1

    # Unresponsiveness estimation
    if args.llhCSV:
        if args.llh_bound:
            min_x = float('inf')
            max_x = float('-inf')

        for i,llh_data in enumerate(llh):
            ax_list[ax_id].plot(llh_data['date'],
                                llh_data['liquid_load_horizon'],
                                label='{} LLH (s)'.format(names[i]))
            if args.jobsCSV:
                ax_list[ax_id].scatter(jobs[i].df['submission_time'],
                                       jobs[i].df['waiting_time'],
                                       label='{} Mean Waiting Time (s)'.format(names[i]))

            if args.llh_bound:
                min_x = min(min_x, llh_data['date'].min())
                max_x = max(max_x, llh_data['date'].max())

        if args.llh_bound:
            llh_bound = args.llh_bound

            # Plots a hline
            ax_list[ax_id].plot([min_x, max_x],
                                [llh_bound, llh_bound],
                                linestyle='-', linewidth=2,
                                label="LLH bound ({})".format(llh_bound))

        title = 'Unresponsiveness estimation'

        ax_list[ax_id].set_title(title)
        ax_list[ax_id].legend(loc='center left', bbox_to_anchor=(1, 0.5))
        ax_id = ax_id + 1

    #####################
    # Figure outputting #
    #####################
    if args.output is not None:
        plt.savefig(args.output)
    else:
        plt.show()

if __name__ == "__main__":
    main()
