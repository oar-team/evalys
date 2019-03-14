# coding: utf-8

from . import core
from . import legacy  # TODO: remove dependency to legacy code
from .. import utils


class SeriesVisualization(core.Visualization):
    """
    Base class to visualize series.

    :cvar _metric: The metric to visualize.

    :cvar available_series:
        Mapping of all the knowns series' visualization classes.  This dict is
        meant to be used through the factory class method.

    :ivar _lspec: The specification of the layout for the visualization.
    :vartype _lspec: _LayoutSpec

    :ivar _ax: The `Axe` to draw on.

    :ivar palette: The palette of colors to be used.

    :ivar xscale:
        The requested adaptation of the x-axis scale.
        Valid values are `None`, and `'time'`.

        * It defaults to `None`, and uses raw values by default.
        * If set to `time`, the x-axis interprets the data as timestamps, and
          uses a time-aware semantic.
    """
    _metric = None
    available_series = {}

    @classmethod
    def factory(cls, name):
        """
        Access visualizations of series by name.

        The available visualizations have to be registered with the class
        decorator `register`.

        :param name: Name of the requested visualization.
        :type: str

        :returns:
            The actual `SeriesVisualization` subclass registered as `name`.
        """
        try:
            return cls.available_series[name]
        except KeyError:
            raise KeyError('Unknown series: {}'.format(name))

    def __init__(self, lspec, *, title='Time Series plot'):
        super().__init__(lspec)
        self.title = title
        self.xscale = None

    def build(self, jobset):
        # TODO: remove dependency to legacy code
        # XXX: palette is not injected properly
        # XXX: we are missing the normalize parameter
        legacy.plot_load(
            load=getattr(jobset, self._metric),
            nb_resources=jobset.MaxProcs,
            ax=self._ax,
            time_scale=(self.xscale == 'time')
        )


def register(*, name, column=None):
    """
    Register a series visualization.

    Available series visualization must inherit from SeriesVisualization, and
    are registered with this class decorator.

    :param name:
        The name under which the visualization is registered in
        `SeriesVisualization`.  This name is to be used with the factory class
        method of `SeriesVisualization`.
    :type: str

    :param column:
        The actual column name that is used for the series.  It defaults to
        `name`.
    """
    def _wrapper(cls):
        if not issubclass(cls, SeriesVisualization):
            raise TypeError(
                'Unable to register a class that does not derive from SeriesVisualization'
            )
        if name in cls.available_series:
            raise KeyError('Name collision with {}'.format(name))
        cls._metric = column or name  # defaults to name
        cls.available_series[name] = cls
        return cls
    return _wrapper


@register(name='queue')
class QueueSeriesVisualization(SeriesVisualization):
    """
    Visualization of the size of the queue with respect to time.
    """
    def __init__(self, lspec, *, title='Queue size'):
        super().__init__(lspec, title=title)


@register(name='utilization', column='utilisation')  # nasty misspell in original source code
class UtilizationSeriesVisualization(SeriesVisualization):
    """
    Visualization of the resources' utilization with respect to time.
    """
    def __init__(self, lspec, *, title='Resources\' utilization'):
        super().__init__(lspec, title=title)


def plot_series(jobset, *, name, title='Time series plot', **kwargs):
    """
    Helper function to create a series visualization of a workload.

    :param jobset: The jobset under study.
    :type jobset: `JobSet`

    :param name: Name of the requested series visualization.
    :type: `str`

    :param title: The title of the window.
    :type title: `str`

    :param \**kwargs:
        The keyword arguments to be fed to the constructor of the visualization
        class.
    """
    layout = core.SimpleLayout(wtitle=title)
    plot = layout.inject(SeriesVisualization.factory(name), spskey='all', title=title)
    utils.bulksetattr(plot, **kwargs)
    plot.build(jobset)
    plot._ax.set_title(title)
    layout.show()
