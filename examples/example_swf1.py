# coding: utf-8
# %matplotlib
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from evalys.workload import Workload

matplotlib.style.use('ggplot')

wkd = Workload.from_csv('UniLu-Gaia-2014-2.swf')
df = wkd.df
print(df.describe())

nb_distinct_req_proc_time = len(df.groupby(['proc_req', 'user_est']))
nb_job_by_req_proc_time = df[['proc_req', 'user_est','jobID']].groupby(['proc_req', 'user_est']).agg(['count'])
wkd.df.hist()

fig = plt.figure()
ax = fig.add_subplot(2, 1, 1)
ax.set_xscale('log')
ax1 = df.hist(bins=np.logspace(1, 4.5, 100), normed=True, column='execution_time', sharex=True, sharey=True, ax=ax)
df.hist(bins=np.logspace(1, 4.5, 100), normed=True, cumulative=True, column='execution_time', sharex=True, sharey=True, ax=ax1, histtype='step')

plt.show()
