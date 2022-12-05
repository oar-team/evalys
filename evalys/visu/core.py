# coding: utf-8

import collections

import matplotlib.pyplot
import numpy


def generate_palette(size):
    """
    Return of discrete palette with the specified number of different colors.
    """
    return list(matplotlib.pyplot.cm.viridis(numpy.linspace(0, 1, size)))


# pylint: disable=bad-whitespace
COLORBLIND_FRIENDLY_PALETTE = (
    # http://jfly.iam.u-tokyo.ac.jp/color/#pallet
    '#999999',        # grey
    ( .9,  .6,   0),  # orange
    (.35,  .7,  .9),  # sky blue
    (  0,  .6,  .5),  # bluish green
    (.95,  .9, .25),  # yellow
    (  0, .45,  .7),  # blue
    ( .8,  .4,   0),  # vermillion
    ( .8,  .6,  .7),  # reddish purple
)
# pylint: enable=bad-whitespace


_LayoutSpec = collections.namedtuple('_LayoutSpec', ('fig', 'spec'))
_LayoutSpec.__doc__ += ': Helper object to share the layout specifications'
_LayoutSpec.fig.__doc__ = 'Figure to be used by the visualization'
_LayoutSpec.spec.__doc__ = 'Root `SubplotSpec` for the visualization'


class EvalysLayout:
    """
    Base layout to organize visualizations.

    :ivar fig: The actual figure to draw on.

    :ivar sps: The `SubplotSpec` defined in the layout.
    :vartype axes: dict

    :ivar visualizations: Binding of the visualizations injected into the layout.
        For each key `spskey` in `self.sps`, `self.visualizations[spskey]` is a
        list of the visualizations with root `SubplotSpec` `self.sps[spskey]`.
    :vartype visualizations: dict
    """

    def __init__(self, *, wtitle='Evalys Figure'):
        self.fig = matplotlib.pyplot.figure()
        self.sps = {}
        self.visualizations = {}
        self.wtitle = wtitle

    def show(self):
        """
        Display the figure window.
        """
        self.fig.show()

    def inject(self, visu_cls, spskey, *args, **kwargs):
        """
        Create a visualization, and bind it to the layout.

        :param visu_cls:
            The class of the visualization to create.  This should be
            `Visualization` or one of its subclass.

        :param spskey:
            The key identifying the `SubplotSpec` fed to the injected
            `Visualization` (or a subclass).  This key must exist in
            `self.sps`.

        :param \*args:
            The positional arguments to be fed to the constructor of the
            visualization class.

        :param \**kwargs:
            The keyword arguments to be fed to the constructor of the
            visualization class.

        :returns: The newly created visualization.
        :rtype: visu_cls
        """
        lspec = _LayoutSpec(fig=self.fig, spec=self.sps[spskey])
        new_visu = visu_cls(lspec, *args, **kwargs)
        self.visualizations.setdefault(spskey, []).append(new_visu)
        return new_visu

    @property
    def wtitle(self):
        """
        The title of the window containing the layout.
        """
        return self.fig.canvas.manager.get_window_title()

    @wtitle.setter
    def wtitle(self, wtitle):
        self.fig.canvas.manager.set_window_title(wtitle)


class SimpleLayout(EvalysLayout):
    """
    Simplest possible layout that uses all available space.
    """

    def __init__(self, *, wtitle='Simple Figure'):
        super().__init__(wtitle=wtitle)
        self.sps['all'] = matplotlib.gridspec.GridSpec(nrows=1, ncols=1)[0]


class Visualization:
    """
    Base class to define visualizations.

    :ivar _lspec: The specification of the layout for the visualization.
    :vartype _lspec: _LayoutSpec

    :ivar _ax: The `Axe` to draw on.

    :ivar palette: The palette of colors to be used.
    """

    def __init__(self, lspec):
        self._lspec = lspec
        self._ax = None
        self._set_axes()

        self.palette = generate_palette(8)

    def _set_axes(self):
        """
        Given the `_LayoutSpec` in `self._lspec`, populate `self._ax`.

        Note that `self._ax` is set to use all the available space given by
        `self._lspec`.
        """
        gs = matplotlib.gridspec.GridSpecFromSubplotSpec(
            nrows=1, ncols=1, subplot_spec=self._lspec.spec
        )
        self._ax = self._lspec.fig.add_subplot(gs[0])

    def build(self, jobset):
        """
        Extract meaningful data from `jobset`, and create the plot.
        """
        raise NotImplementedError()

    @property
    def title(self):
        """
        Title of the visualization.
        """
        return self._ax.get_title()

    @title.setter
    def title(self, title):
        self._ax.set_title(title)
