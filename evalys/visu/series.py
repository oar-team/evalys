# coding: utf-8

from . import core
from . import legacy
from .. import utils


class SeriesVisualization(core.Visualization):
    _metric = None
    available_series = {}

    @classmethod
    def factory(cls, name):
        try:
            return cls.available_series[name]
        except KeyError:
            raise KeyError('Unknown series: {}'.format(name))

    def __init__(self, ax, *, title='Time Series plot'):
        super().__init__(ax)
        self.title = title
        self.xscale = None

    def build(self, jobset):
        legacy.plot_load(
            load=getattr(jobset, self._metric),
            nb_resources=jobset.MaxProcs,
            ax=self.ax,
            time_scale=(self.xscale == 'time'),
            load_label=self.title
        )


def register(*, name, column=None):
    def wrapper(cls):
        if not issubclass(cls, SeriesVisualization):
            raise TypeError(
                'Unable to register a class that does not derive from SeriesVisualization'
            )
        if name in cls.available_series:
            raise KeyError('Name collision with {}'.format(name))
        cls._metric = column or name  # defaults to name
        cls.available_series[name] = cls
        return cls
    return wrapper


@register(name='queue')
class QueueSeriesVisualization(SeriesVisualization):
    def __init__(self, ax, *, title='Queue size'):
        super().__init__(ax, title=title)


@register(name='utilization', column='utilisation')  # nasty misspell in original source code
class UtilizationSeriesVisualization(SeriesVisualization):
    def __init__(self, ax, *, title='Resources\' utilization'):
        super().__init__(ax, title=title)


def plot_series(jobset, *, name, title='Time series plot', **kwargs):
    layout = core.SimpleLayout(wtitle=title)
    plot = layout.inject(SeriesVisualization.factory(name), axkey='all')
    utils.bulksetattr(plot, **kwargs)
    plot.build(jobset)
    layout.show()
