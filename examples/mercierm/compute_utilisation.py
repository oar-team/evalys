from evalys import workload
import pandas as pd
from glob import glob
import matplotlib.pyplot as plt


def compute_overall_utilisation():
    '''
    Use all the swf file present in the curent directory to compute
    overall utilisation of the clusters.
    Write results to "overall_utilisation.csv" and return it.
    '''
    files = [f for f in glob('./*.swf')]
    res = pd.Series()
    i = 0
    for f in files:
        wl = workload.Workload.from_csv(f)
        try:
            norm_util = wl.utilisation / wl.max_procs
            print('File: {}\nUtil: {}\n'.format(f, norm_util.mean()))
            res.set_value(i, norm_util.mean())
            i = i + 1
        except:
            print('{} do not contains max proc info'.format(f))
        finally:
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
    try:
        ou = pd.Series.from_csv("overall_utilisation.csv")
    except:
        ou = compute_overall_utilisation()
    plot_overall_utilisation(ou)
