#!/usr/bin/env python3
"""
Extract time frame from a SWF trace with diffent level of utilisation.

Extract periods of 12 and 60 hours because it is what I need for Grid5000
experiments.

write 10 extracted periods by parameter combination to CSV files
"""

from evalys import workload
import pandas as pd
import os


def extract_periods(w, swf_trace):

    results_dir = "./results"
    variation = 0.1

    metadata = {
        'file': [],
        'begin': [],
        'end': [],
        'norm_util': [],
        'variation': [],
        'period_in_hours': [],
    }

    os.makedirs(results_dir, exist_ok=True)
    for period in [60]:

        for util in range(1, 10):
            res_table = w.extract_periods_with_given_utilisation(
                period, util / 10, variation=variation, nb_max=20)

            for i, results in enumerate(res_table):
                filename = "extracted_{}_{}H_{}util+-{}_{}".format(
                    swf_trace,
                    period, util * 10,
                    variation,
                    i)
                print("Export: {} \n{}".format(filename, results))
                filepath = results_dir + "/" + filename + ".swf"
                results.to_csv(filepath)
                # Add metadata
                metadata['file'].append(filename)
                metadata['begin'].append(results.ExtractBegin)
                metadata['end'].append(results.ExtractEnd)
                metadata['norm_util'].append(util / 10)
                metadata['variation'].append(variation)
                metadata['period_in_hours'].append(period)

    pd.DataFrame(data=metadata).to_csv(results_dir + "/extract_metadata.csv", index=False)


if __name__ == "__main__":
    swf_trace = "HPC2N-2002-2.2-cln"
    w = workload.Workload.from_csv("./" + swf_trace + ".swf")
    extract_periods(w, swf_trace)
