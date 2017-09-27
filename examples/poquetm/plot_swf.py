#!/usr/bin/env python3

import sys
import argparse

import seaborn
from evalys import *
from evalys.visu.legacy import *
from evalys.workload import *

import pandas as pd
import matplotlib.pyplot as plt

def main():
    # Argument parsing
    parser = argparse.ArgumentParser(description='Draws the states the machines are in over time')
    parser.add_argument('--swf-workload', '-w',
                        required=True,
                        help='The name of the SWF workload file')

    parser.add_argument('--output', '-o',
                        help='The output file (format depending on the given extension, pdf is RECOMMENDED). For example: figure.pdf')

    parser.add_argument("--with_details", '-d',
                        action='store_true',
                        help="If set, more details about jobs will be displayed.")

    args = parser.parse_args()


    # Create data structures from input args
    workload = Workload.from_csv(args.swf_workload)

    with_details = False
    if args.with_details:
        with_details = True

    # Plotting
    workload.plot(with_details=with_details)

    # Figure outputting
    if args.output is not None:
        plt.savefig(args.output)
    else:
        plt.show()

if __name__ == "__main__":
    main()
