# coding: utf-8

import matplotlib.gridspec

from . import core
from . import gantt
from . import lifecycle
from . import series
from .. import utils


class DetailsLayout(core.EvalysLayout):
    def __init__(self, *, wtitle='Workload overview'):
        super().__init__(wtitle=wtitle)

        gs = matplotlib.gridspec.GridSpec(nrows=4, ncols=1)

        self.axes['gantt'] = self.fig.add_subplot(gs[3, :])
        self.axes['lifecycle'] = \
                self.fig.add_subplot(gs[2, :], sharex=self.axes['gantt'])
        self.axes['queue'] = \
                self.fig.add_subplot(gs[1, :], sharex=self.axes['gantt'])
        self.axes['utilization'] = \
                self.fig.add_subplot(gs[0, :], sharex=self.axes['gantt'])


def plot_details(jobset, *, title='Workload overview', **kwargs):
    visualizations = {
        'gantt': gantt.GanttVisualization,
        'lifecycle': lifecycle.LifecycleVisualization,
        'queue': series.QueueSeriesVisualization,
        'utilization': series.UtilizationSeriesVisualization,
    }

    layout = DetailsLayout(wtitle=title)
    for axkey, visu_cls in visualizations.items():
        plot = layout.inject(visu_cls, axkey=axkey)
        utils.bulksetattr(plot, **kwargs)
        plot.build(jobset)
    layout.show()
