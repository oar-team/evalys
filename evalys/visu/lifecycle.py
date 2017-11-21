# coding: utf-8

import matplotlib.gridspec
import matplotlib.lines
import matplotlib.patches
import matplotlib.pyplot
import pandas

from . import core
from .. import utils


class LifecycleVisualization(core.Visualization):

    COLUMNS = ('allocated_processors', 'finish_time', 'starting_time',
               'submission_time', )

    _events = ('submit', 'start', 'finish')

    _ev2col = {  # mapping to the actual column
        'submit': 'submission_time',
        'start': 'starting_time',
        'finish': 'finish_time',
    }

    def __init__(self, lspec, *, title='Jobs\' lifecycle'):
        super().__init__(lspec)
        self.title = title
        self.palette = ('blue', 'green', 'red')
        self.markers = ('.', '>', '|')
        self.markersizes = (10, 8, 15)
        self.alpha = 0.5
        self.xscale = None
        self.yscale = None
        self._columns = self.COLUMNS

    def _set_axes(self):
        gs = matplotlib.gridspec.GridSpecFromSubplotSpec(
            nrows=3, ncols=1, hspace=0.0,
            subplot_spec=self._lspec.spec
        )

        self._ax = {}
        self._ax['submit'] = self._lspec.fig.add_subplot(gs[2, :])
        self._ax['start'] = self._lspec.fig.add_subplot(
            gs[1, :], sharex=self._ax['submit'], sharey=self._ax['submit']
        )
        self._ax['finish'] = self._lspec.fig.add_subplot(
            gs[0, :], sharex=self._ax['submit'], sharey=self._ax['submit']
        )

    def _customize_layout(self):
        # hide ticks/labels except for bottom-most axis
        for event in self._events[1:]:
            self._ax[event].xaxis.set_tick_params(
                tick1On=False, tick2On=False,  # remove ticks
                label1On=False, label2On=False  # remove labels
            )
            self._ax[event].xaxis.offsetText.set(visible=False)  # why‽

        for subax in self._ax.values():
            subax.grid(True)

        # adapt scale of axes if requested
        if self.xscale == 'time':
            self._ax['submit'].xaxis.set_major_formatter(
                matplotlib.dates.DateFormatter('%Y-%m-%d\n%H:%M:%S')
            )
        if self.yscale == 'log2':
            self._ax['submit'].set_yscale('log', basey=2)

        # set caption in the top-most stripe
        captions = [
            matplotlib.lines.Line2D(
                [], [],
                color=self.palette[idx],
                marker=self.markers[idx],
                linestyle='none',
                label=event
            )
            for idx, event in enumerate(self._events)
        ]
        self._ax['finish'].legend(handles=captions, loc='best')


    @property
    def title(self):
        return self._ax['finish'].get_title()  # finish is the top-most stripe

    @title.setter
    def title(self, title):
        self._ax['finish'].set_title(title)  # finish is the top-most stripe

    @staticmethod
    def _adapt_jobsize(df):
        df['jobsize'] = df['allocated_processors'].map(len)

    def _adapt_time_xscale(self, df):
        for column in self._ev2col.values():
            # interpret column with time aware semantics
            df[column] = pandas.to_datetime(df[column], unit='s')
            # convert column to use it with matplotlib
            df[column] = df[column].map(matplotlib.dates.date2num)

    def _adapt(self, df):
        self._adapt_jobsize(df)
        if self.xscale == 'time':
            self._adapt_time_xscale(df)

    def _draw(self, df):
        # plot each event with respect to job size
        for idx, event in enumerate(self._events):
            self._ax[event].plot(
                df[self._ev2col[event]], df['jobsize'],
                linestyle='none', alpha=self.alpha, color=self.palette[idx],
                marker=self.markers[idx], markersize=self.markersizes[idx]
            )

        # link events related to the same job
        def _link_events(job):
            xy = {
                event: (job[self._ev2col[event]], job['jobsize'])
                for event in self._events
            }
            links = ('submit', 'start'), ('start', 'finish')
            for idx, (orig, dest) in enumerate(links):
                link = matplotlib.patches.ConnectionPatch(
                    xyA=xy[dest], xyB=xy[orig],
                    axesA=self._ax[dest], axesB=self._ax[orig],
                    coordsA='data', coordsB='data',
                    alpha=0.4*self.alpha, color=self.palette[idx], linestyle='-'
                )
                self._ax[dest].add_artist(link)
        #
        df.apply(_link_events, axis='columns')

    def build(self, jobset):
        df = jobset.df.loc[:, self._columns]  # copy just what is needed
        self._adapt(df)  # extract the data required for the visualization
        self._customize_layout()  # prepare the layout for displaying the data
        self._draw(df)  # do the painting job


def plot_lifecycle(jobset, *, title='Jobs\' life cycle', **kwargs):
    layout = core.SimpleLayout(wtitle=title)
    plot = layout.inject(LifecycleVisualization, spskey='all', title=title)
    utils.bulksetattr(plot, **kwargs)
    plot.build(jobset)
    layout.show()
