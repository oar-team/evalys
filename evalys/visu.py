# coding: utf-8
from __future__ import unicode_literals, print_function

import matplotlib
import matplotlib.patches as mpatch
from matplotlib import pyplot as plt
import pandas as pd

import colorsys

plt.style.use('ggplot')

matplotlib.rcParams['figure.figsize'] = (12.0, 8.0)

available_series = ['bonded_slowdown', 'waiting_time', 'all']


def generate_color_set(nb_colors):
    HSV_tuples = [(x * 1.0 / nb_colors, 1, 0.7) for x in range(nb_colors)]
    return list(map(lambda x: colorsys.hsv_to_rgb(*x), HSV_tuples))


def annotate(ax, rect, annot):
    rx, ry = rect.get_xy()
    cx = rx + rect.get_width() / 2.0
    cy = ry + rect.get_height() / 2.0

    ax.annotate(annot, (cx, cy), color='black',
                fontsize='small', ha='center', va='center')


def plot_gantt(jobset, ax, title):
    for i, job in jobset.df.iterrows():
        RGB_tuples = generate_color_set(16)
        col = RGB_tuples[i % len(RGB_tuples)]
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


def plot_series(series_type, jobsets, ax_series):
    '''
    Plot one or several time series about provided jobsets on the given ax
    series_type can be any value present in available_series.
    '''
    if series_type not in available_series:
        raise AttributeError("The gieven attribute should be one of the folowing: {}".format(available_series))

    if series_type == "bonded_slowdown":
        pass
    elif series_type == "waiting_time":
        series = {}
        indexes = {}
        series_data = {}
        # calculate series for each jobset
        for jobset_name in jobsets.keys():
            indexes[jobset_name] = []
            series_data[jobset_name] = []
            jobset = jobsets[jobset_name]

            df_sorted_by_finished_time = jobset.df.sort_values(by='finish_time')
            for index in range(1, len(df_sorted_by_finished_time)):
                df_cut = df_sorted_by_finished_time[:index]
                # store index
                event_time = df_cut.finish_time[-1:].values[0]
                indexes[jobset_name].append(event_time)
                # store summed waiting_time
                waiting_time_sum = df_cut.waiting_time.sum()
                series_data[jobset_name].append(waiting_time_sum)
            #  create a serie
            series[jobset_name] = pd.Series(data=series_data[jobset_name],
                                            index=indexes[jobset_name])
        # plot series
        for serie_name, serie in series.items():
            ax_series.plot(serie)
        ax_series.set_title(series_type)

    elif series_type == "all":
        pass
    else:
        raise RuntimeError('The serie \"{}\" is not implemeted yet')


def plot_gantt_general_shape(jobset_list, ax):
    '''
    Draw a general gantt shape of multiple jobsets on one plot for comparison
    '''
    color_index = 0
    RGB_tuples = generate_color_set(len(jobset_list))
    legend_rect = []
    legend_label = []
    for jobset_name, jobset in jobset_list.items():
        # generate color
        color = RGB_tuples[color_index % len(RGB_tuples)]
        color_index += 1

        # generate legend
        legend_rect.append(
            mpatch.Rectangle((0, 1), 12, 10, alpha=0.2, color=color))
        legend_label.append(jobset_name)

        for i, job in jobset.df.iterrows():
            duration = job['execution_time']
            for i, itv in enumerate(jobset.res_set[job['jobID']]):
                (y0, y1) = itv
                rect = mpatch.Rectangle((job['starting_time'], y0), duration,
                                        y1 - y0 + 0.9, alpha=0.2,
                                        color=color)
                ax.add_artist(rect)

    # do include legend
    ax.legend(legend_rect, legend_label, loc='center',
              bbox_to_anchor=(0.5, 1.06),
              fancybox=True, shadow=True, ncol=5)
