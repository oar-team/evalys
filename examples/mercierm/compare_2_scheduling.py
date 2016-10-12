from matplotlib import pyplot as plt
from evalys import visu
from evalys import workload


fig, axes = plt.subplots(nrows=5, ncols=1, sharex=True)


w = workload.Workload.from_csv(
    "./tests/easy_mediumWL_smallPF.swf")

w0 = workload.Workload.from_csv(
    "./tests/filler_mediumWL_smallPF.swf")

visu.plot_series_comparison({"random": w.utilisation,
                             "wait": w0.utilisation},
                            axes[0],
                            "Utilisation comparison")

visu.plot_series_comparison({"random": w.queue,
                             "wait": w0.queue},
                            axes[1],
                            "Queue comparison")

visu.plot_job_details(w.df, 100, axes[2], "random")

visu.plot_job_details(w0.df, 100, axes[3], "wait")

visu.plot_series("waiting_time", {"random": w, "wait": w0}, axes[4])

plt.tight_layout(True)
plt.legend()
plt.show()
