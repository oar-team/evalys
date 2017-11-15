# coding: utf-8

from matplotlib import pyplot
import numpy


def generate_palette(size):
    """
    Return of discrete palette with the specified number of different colors.
    """
    return list(pyplot.cm.viridis(numpy.linspace(0, 1, size)))


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


class EvalysLayout:
    """
    Base layout to organize visualizations.

    :ivar fig: The actual figure to draw on.

    :ivar axes: The available Axes in the layout.
    :vartype axes: dict

    :ivar visualizations:
        Binding of the visualizations using the layout. For each key `axkey` in
        `self.axes`, `self.visualizations[axkey]` is a list of the
        visualizations targeting `self.axes[axkey]`.
    :vartype visualizations: dict

    :ivar wtitle: The title of the window containing the layout.
    :vartype wtitle: str

    """

    def __init__(self, *, wtitle='Evalys Figure'):
        self.fig = pyplot.figure()
        self.axes = {}
        self.visualizations = {}
        self.wtitle = wtitle

    def show(self):
        """
        Display the figure window.
        """
        self.fig.show()

    def inject(self, visu_cls, axkey, *args, **kwargs):
        """
        Create a visualization, and bind it to the layout.

        :param visu_cls:
            The class of the visualization to create. This should be a
            Visualization or one of its subclass.

        :param axkey:
            The key identifying the axis the Visualization is using. This key
            must exist in self.axes.

        :param *args:
            The positional arguments to be fed to the constructor of the
            visualization class.

        :param **kwargs:
            The keyword arguments to be fed to the constructor of the
            visualization class.

        :returns: The newly created visualization.
        :rtype: visu_cls

        """
        ax = self.axes[axkey]
        new_visu = visu_cls(ax, *args, **kwargs)
        self.visualizations.setdefault(axkey, []).append(new_visu)
        return new_visu

    @property
    def wtitle(self):
        return self.fig.canvas.get_window_title()

    @wtitle.setter
    def wtitle(self, wtitle):
        self.fig.canvas.set_window_title(wtitle)


class SimpleLayout(EvalysLayout):
    """
    Simplest possible layout with a single Axe using all available space.
    """

    def __init__(self, *, wtitle='Simple Figure'):
        super().__init__(wtitle=wtitle)
        self.axes['all'] = self.fig.add_subplot(1, 1, 1)


class Visualization:
    """
    Base class to define visualizations.

    :ivar ax: The Axe to draw on.

    :ivar palette: The palette of colors to be used.

    :ivar title: The title of the visualization.
    :vartype title: str
    """

    def __init__(self, ax):
        self.ax = ax
        self.palette = generate_palette(8)

    @property
    def title(self):
        return self.ax.get_title()

    @title.setter
    def title(self, title):
        self.ax.set_title(title)
