# coding: utf-8

from evalys.jobset import JobSet
from evalys.visu import plot_gantt

js = JobSet('jobs.csv')
print(js.df.describe())

plot_gantt(js)
