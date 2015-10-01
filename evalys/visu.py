# coding: utf-8
from __future__ import unicode_literals, print_function

import pandas as pd
# import numpy as np

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatch

import colorsys

pd.set_option('display.mpl_style', 'default')  # Make the graphs a bit prettier
# figsize(15, 5)


NB_COLORS = 15
HSV_tuples = [(x * 1.0 / NB_COLORS, 0.5, 0.5) for x in range(NB_COLORS)]
RGB_tuples = list(map(lambda x: colorsys.hsv_to_rgb(*x), HSV_tuples))


def annotate(ax, rect, annot):
    rx, ry = rect.get_xy()
    cx = rx + rect.get_width() / 2.0
    cy = ry + rect.get_height() / 2.0

    ax.annotate(annot, (cx, cy), color='black',
                fontsize=12, ha='center', va='center')


def plot_gantt(jobset):
    fig, ax = plt.subplots()
    for i, job in jobset.df.iterrows():
        col = RGB_tuples[job.jobID % len(RGB_tuples)]
        duration = job['execution_time']
        for i, itv in enumerate(jobset.res_set[job['jobID']]):
            (y0, y1) = itv
            rect = mpatch.Rectangle((job['starting_time'], y0 - 0.4), duration,
                                    y1 - y0 + 0.8, alpha=0.2, color=col)
            if (i == 0):
                annotate(ax, rect, 'j' + str(job['jobID']))
            ax.add_artist(rect)

    ax.set_xlim((0, jobset.df.finish_time.max()))
    ax.set_ylim((0, jobset.nb_max_res))
    #    ax.set_aspect('equal')
    ax.grid(True)
    mng = plt.get_current_fig_manager()
    try:
        mng.resize(*mng.window.maxsize())
        #mng.window.showMaximized()
    except:
        pass
    plt.show()
