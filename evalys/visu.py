# coding: utf-8
from __future__ import unicode_literals, print_function

import matplotlib
import matplotlib.patches as mpatch
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import random
import colorsys

from evalys import metrics

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


def plot_gantt(jobset, ax=None, title="Gantt chart",
               labels=True, palette=None, alpha=0.3,
               time_scale=False,
               color_function=None,
               label_function=None):
    # Palette generation if needed
    if palette is None:
        palette = generate_color_set(16)
    assert(len(palette) > 0)

    if color_function is None:
        def color_randrobin_select(job, palette):
            return palette[job.unique_number % len(palette)]
        color_function = color_randrobin_select
    if label_function is None:
        def job_id_label(job):
            return job['jobID']
        label_function = job_id_label

    # Get current axe to plot
    if ax is None:
        ax = plt.gca()

    df = jobset.df.copy()
    df["unique_number"] = np.arange(0, len(df))

    if time_scale:
        df['submission_time'] = pd.to_datetime(df['submission_time'], unit='s')
        df['starting_time'] = pd.to_datetime(df['starting_time'], unit='s')
        df['execution_time'] = pd.to_timedelta(df['execution_time'], unit='s')

    def plot_job(job):
        col = color_function(job, palette)
        duration = job['execution_time']
        for itv in job['allocated_processors'].intervals():
            (y0, y1) = itv
            x0 = job['starting_time']
            if time_scale:
                # Convert date to matplotlib float representation
                x0 = matplotlib.dates.date2num(x0.to_pydatetime())
                finish_time = matplotlib.dates.date2num(
                    job['starting_time'] + job['execution_time']
                )
                duration = finish_time - x0
            rect = mpatch.Rectangle((x0, y0), duration,
                                    y1 - y0 + 0.9, alpha=alpha, color=col)
            if labels:
                annotate(ax, rect, str(label_function(job)))
            ax.add_artist(rect)

    # apply for all jobs
    df.apply(plot_job, axis=1)

    # set graph limits, grid and title
    ax.set_xlim(df['submission_time'].min(), (
        df['starting_time'] + df['execution_time']).max())
    ax.set_ylim(jobset.res_bounds[0]-1, jobset.res_bounds[1]+2)
    ax.grid(True)
    ax.set_title(title)


def plot_pstates(pstates, x_horizon, ax=None, palette=None,
                 off_pstates=None,
                 son_pstates=None,
                 soff_pstates=None):
    # palette generation if needed
    if palette is None:
        palette = ["#000000", "#56ae6c", "#ba495b"]
    assert(len(palette) >= 3)
    labels = ["OFF", "switch ON", "switch OFF"]
    alphas = [0.6, 1, 1]

    if off_pstates is None:
        off_pstates = set()
    if son_pstates is None:
        son_pstates = set()
    if soff_pstates is None:
        soff_pstates = set()
    # Get current axe to plot
    if ax is None:
        ax = plt.gca()

    interesting_pstates = off_pstates | son_pstates | soff_pstates

    for _, job in pstates.pseudo_jobs.iterrows():
        if job['pstate'] in interesting_pstates:
            if job['pstate'] in off_pstates:
                col_id = 0
            elif job['pstate'] in son_pstates:
                col_id = 1
            elif job['pstate'] in soff_pstates:
                col_id = 2

            color = palette[col_id]
            alpha = alphas[col_id]
            label = labels[col_id]

            interval_list = pstates.intervals[job['interval_id']]
            for machine_interval in interval_list:
                (y0, y1) = machine_interval
                (b, e) = (job['begin'], min(job['end'], x_horizon))
                rect = mpatch.Rectangle((b, y0), e - b, y1 - y0 + 0.9,
                                        color=color, alpha=alpha,
                                        label=label)
                ax.add_artist(rect)


def plot_mstates(mstates_df, ax=None, title=None, palette=None, reverse=True):
    # Parameter handling
    if palette is None:
        # Colorblind palette
        palette = ["#000000", "#56ae6c", "#ba495b", "#000000", "#8960b3"]

    stack_order = ['nb_sleeping', 'nb_switching_on', 'nb_switching_off',
                   'nb_idle', 'nb_computing']

    alphas = [0.6, 1, 1, 0, 0.3]

    assert(len(palette) == len(stack_order)), \
        "Palette should be of size {}".format(len(stack_order))

    # Get current axe to plot
    if ax is None:
        ax = plt.gca()

    # Should the display order be reversed?
    if reverse:
        palette = palette[::-1]
        stack_order = stack_order[::-1]
        alphas = alphas[::-1]

    # Computing temporary date to compute the stacked area
    y = np.row_stack(tuple([mstates_df[x] for x in stack_order]))
    y = np.cumsum(y, axis=0)

    # Plotting
    first_i = 0
    ax.fill_between(mstates_df['time'], 0, y[first_i, :],
                    facecolor=palette[first_i], alpha=alphas[first_i],
                    step='post', label=stack_order[first_i])

    for index, _ in enumerate(stack_order[1:]):
        ax.fill_between(mstates_df['time'], y[index, :], y[index+1, :],
                        facecolor=palette[index+1], alpha=alphas[index+1],
                        step='post',
                        label=stack_order[index+1])

    if title is not None:
        ax.set_title(title)


def plot_gantt_pstates(jobset, pstates, ax, title, labels=True,
                       off_pstates=None,
                       son_pstates=None,
                       soff_pstates=None):

    if off_pstates is None:
        off_pstates = set()
    if son_pstates is None:
        son_pstates = set()
    if soff_pstates is None:
        soff_pstates = set()
    plot_gantt(jobset, ax, title, labels, palette=["#8960b3"], alpha=0.3)

    fpb = pstates.pseudo_jobs.loc[pstates.pseudo_jobs['end'] < float('inf')]

    ax.set_xlim(min(jobset.df.submission_time.min(), fpb.begin.min()),
                max(jobset.df.finish_time.max(), fpb.end.max()))
    ax.set_ylim(min(jobset.res_bounds[0], pstates.res_bounds[0]),
                max(jobset.res_bounds[1], pstates.res_bounds[1]))
    ax.grid(True)
    ax.set_title(title)

    plot_pstates(pstates, ax.get_xlim()[1], ax,
                 off_pstates=off_pstates,
                 son_pstates=son_pstates,
                 soff_pstates=soff_pstates)


def plot_processor_load(jobset, ax=None, title="Load", labels=True):
    """
    Display the impact of each job on the load of each processor.

    need: execution_time, jobID, allocated_processors
    """

    # Get current axe to plot
    if ax is None:
        ax = plt.gca()

    def _draw_rect(ax, base, width, height, color, label):
        rect = mpatch.Rectangle(base, width, height, alpha=0.2, color=color)
        if label:
            annotate(ax, rect, label)
        ax.add_artist(rect)

    RGB_tuples = generate_color_set(16)
    load = {
        p: 0.0 for p in range(jobset.res_bounds[0], jobset.res_bounds[1] + 1)
    }

    for row in jobset.df.itertuples():
        color = RGB_tuples[row.Index % len(RGB_tuples)]
        duration = row.execution_time
        label = row.jobID if labels else None

        baseproc = next(iter(row.allocated_processors))
        base = (baseproc, load[baseproc])
        width = 0  # width is incremented in the first loop iteration
        for proc in row.allocated_processors:
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


def plot_series(series_type, jobsets, ax=None, time_scale=False):
    '''
    Plot one or several time series about provided jobsets on the given ax
    series_type can be any value present in available_series.
    '''
    # Get current axe to plot
    if ax is None:
        ax = plt.gca()

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
            if time_scale:
                series[jobset_name].index = pd.to_datetime(
                    jobset.df['submission_time'] + jobset.df['waiting_time'],
                    unit='s')
        # plot series
        for serie_name, serie in series.items():
            serie.plot(ax=ax, label=serie_name, drawstyle="steps")
    else:
        raise RuntimeError('The serie \"{}\" is not implemeted yet')

    # Manage legend
    ax.legend()
    ax.set_title(series_type)
    ax.grid(True)


def plot_gantt_general_shape(jobset_list, ax=None, alpha=0.3,
                             title="Gantt general shape"):
    '''
    Draw a general gantt shape of multiple jobsets on one plot for comparison
    '''
    # Get current axe to plot
    if ax is None:
        ax = plt.gca()

    color_index = 0
    RGB_tuples = generate_color_set(len(jobset_list))
    legend_rect = []
    legend_label = []
    xmin = None
    xmax = None
    for jobset_name, jobset in jobset_list.items():
        # generate color
        color = RGB_tuples[color_index % len(RGB_tuples)]
        color_index += 1

        # generate legend
        legend_rect.append(
            mpatch.Rectangle((0, 1), 12, 10, alpha=alpha, color=color))
        legend_label.append(jobset_name)

        def plot_job(job):
            duration = job['execution_time']
            for itv in job['allocated_processors'].intervals():
                (y0, y1) = itv
                rect = mpatch.Rectangle((job['starting_time'], y0), duration,
                                        y1 - y0 + 0.9, alpha=alpha,
                                        color=color)
                ax.add_artist(rect)

        # apply for all jobs
        jobset.df.apply(plot_job, axis=1)

        # compute graphical boundaries
        if not xmin or jobset.df.submission_time.min() < xmin:
            xmin = jobset.df.submission_time.min()
        if not xmax or jobset.df.finish_time.max() < xmax:
            xmax = jobset.df.finish_time.max()

    # do include legend
    ax.legend(legend_rect, legend_label, loc='center',
              bbox_to_anchor=(0.5, 1.06),
              fancybox=True, shadow=True, ncol=5)
    ax.set_xlim((xmin, xmax))
    # use last jobset of the previous loop to set the resource bounds assuming
    # that all the gantt have the same number of resources
    ax.set_ylim(jobset.res_bounds[0]-1, jobset.res_bounds[1]+2)
    ax.grid(True)
    ax.set_title(title)


def plot_job_details(dataframe, size, ax=None, title="Job details",
                     time_scale=False, time_offset=0):
    # TODO manage also the Jobset case
    # Get current axe to plot
    if ax is None:
        ax = plt.gca()

    # Avoid side effect
    df = pd.DataFrame.copy(dataframe)
    df = df.sort_values(by='jobID')

    df['submission_time'] = df['submission_time'] + time_offset
    df['starting_time'] = df['submission_time'] + df['waiting_time']
    df['finish_time'] = df['starting_time'] + df['execution_time']

    to_plot = [('starting_time', 'green', '>', size),
               ('submission_time', 'blue', '.', 0),
               ('finish_time', 'red', '|', size * 2)]

    lines = [['submission_time', 'starting_time', 'blue', 0, size],
             ['starting_time', 'finish_time', 'green', size, size * 2]]

    if time_scale:
        df['submission_time'] = pd.to_datetime(df['submission_time'], unit='s')
        df['starting_time'] = pd.to_datetime(df['starting_time'], unit='s')
        df['finish_time'] = pd.to_datetime(df['finish_time'], unit='s')

    # select the axe
    plt.sca(ax)

    # plot lines
    # add jitter
    jitter = size / 20
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
        if time_scale:
            # Convert date to matplotlib float representation
            x = x.dt.to_pydatetime()
        y = new_proc_alloc + treshold
        plt.scatter(x, y, c=color, marker=marker,
                    s=60, label=serie, alpha=0.5)

    ax.grid(True)
    ax.legend()
    ax.set_title(title)


def plot_series_comparison(series, ax=None, title="Series comparison"):
    ''' Plot and compare two serie in post step '''
    assert len(series) == 2
    # Get current axe to plot
    if ax is None:
        ax = plt.gca()

    first_serie_name = list(series.keys())[0]
    first_serie = list(series.values())[0]
    first_serie.plot(drawstyle="steps-post", ax=ax, label=first_serie_name)

    second_serie_name = list(series.keys())[1]
    second_serie = list(series.values())[1]
    second_serie.plot(drawstyle="steps-post", ax=ax, label=second_serie_name)

    df = pd.DataFrame(series, index=first_serie.index).fillna(method='ffill')
    y1 = df[first_serie_name]
    y2 = df[second_serie_name]
    ax.fill_between(df.index, y1, y2, where=y2 < y1, facecolor='red',
                    step='post', alpha=0.5,
                    label=first_serie_name + ">" + second_serie_name)
    ax.fill_between(df.index, y1, y2, where=y2 > y1, facecolor='green',
                    step='post', alpha=0.5,
                    label=first_serie_name + "<" + second_serie_name)
    ax.grid(True)
    ax.set_title(title)


def plot_fragmentation(frag, ax=None, label="Fragmentation"):
    """
    Plot fragmentation raw data, distribution and ecdf in 3 subplots
    given in the ax list
    fragmentation can be optain using fragmentation method
    """
    # Get current axe to plot
    if ax is None:
        ax = plt.subplots(nrows=3)

    assert len(ax) == 3

    # direct plot
    frag.plot(ax=ax[0], label=label)
    ax[0].set_title("Fragmentation over resources")

    # plot distribution
    sns.distplot(frag, ax=ax[1], label=label, kde=False, rug=True)
    ax[1].set_title("Fragmentation distribution")

    # plot ecdf
    from statsmodels.distributions.empirical_distribution import ECDF
    ecdf = ECDF(frag)
    ax[2].step(ecdf.x, ecdf.y, label=label)
    ax[2].set_title("Fragmentation ecdf")


def plot_load(load, nb_resources=None, ax=None, normalize=False,
              time_scale=False, load_label="load",
              UnixStartTime=0, TimeZoneString='UTC'):
    '''
    Plots the number of used resources against time
    :normalize: if True normalize by the number of resources
    `nb_resources`
    '''
    mean = metrics.load_mean(load)
    u = load.copy()

    if time_scale:
        # make the time index a column
        u = u.reset_index()
        # convert timestamp to datetime
        u.index = pd.to_datetime(u['time'] + UnixStartTime,
                                 unit='s')
        u.index.tz_localize('UTC').tz_convert(TimeZoneString)

    if normalize and nb_resources is None:
        nb_resources = u.load.max()

    if normalize:
        u.load = u.load / nb_resources
        mean = mean / nb_resources

    # get an axe if not provided
    if ax is None:
        ax = plt.gca()

    # leave room to have better view
    ax.margins(x=0.1, y=0.1)

    # plot load
    u.load.plot(drawstyle="steps-post", ax=ax, label=load_label)

    # plot a line for max available area
    if nb_resources and not normalize:
        ax.plot([u.index[0], u.index[-1]],
                [nb_resources, nb_resources],
                linestyle='-', linewidth=2,
                label="Maximum resources ({})".format(nb_resources))

    # plot a line for mean utilisation
    ax.plot([u.index[0], u.index[-1]],
            [mean, mean],
            linestyle='--', linewidth=1,
            label="Mean {0} ({1:.2f})".format(load_label, mean))
    sns.rugplot(u.load[u.load == 0].index, ax=ax, color='r')
    ax.scatter([], [], marker="|", linewidth=1, s=200,
               label="Reset event ({} == 0)".format(load_label), color='r')
    # FIXME: Add legend when this bug is fixed
    # https://github.com/mwaskom/seaborn/issues/1071

    # ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    ax.grid(True)
    ax.legend()
    ax.set_title(load_label)


def plot_free_resources(utilisation, nb_resources, normalize=False,
                        time_scale=False,
                        UnixStartTime=0, TimeZoneString='UTC'):
    '''
    Plots the number of free resources against time
    :normalize: if True normalize by the number of resources `nb_resources`
    '''
    free = nb_resources - utilisation

    if normalize:
        free = free / nb_resources

    if time_scale:
        free.index = pd.to_datetime(free['time'] + UnixStartTime,
                                    unit='s', utc=True)
        free.index.tz_localize('UTC').tz_convert(TimeZoneString)

    free.plot()
    # plot a line for the number of procs
    plt.plot([free.index[0], free.index[-1]],
             [nb_resources, nb_resources],
             linestyle='-', linewidth=1,
             label="Maximum resources ({})".format(nb_resources))
