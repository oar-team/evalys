#! /usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import timeit

from evalys.jobset import JobSet

parser = argparse.ArgumentParser()
parser.add_argument('method')
parser.add_argument('jobsCSV')
parser.add_argument('--number', '-n', default=10, type=int)
args = parser.parse_args()

js = JobSet.from_csv(args.jobsCSV)

print(
    '{};{};{}'.format(
        args.method,
        args.number,
        timeit.timeit(getattr(js, args.method), number=args.number)
    )
)
