# coding: utf-8
from evalys.jobset import JobSet

js = JobSet('jobs.csv')
print(js.df.describe())

js.df.hist()
js.gantt()
