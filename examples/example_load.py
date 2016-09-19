#! /usr/bin/env python3

import argparse
import matplotlib.pyplot as plt

from evalys.visu import plot_load
from evalys.jobset import JobSet


def main():
    # parse command line
    parser = argparse.ArgumentParser(
        description='Display the load of each processor.'
    )
    parser.add_argument(
        'jobsCSV',
        help='The name of the CSV file which contains jobs information'
    )
    parser.add_argument(
        '--output', '-o',
        help='The output file (format depending on the given extension, pdf'
        'is RECOMMENDED). For example: figure.pdf'
    )
    args = parser.parse_args()

    j = JobSet.from_csv(args.jobsCSV)  # create data structure from input args
    fig = plt.figure()  # create figure
    ax = fig.gca()  # extract axes
    plot_load(j, ax, str(args.jobsCSV))  # build visualization

    # show figure
    if args.output is not None:
        plt.savefig(args.output)
    else:
        plt.show()


if __name__ == "__main__":
    main()
