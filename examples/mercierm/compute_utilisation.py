from evalys import workload
from evalys.metrics import load_mean
import pandas as pd
from glob import glob
import matplotlib.pyplot as plt


def compute_overall_utilisation():
    '''
    Use all the swf file present in the curent directory to compute
    overall utilisation of the clusters.
    Write results to "overall_utilisation.csv" and return it.
    '''
    files = [f for f in glob('./swf_files/*.swf')]
    res = pd.Series()
    i = 0
    for f in files:
        print('Loading SWF file: {}'.format(f))
        try:
            wl = workload.Workload.from_csv(f)
            norm_util_mean = load_mean(wl.utilisation) / wl.MaxProcs
            print('Mean Util: {}\n'.format(norm_util_mean))
            res.set_value(f, norm_util_mean)
            i = i + 1
        except AttributeError as e:
            print("Unable to compute normalize mean: {}".format(e))
        finally:
            if wl:
                del wl
    print('{}'.format(res))
    print('{}'.format(res.mean()))
    print(res.describe())
    res.to_csv("overall_utilisation.csv")
    return res


def plot_overall_utilisation(ou):
    plt.style.use('ggplot')
    ou.plot(kind="hist")
    plt.axvline(ou.mean(), color='b', linestyle='dashed', linewidth=2)
    plt.savefig("overall_util_hist.pdf")
    plt.show()


if __name__ == "__main__":
    import os.path
    if os.path.isfile("overall_utilisation.csv"):
        ou = pd.Series.from_csv("overall_utilisation.csv")
    else:
        ou = compute_overall_utilisation()
    plot_overall_utilisation(ou)
