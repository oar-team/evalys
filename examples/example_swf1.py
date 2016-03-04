# coding: utf-8
# %matplotlib
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from evalys.workload import Workload

matplotlib.style.use('ggplot')

wkd = Workload(file='UniLu-Gaia-2014-2.swf')
df = wkd.df
print(df.describe())

nb_distinct_req_proc_time = len(df.groupby(['Req Nb Proc', 'Req Time']))
nb_job_by_req_proc_time = df[['Req Nb Proc', 'Req Time','Job']].groupby(['Req Nb Proc', 'Req Time']).agg(['count'])
wkd.df.hist()

fig = plt.figure()
ax = fig.add_subplot(2, 1, 1)
ax.set_xscale('log')
ax1 = df.hist(bins=np.logspace(1, 4.5, 100), normed=True, column='runtime', sharex=True, sharey=True, ax=ax)
df.hist(bins=np.logspace(1, 4.5, 100), normed=True, cumulative=True, column='runtime', sharex=True, sharey=True, ax=ax1, histtype='step')
