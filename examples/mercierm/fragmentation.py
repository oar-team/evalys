"""
    Show fragmentation of free slots one one or several jobsets

Usage:
    fragmentation.py <jobset_csv_files> ... [-h]

Options:
    -h --help      show this help message and exit.
"""

from evalys import interval_set
from evalys.jobset import JobSet
import numpy as np
import matplotlib.pyplot as plt
import docopt


def compute_fragmentation(fs):
    fs["total"] = fs.allocated_processors.apply(
        lambda x: interval_set.total(interval_set.string_to_interval_set(x)))

    area = np.repeat(fs.execution_time, fs["total"])
    area = fs["total"] * fs["execution_time"]

    filtred_e = area[
        lambda x: x > area.quantile(0.15)][
            lambda x: x < area.quantile(0.85)]

    frag = {}
    frag['max'] = 1 - (filtred_e.max() / filtred_e.sum())
    frag['mean'] = 1 - (filtred_e.mean() / filtred_e.sum())
    frag['median'] = 1 - (filtred_e.median() / filtred_e.sum())
    frag['q1'] = 1 - (filtred_e.quantile(0.25) / filtred_e.sum())
    frag['q3'] = 1 - (filtred_e.quantile(0.75) / filtred_e.sum())

    print("fragmentation: {}".format(frag))
    return filtred_e


def plot_fragmentation(frag, axe, label):
    frag.hist(bins=20, ax=axe[0], alpha=0.5, label=label)
    sq = frag.value_counts()
    ecdf = sq.sort_index().cumsum()
    ecdf.plot(ax=axe[1], label=label)


def compare_jobsets_fragmentation(files):

    _, axe = plt.subplots(nrows=2)

    for f in files:
        js = JobSet.from_csv(f)
        fs = js.free_slots()
        frag = compute_fragmentation(fs)
        plot_fragmentation(frag, axe, f.split("/")[-1:][0])

    axe[1].grid(True)
    plt.legend(loc="lower right")
    plt.show()

if __name__ == "__main__":
    # retrieving arguments
    arguments = docopt.docopt(__doc__)
    compare_jobsets_fragmentation(arguments['<jobset_csv_files>'])
