# coding: utf-8

from matplotlib import pyplot as plt
import numpy as np


def generate_palette(size):
    return list(plt.cm.viridis(np.linspace(0, 1, size)))


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
