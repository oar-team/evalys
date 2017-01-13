'''
    Interactively explore the difference between two schedules of the same trace.

Usage:
    compare_2_scheduling.py <swf_file1> <swf_file2> [-h]

Options:
    -h --help      show this help message and exit.
'''
import matplotlib
matplotlib.use('Qt5Agg')

from matplotlib import pyplot as plt
from evalys import visu
from evalys import workload
from docopt import docopt
#retrieving arguments
arguments = docopt(__doc__, version='1.0.0rc2')


fig, axes = plt.subplots(nrows=5, ncols=1, sharex=True)

w = workload.Workload.from_csv(arguments["<swf_file1>"])
w0 = workload.Workload.from_csv(arguments["<swf_file2>"])

visu.plot_series_comparison({arguments["<swf_file1>"]: w.utilisation.load,
                             arguments["<swf_file2>"]: w0.utilisation.load},
                            axes[0],
                            "Utilisation comparison")

visu.plot_series_comparison({arguments["<swf_file1>"]: w.queue.load,
                             arguments["<swf_file2>"]: w0.queue.load},
                            axes[1],
                            "Queue comparison")

visu.plot_job_details(w.df, 100, axes[2], arguments["<swf_file1>"])

visu.plot_job_details(w0.df, 100, axes[3], arguments["<swf_file2>"])

visu.plot_series("waiting_time", {arguments["<swf_file1>"]: w, arguments["<swf_file2>"]: w0}, axes[4])

plt.tight_layout(True)
plt.legend()
plt.show()
