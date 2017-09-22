# coding: utf-8

import functools

from matplotlib import pyplot as plt
import matplotlib.patches as mpatch
import matplotlib.dates as mdates
import numpy as np
import pandas as pd

from . import core

# helper functions: formatting of df  #####

def _default_format_df(df):
    df['unique_number'] = np.arange(0, len(df))


def _time_scaled_format_df(df):
    # interpret columns with time aware semantics
    df.submission_time = pd.to_datetime(df.submission_time, unit='s')
    df.starting_time = pd.to_datetime(df.starting_time, unit='s')
    df.execution_time = pd.to_timedelta(df.execution_time, unit='s')
    df.finish_time = df.starting_time +  df.execution_time
    # convert columns to use them with matplotlib
    df.starting_time = df.starting_time.map(mdates.date2num)
    df.finish_time = df.finish_time.map(mdates.date2num)
    df.execution_time = df.finish_time - df.starting_time


def _chain_df_formatters(*formatters):
    """
    List[Callable[[pandas.DataFrame], None]] -> Callable[pandas.DataFrame[], None]

    Chain the formatters in the order they are provided. The operations must be
    in place.
    """
    def _chained_df_formatter(df):
        for format_df in formatters:
            format_df(df)
    return _chained_df_formatter


# helper functions: drawing of jobs  #####

def _round_robin_map(job, palette):
    return palette[job.unique_number % len(palette)]


def _annotate(rect, label):
    rx, ry = rect.get_xy()
    cx = rx + rect.get_width() / 2.0
    cy = ry + rect.get_height() / 2.0

    rect.axes.annotate(
        label,
        (cx, cy),
        color='black',
        fontsize='small',
        ha='center',
        va='center'
    )

def _plot_job(job, **kwargs):
    x0 = job.starting_time
    duration = job.execution_time
    for itv in job.allocated_processors.intervals():
        height = itv.sup - itv.inf + 0.9
        rect = mpatch.Rectangle(
            (x0, itv.inf),
            duration,
            height,
            alpha=kwargs['alpha'],
            facecolor=kwargs['color_function'](job),
            edgecolor='black',
            linewidth=0.5
        )
        kwargs['ax'].add_artist(rect)
        if kwargs['label_function'] is not None:
            _annotate(rect, kwargs['label_function'](job))


# helper functions: configuration of display  #####

def _configure_display(df, **kwargs):
    kwargs['ax'].set(
        xlim=(df.submission_time.min(), df.finish_time.max()),
        ylim=kwargs['ylim'],
        title=kwargs['title']
    )
    kwargs['ax'].grid(True)


# actual visualization definition  #####

def _core_gantt(jobset, format_df, plot_job, configure_display, *, columns=()):

    # do not alter original data, create a new df
    if columns:
        df = jobset.df.loc[:, columns]
    else:
        df = jobset.df.copy()  # do not alter original data, copy all
    assert df is not jobset.df

    format_df(df)
    df.apply(plot_job, axis='columns')
    configure_display(df)


def plot_gantt(jobset, **kwargs):

    _params = {  # default values of parameters
        'ax': plt.gca(),
        'title': 'Gantt chart',
        'labels': True,
        'alpha': 0.4,
        'time_scale': False,
        'palette': core.generate_palette(8),
        'color_function': _round_robin_map,
        'label_function': lambda job: str(job.jobID),
    }
    _params.update(kwargs)  # user supplied parameters have priority
    _params['color_function'] = \
            functools.partial(  # bind palette once everything is known
                _params['color_function'],
                palette=_params['palette']
            )

    # set up core functions
    _df_formatters = [_default_format_df]
    if _params['time_scale']:
        _df_formatters.append(_time_scaled_format_df)
    format_df = _chain_df_formatters(*_df_formatters)

    plot_job = functools.partial(_plot_job, **_params)

    configure_display = \
            functools.partial(
                _configure_display,
                ylim=(jobset.res_bounds.inf - 1, jobset.res_bounds.sup + 2),
                **_params
            )

    # do the job!
    cols = (
        'jobID',
        'allocated_processors',
        'execution_time',
        'finish_time',
        'starting_time',
        'submission_time',
    )
    _core_gantt(jobset, format_df, plot_job, configure_display, columns=cols)
