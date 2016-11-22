#!/usr/bin/env python3
"""
Extract time frame from a SWF trace with diffent level of utilisation.

Extract periods of 12 and 60 hours because it is what I need for Grid5000
experiments.

write 10 extracted periods by parameter combination to CSV files
"""

from evalys import workload
import os


def extract_periods(w, swf_trace):

    results_dir = "./results"
    variation = 0.02

    os.makedirs(results_dir, exist_ok=True)
    for periods in [12, 60]:

        for util in range(1, 10):
            res_table = w.extract_periods_with_given_utilisation(
                periods, util / 10, variation=variation)

            for results in res_table[:10]:
                filename = "extracted_{}_{}H_{}util+-{}_{}.swf".format(
                    swf_trace,
                    periods, util * 10,
                    variation,
                    results.UnixStartTime)
                print("Export: {} \n{}".format(filename, results))
                filepath = results_dir + "/" + filename
                results.to_csv(filepath)


if __name__ == "__main__":
    swf_trace = "HPC2N-2002-2.2-cln"
    w = workload.Workload.from_csv("./" + swf_trace + ".swf")
    extract_periods(w, swf_trace)
