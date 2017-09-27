# coding: utf-8

import functools

import matplotlib.dates as mdates
import matplotlib.patches as mpatch
import numpy as np
import pandas as pd

from . import core


class GanttVisualization(core.Visualization):
    def __init__(self, ax, *, title='Gantt chart'):
        super().__init__(ax)
        self.title = title
        self.xscale = None
        self.alpha = 0.4
        self.colorer = self.round_robin_map
        self.labeler = lambda job: str(job['jobID'])
        self._columns = (
            'jobID',
            'allocated_processors',
            'execution_time',
            'finish_time',
            'starting_time',
            'submission_time',
        )

    @staticmethod
    def adapt_uniq_num(df):
        df['uniq_num'] = np.arange(0, len(df))

    @staticmethod
    def adapt_time_xscale(df):
        # interpret columns with time aware semantics
        df['submission_time'] = pd.to_datetime(df['submission_time'], unit='s')
        df['starting_time'] = pd.to_datetime(df['starting_time'], unit='s')
        df['execution_time'] = pd.to_timedelta(df['execution_time'], unit='s')
        df['finish_time'] = df['starting_time'] + df['execution_time']
        # convert columns to use them with matplotlib
        df['starting_time'] = df['starting_time'].map(mdates.date2num)
        df['finish_time'] = df['finish_time'].map(mdates.date2num)
        df['execution_time'] = df['finish_time'] - df['starting_time']

    def adapt(self, df):
        self.adapt_uniq_num(df)
        if self.xscale == 'time':
            self.adapt_time_xscale(df)

    @staticmethod
    def annotate(rect, label):
        rx, ry = rect.get_xy()
        cx, cy = rx + rect.get_width() / 2.0, ry + rect.get_height() / 2.0
        rect.axes.annotate(
            label,
            (cx, cy),
            color='black',
            fontsize='small',
            ha='center',
            va='center'
        )

    @staticmethod
    def round_robin_map(job, palette):
        return palette[job['uniq_num'] % len(palette)]

    def plot_job(self, job):
        x0 = job['starting_time']
        duration = job['execution_time']
        for itv in job['allocated_processors'].intervals():
            height = itv.sup - itv.inf + 1
            rect = mpatch.Rectangle(
                (x0, itv.inf),
                duration,
                height,
                alpha=self.alpha,
                facecolor=functools.partial(self.colorer, palette=self.palette)(job),
                edgecolor='black',
                linewidth=0.5
            )
            self.ax.add_artist(rect)
            self.annotate(rect, self.labeler(job))

    def build(self, jobset):
        # build the visualization
        df = jobset.df.loc[:, self._columns]  # copy just what is needed
        self.adapt(df)
        df.apply(self.plot_job, axis='columns')

        # tweak visualization appearance
        self.ax.set(
            xlim=(df.submission_time.min(), df.finish_time.max()),
            ylim=(jobset.res_bounds.inf - 1, jobset.res_bounds.sup + 2),
        )
        self.ax.grid(True)
        if self.xscale == 'time':
            self.ax.xaxis.set_major_formatter(
                mdates.DateFormatter('%Y-%m-%d\n%H:%M:%S')
            )


class GanttLayout(core.EvalysLayout):
    def __init__(self, *, wtitle='Gantt chart'):
        super().__init__(wtitle=wtitle)
        self.axes['gantt'] = self.fig.add_subplot(1, 1, 1)
        self.visualizations['gantt'] = \
                GanttVisualization(self.axes['gantt'], title=wtitle)


def plot_gantt(jobset, *, title='Gantt chart', **kwargs):
    fig = GanttLayout(wtitle=title)
    gantt = fig.visualizations['gantt']

    for kw in kwargs:
        getattr(gantt, kw)  # check .kw is a valid attribute, if not raise
        setattr(gantt, kw, kwargs[kw])  # .kw is valid, update its value

    gantt.build(jobset)
    fig.show()
