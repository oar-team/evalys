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
    parser.add_argument('--priority-job-waiting-time-bound',
                        type=float,
                        help='If set, draws an horizon line corresponding to this bound')

    parser.add_argument('--time-window', nargs='+',
                        type=float,
                        help="If set, limits the time window of study. Example: 0 4200")

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
                        help="If set, the resource usage will be outputted. Requires machine states")
    parser.add_argument("--power", action='store_true',
                        help="If set, the instantaneous power will be outputted. Requires energyCSV")
    parser.add_argument("--energy", action='store_true',
                        help="If set, the cumulated energy consumption will be outputted. Requires energyCSV")
    parser.add_argument('--llh', action='store_true',
                        help='If set, the LLH will be outputted. Requires llhCSV. Jobs are optional.')
    parser.add_argument('--load-in-queue', action='store_true',
                        help='If set, the load in queue will be outputted. Requires llhCSV.')
    parser.add_argument('--nb-jobs-in-queue', action='store_true',
                        help='If set, the number of jobs in queue will be outputted. Requires llhCSV.')
    parser.add_argument('--priority-job-size', action='store_true',
                        help='If set, the size of the priority job will be outputted. Requires llhCSV.')
    parser.add_argument('--priority-job-expected-waiting-time', action='store_true',
                        help='If set, the expected waiting time of the priority job will be outputted. Requires llhCSV.')
    parser.add_argument('--priority-job-starting-expected-soon', action='store_true',
                        help='If set, whether the priority job is expected to start soon will be outputted. Requires llhCSV')

    args = parser.parse_args()


    ###################
    # Figure creation #
    ###################
    nb_instances = None
    nb_subplots = 0
    left_adjust = 0.05
    top_adjust = 0.95
    bottom_adjust = 0.05
    right_adjust = 0.95

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
        right_adjust = min(right_adjust, 0.85)

        nb_ru = len(args.mstatesCSV)
        nb_subplots += nb_ru

        if nb_instances is not None:
            assert(nb_instances == nb_ru), 'Inconsistent number of instances (nb_ru={} but already got nb_instances={})'.format(nb_ru, nb_instances)
        else:
            nb_instances = nb_ru

    if args.power:
        assert(args.energyCSV), "EnergyCSV must be given to compute power!"
        nb_subplots += 1

    if args.energy:
        assert(args.energyCSV), "EnergyCSV must be given to compute energy!"

        nb_energy = 1
        nb_subplots += nb_energy

    if args.energyCSV:
        nb_energy_csv = len(args.energyCSV)

        if nb_instances is not None:
            assert(nb_instances == nb_energy_csv), 'Inconsistent number of instances (nb_energy_csv={} but already got nb_instances={})'.format(nb_energy_csv, nb_instances)
        else:
            nb_instances = nb_energy_csv

    if args.llh:
        assert(args.llhCSV), "LLH_CSV must be given to compute llh!"
        right_adjust = min(right_adjust, 0.85)
        nb_subplots += 1

    if args.load_in_queue:
        assert(args.llhCSV), "LLH_CSV must be given to compute llh!"
        nb_subplots += 1

    if args.nb_jobs_in_queue:
        assert(args.llhCSV), "LLH_CSV must be given to compute the queue!"
        nb_subplots += 1

    if args.priority_job_size:
        assert(args.llhCSV), "LLH_CSV must be given to compute the priority job size!"
        nb_subplots += 1

    if args.priority_job_expected_waiting_time:
        assert(args.llhCSV), "LLH_CSV must be given to compute the priority job size!"
        nb_subplots += 1

    if args.priority_job_starting_expected_soon:
        assert(args.llhCSV), "LLH_CSV must be given to compute the priority job size!"
        nb_subplots += 1

    if args.llhCSV:
        nb_llh_csv = len(args.llhCSV)
        if nb_instances is not None:
            assert(nb_instances == nb_llh_csv), 'Inconsistent number of instances (nb_llh_csv={} but already got nb_instances={})'.format(nb_llh_csv, nb_instances)
        else:
            nb_instances = nb_llh_csv

    if nb_subplots == 0:
        print('There is nothing to plot!')
        sys.exit(0)

    names = args.names
    assert(nb_instances == len(names)), 'The number of names ({} in {}) should equal the number of instances ({})'.format(len(names), names, nb_instances)

    fig, ax_list = plt.subplots(nb_subplots, sharex = True, sharey = False)
    fig.subplots_adjust(bottom=bottom_adjust,
                        right=right_adjust,
                        top=top_adjust,
                        left=left_adjust)
    #fig.tight_layout()
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
    power = list()
    if args.energyCSV:
        for csv_filename in args.energyCSV:
            energy_data = pd.read_csv(csv_filename)

            # Drop values outside the time window
            if time_min is not None:
                energy_data = energy_data.loc[energy_data['time'] >= time_min]
            if time_max is not None:
                energy_data = energy_data.loc[energy_data['time'] <= time_max]
            energy.append(energy_data)

            if args.power:
                df = energy_data.drop_duplicates(subset='time')
                df = df.drop(['event_type', 'wattmin', 'epower'], axis=1)
                diff = df.diff(1)
                diff.rename(columns={'time':'time_diff', 'energy':'energy_diff'},
                            inplace=True)
                joined = pd.concat([df, diff], axis=1)
                joined['power'] = joined['energy_diff'] / joined['time_diff']
                power.append(joined)

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
    legends = list()
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
    if args.power:
        for i,power_data in enumerate(power):
            ax_list[ax_id].plot(power_data['time'], power_data['power'],
                                label=names[i],
                                drawstyle='steps-pre')

        ax_list[ax_id].set_title('Power (W)')
        ax_list[ax_id].legend(loc='center left', bbox_to_anchor=(1, 0.5))
        ax_id = ax_id + 1

    # Energy
    if args.energy:
        for i,energy_data in enumerate(energy):

            ax_list[ax_id].plot(energy_data['time'], energy_data['energy'],
                                label=names[i])

        ax_list[ax_id].set_title('Energy (J)')
        ax_list[ax_id].legend(loc='center left', bbox_to_anchor=(1, 0.5))
        ax_id = ax_id + 1

    # Unresponsiveness estimation
    if args.llh:
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
                                       label='{} Waiting Time (s)'.format(names[i]))

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

    # Number of jobs in queue
    if args.nb_jobs_in_queue:
        for i,llh_data in enumerate(llh):
            ax_list[ax_id].plot(llh_data['date'],
                                llh_data['nb_jobs_in_queue'],
                                label='{}'.format(names[i]),
                                drawstyle="steps-post")
        ax_list[ax_id].set_title('Number of jobs in queue')
        ax_list[ax_id].legend(loc='center left', bbox_to_anchor=(1, 0.5))
        ax_id = ax_id + 1

    # Load in queue
    if args.load_in_queue:
        for i,llh_data in enumerate(llh):
            ax_list[ax_id].plot(llh_data['date'],
                                llh_data['load_in_queue'],
                                label='{}'.format(names[i]),
                                drawstyle="steps-post")
        ax_list[ax_id].set_title('Load in queue (nb_res * seconds)')
        ax_list[ax_id].legend(loc='center left', bbox_to_anchor=(1, 0.5))
        ax_id = ax_id + 1

    # Priority job size
    if args.priority_job_size:
        for i,llh_data in enumerate(llh):
            ax_list[ax_id].plot(llh_data['date'],
                                llh_data['first_job_size'],
                                label='{}'.format(names[i]),
                                drawstyle="steps-post")
        ax_list[ax_id].set_title('Number of requested resources of the priority job')
        ax_list[ax_id].legend(loc='center left', bbox_to_anchor=(1, 0.5))
        ax_id = ax_id + 1

    # Priority job expected waiting time
    if args.priority_job_expected_waiting_time:
        if args.priority_job_waiting_time_bound:
            min_x = float('inf')
            max_x = float('-inf')
        for i,llh_data in enumerate(llh):
            ax_list[ax_id].plot(llh_data['date'],
                                llh_data['priority_job_expected_waiting_time'],
                                label='{}'.format(names[i]),
                                drawstyle="steps-post")
            if args.priority_job_waiting_time_bound:
                min_x = min(min_x, llh_data['date'].min())
                max_x = max(max_x, llh_data['date'].max())

        if args.priority_job_waiting_time_bound:
            priority_job_waiting_time_bound = args.priority_job_waiting_time_bound
            # Plots a hline
            ax_list[ax_id].plot([min_x, max_x],
                                [priority_job_waiting_time_bound, priority_job_waiting_time_bound],
                                linestyle='-', linewidth=2,
                                label="Bound ({})".format(priority_job_waiting_time_bound))
        ax_list[ax_id].set_title('Expected waiting time of the priority job (s)')
        ax_list[ax_id].legend(loc='center left', bbox_to_anchor=(1, 0.5))
        ax_id = ax_id + 1

    # Whether priority job is expected to start soon
    if args.priority_job_starting_expected_soon:
        for i,llh_data in enumerate(llh):
            ax_list[ax_id].plot(llh_data['date'],
                                llh_data['priority_job_starting_expected_soon'],
                                label='{}'.format(names[i]),
                                drawstyle="steps-post")
        ax_list[ax_id].set_title('Is the priority job expected to start soon ?')
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
