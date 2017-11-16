# coding: utf-8

import functools

import matplotlib.dates
import matplotlib.patches
import numpy
import pandas

from . import core
from .. import utils


class GanttVisualization(core.Visualization):

    COLUMNS = ('jobID', 'allocated_processors', 'execution_time',
               'finish_time', 'starting_time', 'submission_time')

    def __init__(self, ax, *, title='Gantt chart'):
        super().__init__(ax)
        self.title = title
        self.xscale = None
        self.alpha = 0.4
        self.colorer = self.round_robin_map
        self.labeler = lambda job: str(job['jobID'])
        self._columns = type(self).COLUMNS

    @staticmethod
    def adapt_uniq_num(df):
        df['uniq_num'] = numpy.arange(0, len(df))

    @staticmethod
    def adapt_time_xscale(df):
        # interpret columns with time aware semantics
        df['submission_time'] = pandas.to_datetime(df['submission_time'], unit='s')
        df['starting_time'] = pandas.to_datetime(df['starting_time'], unit='s')
        df['execution_time'] = pandas.to_timedelta(df['execution_time'], unit='s')
        df['finish_time'] = df['starting_time'] + df['execution_time']
        # convert columns to use them with matplotlib
        df['starting_time'] = df['starting_time'].map(matplotlib.dates.date2num)
        df['finish_time'] = df['finish_time'].map(matplotlib.dates.date2num)
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
            rect = matplotlib.patches.Rectangle(
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
                matplotlib.dates.DateFormatter('%Y-%m-%d\n%H:%M:%S')
            )


class DiffGanttVisualization(GanttVisualization):
    def __init__(self, ax, *, title='Gantt chart'):
        super().__init__(ax, title=title)
        self.alpha = 0.5
        self.colorer = lambda _, palette: palette[0]  # single color per jobset
        self.labeler = lambda _: ''  # do not label jobs
        self.palette = None  # let .build(…) figure the number of colors

    def build(self, jobsets):
        _orig_palette = self.palette  # save original palette

        # create an adapted palette if none has been provided
        palette = self.palette or core.generate_palette(len(jobsets))

        gxmin, gxmax = None, None  # global xlim
        captions = []  # list of proxy objects for the legend

        for idx, (js_name, js_obj) in enumerate(jobsets.items()):
            # create a palette made of a single color for current jobset
            color = palette[idx]
            self.palette = [color]

            # build as a GanttVisualization for current jobset
            super().build(js_obj)

            # tweak visualization appearance
            if idx:
                # recompute xlim with respect to previous GanttVisualization
                xmin, xmax = self.ax.get_xlim()
                gxmin, gxmax = min(xmin, gxmin), max(xmax, gxmax)
                self.ax.set_xlim(gxmin, gxmax)
            else:
                # first GanttVisualization, save xlim as is
                gxmin, gxmax = self.ax.get_xlim()

            # create a proxy object for the legend
            captions.append(
                matplotlib.patches.Patch(color=color, alpha=self.alpha, label=js_name)
            )

        # add legend to the visualization
        self.ax.legend(handles=captions, loc='best')

        self.palette = _orig_palette  # restore original palette


def plot_gantt(jobset, *, title='Gantt chart', **kwargs):
    layout = core.SimpleLayout(wtitle=title)
    plot = layout.inject(GanttVisualization, axkey='all', title=title)
    utils.bulksetattr(plot, **kwargs)
    plot.build(jobset)
    layout.show()


def plot_diff_gantt(jobsets, *, title='Gantt charts comparison', **kwargs):
    layout = core.SimpleLayout(wtitle=title)
    plot = layout.inject(DiffGanttVisualization, axkey='all', title=title)
    utils.bulksetattr(plot, **kwargs)
    plot.build(jobsets)
    layout.show()
