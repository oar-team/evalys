# coding: utf-8
from __future__ import unicode_literals, print_function

import matplotlib
import matplotlib.patches as mpatch
from matplotlib import pyplot as plt

import colorsys

plt.style.use('ggplot')

matplotlib.rcParams['figure.figsize'] = (12.0, 8.0)

NB_COLORS = 16
HSV_tuples = [(x * 1.0 / NB_COLORS, 1, 0.7) for x in range(NB_COLORS)]
RGB_tuples = list(map(lambda x: colorsys.hsv_to_rgb(*x), HSV_tuples))


def annotate(ax, rect, annot):
    rx, ry = rect.get_xy()
    cx = rx + rect.get_width() / 2.0
    cy = ry + rect.get_height() / 2.0

    ax.annotate(annot, (cx, cy), color='black',
                fontsize='small', ha='center', va='center')


def plot_gantt(jobset, ax, title):
    for i, job in jobset.df.iterrows():
        col = RGB_tuples[job.jobID % len(RGB_tuples)]
        duration = job['execution_time']
        for i, itv in enumerate(jobset.res_set[job['jobID']]):
            (y0, y1) = itv
            rect = mpatch.Rectangle((job['starting_time'], y0), duration,
                                    y1 - y0 + 0.9, alpha=0.2, color=col)
            annotate(ax, rect, str(job['jobID']))
            ax.add_artist(rect)

    ax.set_xlim((jobset.df.submission_time.min(), jobset.df.finish_time.max()))
    ax.set_ylim(jobset.res_bounds)
    ax.grid(True)
    ax.set_title(title)
