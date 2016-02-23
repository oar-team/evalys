# coding: utf-8
import matplotlib
from evalys.jobset import JobSet

#matplotlib.use('WX')

js = JobSet('jobs.csv')
print(js.df.describe())

js.df.hist()
#js.gantt()
