#!/usr/bin/python3

import argparse

import seaborn
from evalys import *
from evalys.mstates import *
from evalys.visu import *

import matplotlib.pyplot as plt

def main():
    # Argument parsing
    parser = argparse.ArgumentParser(description='Draws the states the machines are in over time')
    parser.add_argument('mstatesCSV', nargs='+',
                        help='The name of the CSV file which contains pstate information')
    parser.add_argument('--output', '-o',
                        help='The output file (format depending on the given extension, pdf is RECOMMENDED). For example: figure.pdf')

    args = parser.parse_args()

    # Create data structures from input args
    ms = [MachineStatesChanges(x) for x in args.mstatesCSV]

    # Figure creation
    nb_subplots = len(args.mstatesCSV)
    fig, ax_list = plt.subplots(nb_subplots, sharex = True, sharey = True)
    if nb_subplots < 2:
        ax_list = [ax_list]

    # Plotting
    for i, m in enumerate(ms):
        plot_mstates(m.df, ax_list[i], title=args.mstatesCSV[i])
        ax_list[i].legend(loc='center left', bbox_to_anchor=(1, 0.5))

    # Figure outputting
    if args.output is not None:
        plt.savefig(args.output)
    else:
        plt.show()

if __name__ == "__main__":
    main()
