from evalys import interval_set
from evalys.jobset import JobSet
import numpy as np
import matplotlib.pyplot as plt


def compute_fragmentation(fs):
    fs["total"] = fs.allocated_processors.apply(
        lambda x: interval_set.total(interval_set.string_to_interval_set(x)))

    area = np.repeat(fs.execution_time, fs["total"])
    area = fs["total"] * fs["execution_time"]

    filtred_e = area[lambda x: x > area.quantile(0.15)][lambda x: x < area.quantile(0.85)]

    frag = {}
    frag['max'] = 1 - (filtred_e.max() / filtred_e.sum())
    frag['mean'] = 1 - (filtred_e.mean() / filtred_e.sum())
    frag['median'] = 1 - (filtred_e.median() / filtred_e.sum())
    frag['q1'] = 1 - (filtred_e.quantile(0.25) / filtred_e.sum())
    frag['q3'] = 1 - (filtred_e.quantile(0.75) / filtred_e.sum())

    print("fragmentation: {}".format(frag))
    return filtred_e


def plot_fragmentation(frag):
    _, axe = plt.subplots(nrows=2)
    frag.hist(bins=20, ax=axe[0])
    sq = frag.value_counts()
    ecdf = sq.sort_index().cumsum()*1./len(sq)
    ecdf.plot(ax=axe[1])


if __name__ == "__main__":
    js = JobSet.from_csv("~/scratch/small.csv")
    fs = js.free_slots()
    frag = compute_fragmentation(fs)
    plot_fragmentation(frag)

    plt.show()
