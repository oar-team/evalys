# coding: utf-8

from . import core
from . import legacy
from .. import utils


class LifecycleVisualization(core.Visualization):
    def __init__(self, ax, *, title='Jobs\' lifecycle'):
        super().__init__(ax)
        self.title = title
        self.xscale = None

    def build(self, jobset):
        legacy.plot_job_details(
            dataframe=jobset.df,
            size=jobset.MaxProcs,
            ax=self.ax,
            title=self.title,
            time_scale=(self.xscale == 'time')
        )


def plot_lifecycle(jobset, *, title='Jobs\' life cycle', **kwargs):
    layout = core.SimpleLayout(wtitle=title)
    plot = layout.inject(LifecycleVisualization, axkey='all')
    utils.bulksetattr(plot, **kwargs)
    plot.build(jobset)
    layout.show()
