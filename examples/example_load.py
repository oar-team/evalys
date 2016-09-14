#! /usr/bin/env python3

import argparse
import matplotlib.pyplot as plt

from evalys.visu import plot_load
from evalys.jobset import JobSet


def main():
    # Argument parsing
    parser = argparse.ArgumentParser(description='Display the load of each processor.')
    parser.add_argument('jobsCSV',
                        help='The name of the CSV file which contains jobs information')
    parser.add_argument('--output', '-o',
                        help='The output file (format depending on the given extension, pdf is RECOMMENDED). For example: figure.pdf')
    parser.add_argument('--title', default = 'Load',
                        help="Sets the subplot title")

    args = parser.parse_args()

    # Create data structures from input args
    j = JobSet.from_csv(args.jobsCSV)

    # Figure creation
    nb_subplots = 1
    fig, ax_list = plt.subplots(nb_subplots, sharex = True, sharey = True)
    if nb_subplots < 2:
        ax_list = [ax_list]

    # Plot
    plot_load(j, ax_list[0], str(args.title))

    # Figure outputting
    if args.output is not None:
        plt.savefig(args.output)
    else:
        plt.show()

if __name__ == "__main__":
    main()
