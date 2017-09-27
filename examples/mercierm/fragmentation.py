"""
    Show fragmentation of free slots one one or several jobsets

Usage:
    fragmentation.py <jobset_csv_files> ... [-h]

Options:
    -h --help      show this help message and exit.
"""

from evalys.jobset import JobSet
from evalys.visu.legacy import plot_fragmentation
import matplotlib.pyplot as plt
import docopt
import pandas as pd
import seaborn as sns


def fragmentation_from_CCGRID(js, size, p=2):
    """ NOT WORKING """
    fs = js.free_resources_gaps()

    ftotal = 0
    num = 0
    for i in range(size):
        df = fs.nb_resources[lambda x: x >= i]
        if df.sum() == 0:
            continue
        f = 1 - ((df**p).sum() / df.sum()**p)
        if f != 0:
            ftotal = ftotal + f
            num = num + 1

    return ftotal / num


def compare_jobsets_fragmentation(files):

    width = 10
    height = 10
    fig, axe = plt.subplots(nrows=3, figsize=(width, height))

    frag_serie = pd.Series()
    for f in files:
        js = JobSet.from_csv(f, resource_bounds=(0, 239))
        frag = js.fragmentation()
        label = f.split("/")[-1:][0]
        mean_frag = frag.mean()
        frag_serie.set_value(label, round(mean_frag, 2))

        label = label + '(mean frag: {0:.2f})'.format(mean_frag)
        plot_fragmentation(frag, axe, label)

    axe[0].legend()

    return frag_serie


if __name__ == "__main__":
    # retrieving arguments
    arguments = docopt.docopt(__doc__)
    sns.set()
    compare_jobsets_fragmentation(arguments['<jobset_csv_files>'])
    # plt.show()
