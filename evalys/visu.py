# coding: utf-8
from __future__ import unicode_literals, print_function

import matplotlib
import matplotlib.patches as mpatch
from matplotlib import pyplot as plt
import pandas as pd
from evalys import metrics
import random

import colorsys


# plt.style.use('ggplot')

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


def plot_gantt(jobset, ax, title, labels=True):
    for i, job in jobset.df.iterrows():
        RGB_tuples = generate_color_set(16)
        col = RGB_tuples[i % len(RGB_tuples)]
        duration = job['execution_time']
        for itv in jobset.res_set[job['jobID']]:
            (y0, y1) = itv
            rect = mpatch.Rectangle((job['starting_time'], y0), duration,
                                    y1 - y0 + 0.9, alpha=0.2, color=col)
            if labels:
                annotate(ax, rect, str(job['jobID']))
            ax.add_artist(rect)

    ax.set_xlim((jobset.df.submission_time.min(), jobset.df.finish_time.max()))
    ax.set_ylim(jobset.res_bounds)
    ax.grid(True)
    ax.set_title(title)


def plot_pstates(pstates, x_horizon, ax, off_pstates=[]):
    for _, job in pstates.pseudo_jobs.iterrows():
        if job['pstate'] in off_pstates:
            interval_list = pstates.intervals[job['interval_id']]
            for machine_interval in interval_list:
                (y0, y1) = machine_interval
                (b, e) = (job['begin'], min(job['end'], x_horizon))
                rect = mpatch.Rectangle((b, y0), e - b, y1 - y0 + 0.9,
                                        color=(0, 0, 0))
                ax.add_artist(rect)


def plot_gantt_pstates(jobset, pstates, ax, title,
                       labels=True, off_pstates=[]):

    plot_gantt(jobset, ax, title, labels)

    fpb = pstates.pseudo_jobs.loc[pstates.pseudo_jobs['end'] < float('inf')]

    ax.set_xlim(min(jobset.df.submission_time.min(), fpb.begin.min()),
                max(jobset.df.finish_time.max(), fpb.end.max()))
    ax.set_ylim(min(jobset.res_bounds[0], pstates.res_bounds[0]),
                max(jobset.res_bounds[1], pstates.res_bounds[1]))
    ax.grid(True)
    ax.set_title(title)

    plot_pstates(pstates, ax.get_xlim()[1], ax, off_pstates)


def plot_load(jobset, ax, title, labels=True):
    """
    Display the impact of each job on the load of each processor.

    need: execution_time, jobID, allocated_processors
    """
    from evalys.jobset import interval_set_to_set, string_to_interval_set
    # XXX: find a better way to organize modules to avoid this unnecessary
    # circular dependency avoidance trick

    def _draw_rect(ax, base, width, height, color, label):
        rect = mpatch.Rectangle(base, width, duration, alpha=0.2, color=color)
        if label:
            annotate(ax, rect, label)
        ax.add_artist(rect)

    RGB_tuples = generate_color_set(16)
    load = {p: 0.0 for p in range(*jobset.res_bounds)}

    for row in jobset.df.itertuples():
        color = RGB_tuples[row.Index % len(RGB_tuples)]
        duration = row.execution_time
        label = row.jobID if labels else None

        procset = sorted(
            interval_set_to_set(
                string_to_interval_set(
                    str(row.allocated_processors)
                )
            )
        )
        base = (procset[0], load[procset[0]])
        width = 0  # width is incremented in the first loop iteration
        for proc in procset:
            if base[0] + width != proc or load[proc] != base[1]:
                # we cannot merge across processors: draw the current
                # rectangle, and start anew
                _draw_rect(ax, base, width, duration, color, label)
                base = (proc, load[proc])
                width = 1
            else:
                # we can merge across processors: extend width, and continue
                width += 1
            load[proc] += duration

        # draw last pending rectangle if necessary
        if width > 0:
            _draw_rect(ax, base, width, duration, color, label)

    ax.set_xlim(jobset.res_bounds)
    ax.set_ylim(0, 1.02 * max(load.values()))
    ax.grid(True)
    ax.set_title(title)
    ax.set_xlabel('proc. id')
    ax.set_ylabel('load / s')


def plot_series(series_type, jobsets, ax_series):
    '''
    Plot one or several time series about provided jobsets on the given ax
    series_type can be any value present in available_series.
    '''
    if series_type not in available_series:
        raise AttributeError(
            "The gieven attribute should be one of the folowing:"
            "{}".format(available_series))

    if series_type == "waiting_time":
        series = {}
        for jobset_name in jobsets.keys():
            jobset = jobsets[jobset_name]
            #  create a serie
            series[jobset_name] = metrics.cumulative_waiting_time(jobset.df)
            series[jobset_name].index = pd.to_datetime(
                jobset.df['submission_time'] + jobset.df['waiting_time'],
                unit='s')
        # plot series
        for serie_name, serie in series.items():
            serie.plot(ax=ax_series, label=serie_name, drawstyle="steps")
    else:
        raise RuntimeError('The serie \"{}\" is not implemeted yet')

    # Manage legend
    ax_series.legend(loc='upper left')
    ax_series.set_title(series_type)
    ax_series.grid(True)


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
    ax.set_xlim((jobset.df.submission_time.min(), jobset.df.finish_time.max()))
    ax.set_ylim(jobset.res_bounds)
    ax.grid(True)
    ax.set_title("General shape")


def plot_job_details(dataframe, size, ax, title):
    # TODO manage also the Jobset case
    # Avoid side effect
    df = pd.DataFrame.copy(dataframe)
    df = df.sort_values(by='jobID')

    df['starting_time'] = df['submission_time'] + df['waiting_time']
    df['finish_time'] = df['starting_time'] + df['execution_time']

    to_plot = [('starting_time', 'green', '>', size),
               ('submission_time', 'blue', '.', 0),
               ('finish_time', 'red', '|', size * 2)]

    lines = [['submission_time', 'starting_time', 'blue', 0, size],
             ['starting_time', 'finish_time', 'green', size, size * 2]]

    df['submission_time'] = pd.to_datetime(df['submission_time'], unit='s')
    df['starting_time'] = pd.to_datetime(df['starting_time'], unit='s')
    df['finish_time'] = pd.to_datetime(df['finish_time'], unit='s')

    # select the axe
    plt.sca(ax)

    # plot lines
    # add jitter
    jitter = size / 10
    random.seed(a=0)
    new_proc_alloc = df['proc_alloc'].apply(
        lambda x: x + random.uniform(-jitter, jitter))
    for begin, end, color, treshold_begin, treshold_end in lines:
        for i, item in df.iterrows():
            x_begin = item[begin]
            x_end = item[end]
            plt.plot([x_begin, x_end], [new_proc_alloc[i] + treshold_begin,
                                        new_proc_alloc[i] + treshold_end],
                     color=color, linestyle='-', linewidth=1, alpha=0.2)

    # plot one point per serie
    for serie, color, marker, treshold in to_plot:
        x = df[serie]
        # Convert date to matplotlib float representation
        x = x.dt.to_pydatetime()
        y = new_proc_alloc + treshold
        plt.scatter(x, y, c=color, marker=marker,
                    s=60, label=serie, alpha=0.5)

    ax.grid(True)
    ax.set_title(title)


def plot_series_comparison(series, axe, title):
    ''' Plot and compare two serie in post step '''
    assert len(series) == 2

    first_serie_name = list(series.keys())[0]
    first_serie = list(series.values())[0]
    first_serie.plot(drawstyle="steps-post", ax=axe, label=first_serie_name)

    second_serie_name = list(series.keys())[1]
    second_serie = list(series.values())[1]
    second_serie.plot(drawstyle="steps-post", ax=axe, label=second_serie_name)

    df = pd.DataFrame(series).fillna(method='ffill')
    y1 = df[first_serie_name]
    y2 = df[second_serie_name]
    axe.fill_between(df.index, y1, y2, where=y2 < y1, facecolor='red',
                     step='post', alpha=0.5,
                     label=first_serie_name + ">" + second_serie_name)
    axe.fill_between(df.index, y1, y2, where=y2 > y1, facecolor='green',
                     step='post', alpha=0.5,
                     label=first_serie_name + "<" + second_serie_name)
    axe.grid(True)
    axe.set_title(title)
