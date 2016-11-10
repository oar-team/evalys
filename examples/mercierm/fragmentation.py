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
import pandas as pd
import seaborn as sns


def compute_fragmentation(fs):
    fs["nb_resources"] = fs.allocated_processors.apply(
        lambda x: interval_set.total(interval_set.string_to_interval_set(x)))

    area = np.repeat(fs.execution_time, fs["nb_resources"])
    # area = pd.Series(np.array(fs["total"] * fs["execution_time"],
    #                           dtype=np.float64))

    # filtred_e = area
    filtred_e = area[lambda x: x > area.quantile(0.10)]

    frag = {}
    frag['max'] = 1 - (filtred_e.max() / filtred_e.sum())
    frag['mean'] = 1 - (filtred_e.mean() / filtred_e.sum())
    frag['median'] = 1 - (filtred_e.median() / filtred_e.sum())
    frag['q1'] = 1 - (filtred_e.quantile(0.25) / filtred_e.sum())
    frag['q3'] = 1 - (filtred_e.quantile(0.75) / filtred_e.sum())

    print("fragmentation: {}".format(frag))
    return filtred_e


def plot_fragmentation(frag, axe, label):
    # frag.hist(bins=20, ax=axe[0], alpha=0.5, label=label)
    sns.distplot(frag, ax=axe[0], label=label, kde=False, rug=True)
    axe[0].set_title("Free slots area distribution")
    val_count = frag.value_counts()
    cum_sum = val_count.sort_index().cumsum()
    ecdf = cum_sum / cum_sum[cum_sum.index[-1]]
    ecdf.plot(ax=axe[1], label=label, title="Free slots area ecdf")


def compare_jobsets_fragmentation(files):

    _, axe = plt.subplots(nrows=2)

    for f in files:
        js = JobSet.from_csv(f)
        fs = js.free_slots()
        frag = compute_fragmentation(fs)
        label = f.split("/")[-1:][0]
        plot_fragmentation(frag, axe, label)
        fs = fs[lambda x: x.execution_time > 65]
        sns.jointplot(x="execution_time", y="nb_resources", data=fs,
                      label=label)

    axe[1].grid(True)
    plt.legend(loc="lower right")
    plt.show()

if __name__ == "__main__":
    # retrieving arguments
    arguments = docopt.docopt(__doc__)
    sns.set()
    compare_jobsets_fragmentation(arguments['<jobset_csv_files>'])
