# coding: utf-8

import functools

import matplotlib.dates
import matplotlib.patches
import numpy
import pandas

from . import core
from .. import utils


class GanttVisualization(core.Visualization):
    """
    Visualization of a jobset as a Gantt chart.

    The `GanttVisualization` class displays a jobset as a Gantt chart.  Each
    job in the jobset is represented as a set of rectangle.
    The x-axis represents time, while the y-axis represents resources.

    :cvar COLUMNS: The columns required to build the visualization.

    :ivar _lspec: The specification of the layout for the visualization.
    :vartype _lspec: `core._LayoutSpec`

    :ivar _ax: The `Axe` to draw on.

    :ivar palette: The palette of colors to be used.

    :ivar xscale:
        The requested adaptation of the x-axis scale.
        Valid values are `None`, and `'time'`.
        - It defaults to `None`, and uses raw values by default.
        - If set to `time`, the x-axis interprets the data as timestamps, and
          uses a time-aware semantic.

    :ivar alpha:
        The transparency level of the rectangles depicting jobs.  It defaults
        to `0.4`.
    :vartype alpha: float

    :ivar colorer:
        The strategy to assign a color to a job.  By default, the colors of the
        palette are picked with a round-robin strategy.
        The colorer is a function expecting two positional parameters: first
        the `job`, and second the `palette`.
        See `GanttVisualization.round_robin_map` for an example.

    :ivar labeler:
        The strategy to label jobs.  By default, the `jobID` column is used to
        label jobs.
        To disable the labeling of jobs, simply return an empty string.
    """

    COLUMNS = ('jobID', 'allocated_resources', 'execution_time',
               'finish_time', 'starting_time', 'submission_time', )

    def __init__(self, lspec, *, title='Gantt chart'):
        super().__init__(lspec)
        self.title = title
        self.xscale = None
        self.alpha = 0.4
        self.colorer = self.round_robin_map
        self.labeler = lambda job: str(job['jobID'])
        self._columns = self.COLUMNS

    def _customize_layout(self):
        self._ax.grid(True)

        # adapt scale of axes if requested
        if self.xscale == 'time':
            self._ax.xaxis.set_major_formatter(
                matplotlib.dates.DateFormatter('%Y-%m-%d\n%H:%M:%S')
            )

    @staticmethod
    def _adapt_uniq_num(df):
        df['uniq_num'] = numpy.arange(0, len(df))

    @staticmethod
    def _adapt_time_xscale(df):
        # interpret columns with time aware semantics
        df['submission_time'] = pandas.to_datetime(df['submission_time'], unit='s')
        df['starting_time'] = pandas.to_datetime(df['starting_time'], unit='s')
        df['execution_time'] = pandas.to_timedelta(df['execution_time'], unit='s')
        df['finish_time'] = df['starting_time'] + df['execution_time']
        # convert columns to use them with matplotlib
        df['submission_time'] = df['submission_time'].map(matplotlib.dates.date2num)
        df['starting_time'] = df['starting_time'].map(matplotlib.dates.date2num)
        df['finish_time'] = df['finish_time'].map(matplotlib.dates.date2num)
        df['execution_time'] = df['finish_time'] - df['starting_time']

    def _adapt(self, df):
        self._adapt_uniq_num(df)
        if self.xscale == 'time':
            self._adapt_time_xscale(df)

    @staticmethod
    def _annotate(rect, label):
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

    def _draw(self, df):
        def _plot_job(job):
            x0 = job['starting_time']
            duration = job['execution_time']
            for itv in job['allocated_resources'].intervals():
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
                self._ax.add_artist(rect)
                self._annotate(rect, self.labeler(job))
        #
        df.apply(_plot_job, axis='columns')

    def build(self, jobset):
        df = jobset.df.loc[:, self._columns]  # copy just what is needed
        self._adapt(df)  # extract the data required for the visualization
        self._customize_layout()  # prepare the layout for displaying the data
        self._draw(df)  # do the painting job

        # tweak boundaries to match the studied jobset
        self._ax.set(
            xlim=(df.submission_time.min(), df.finish_time.max()),
            ylim=(jobset.res_bounds.inf - 1, jobset.res_bounds.sup + 2),
        )



class DiffGanttVisualization(GanttVisualization):
    def __init__(self, lspec, *, title='Gantt charts comparison'):
        super().__init__(lspec, title=title)
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
                xmin, xmax = self._ax.get_xlim()
                gxmin, gxmax = min(xmin, gxmin), max(xmax, gxmax)
                self._ax.set_xlim(gxmin, gxmax)
            else:
                # first GanttVisualization, save xlim as is
                gxmin, gxmax = self._ax.get_xlim()

            # create a proxy object for the legend
            captions.append(
                matplotlib.patches.Patch(color=color, alpha=self.alpha, label=js_name)
            )

        # add legend to the visualization
        self._ax.legend(handles=captions, loc='best')

        self.palette = _orig_palette  # restore original palette


def plot_gantt(jobset, *, title='Gantt chart', **kwargs):
    """
    Helper function to create a Gantt chart of a workload.

    :param jobset: The jobset under study.
    :type jobset: `JobSet`

    :param title: The title of the window.
    :type title: str

    :param **kwargs:
        The keyword arguments to be fed to the constructor of the visualization
        class.
    """
    layout = core.SimpleLayout(wtitle=title)
    plot = layout.inject(GanttVisualization, spskey='all', title=title)
    utils.bulksetattr(plot, **kwargs)
    plot.build(jobset)
    layout.show()


def plot_diff_gantt(jobsets, *, title='Gantt charts comparison', **kwargs):
    """
    Helper function to create a comparison of Gantt charts of two (or more)
    workloads.

    :param jobsets: The jobsets under study.
    :type jobset: list(JobSet)

    :param title: The title of the window.
    :type title: str

    :param **kwargs:
        The keyword arguments to be fed to the constructor of the visualization
        class.
    """
    layout = core.SimpleLayout(wtitle=title)
    plot = layout.inject(DiffGanttVisualization, spskey='all', title=title)
    utils.bulksetattr(plot, **kwargs)
    plot.build(jobsets)
    layout.show()
