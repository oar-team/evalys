# coding: utf-8

from matplotlib import pyplot
import numpy


def generate_palette(size):
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
    def __init__(self, *, wtitle='Evalys Figure'):
        self.fig = pyplot.figure()
        self.axes = {}
        self.visualizations = {}
        self.wtitle = wtitle

    def show(self):
        self.fig.show()

    def register(self, visu_cls, axkey, *args, **kwargs):
        # Add a new visualization to the layout.
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


class Visualization:
    def __init__(self, ax):
        self.ax = ax
        self.palette = generate_palette(8)

    @property
    def title(self):
        return self.ax.get_title()

    @title.setter
    def title(self, title):
        self.ax.set_title(title)
