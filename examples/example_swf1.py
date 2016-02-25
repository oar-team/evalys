# coding: utf-8
import matplotlib
from evalys.workload import Workload

# matplotlib.use('WX')

wkd = Workload(file='UniLu-Gaia-2014-2.swf')
df = wkd.df 
print(df.describe())

nb_distinct_req_proc_time = len(df.groupby(['Req Nb Proc', 'Req Time']))
nb_job_by_req_proc_time = df[['Req Nb Proc', 'Req Time','Job']].groupby(['Req Nb Proc', 'Req Time']).agg(['count'])
wkd.df.hist()

