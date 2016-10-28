# coding: utf-8
import matplotlib.pyplot as plt
from evalys.jobset import JobSet

#matplotlib.use('WX')

js = JobSet.from_csv('jobs.csv')
print(js.df.describe())

js.df.hist()

fig, axe = plt.subplots()
js.gantt(axe, "test")
plt.show()
