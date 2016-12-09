import pandas as pd
from math import sqrt


def cumulative_waiting_time(dataframe):
    '''
    Compute the cumulative waiting time on the given dataframe

    :dataframe: a DataFrame that contains a "starting_time" and a
        "waiting_time" column.
    '''
    # Avoid side effect
    df = pd.DataFrame.copy(dataframe)
    df['starting_time'] = df['submission_time'] + df['waiting_time']
    df_sorted_by_starting_time = df.sort_values(by='starting_time')

    wt_cumsum = df_sorted_by_starting_time.waiting_time.cumsum()
    wt_cumsum.name = "cumulative waiting time"
    # Sort by starting time
    wt_cumsum.index = df_sorted_by_starting_time['starting_time']

    return wt_cumsum


def compute_load(dataframe, col_begin, col_end, col_cumsum,
                 begin_time=0, end_time=None):
    """
    Compute the load of the `col_cumsum` columns between events from
    `col_begin` to `col_end`. In practice it is used to compute the queue
    load and the cluster load (utilisation).

    :returns: a load dataframe of all events indexed by time with a `load`
        and an `area` column.
    """
    # Avoid side effect
    df = pd.DataFrame.copy(dataframe)
    df['starting_time'] = df['submission_time'] + df['waiting_time']
    df['finish_time'] = df['starting_time'] + df['execution_time']

    df = df.sort_values(by=col_begin)

    # Cleaning:
    # - still running jobs (runtime = -1)
    # - not scheduled jobs (wait = -1)
    # - no procs allocated (proc_alloc = -1)
    max_time = df['finish_time'].max() + 1000
    df.ix[df['execution_time'] == -1, 'finish_time'] = max_time
    df.ix[df['execution_time'] == -1, 'starting_time'] = max_time
    df = df[df['proc_alloc'] > 0]

    # Create a list of start and stop event associated to the number of
    # proc allocation changes: starts add procs, stop remove procs
    event_columns = ['time', col_cumsum, 'jobID']
    start_event_df = pd.concat([df[col_begin],
                                df[col_cumsum],
                                df['jobID']],
                               axis=1)
    start_event_df.columns = event_columns
    # Stop event give negative proc_alloc value
    stop_event_df = pd.concat([df[col_end],
                               - df[col_cumsum],
                               df['jobID']],
                              axis=1)
    stop_event_df.columns = event_columns

    # merge events and sort them
    event_df = start_event_df.append(
        stop_event_df,
        ignore_index=True).sort_values(by='time').reset_index(drop=True)

    # sum the event that happend at the same time and cummulate events
    load_df = pd.DataFrame(
        event_df.groupby(event_df['time'])[col_cumsum].sum().cumsum(),
        columns=[col_cumsum])
    load_df["time"] = load_df.index

    # compute area
    load_df["area"] = - load_df["time"].diff(-1) * load_df[col_cumsum]
    del load_df["time"]

    load_df.columns = ["load", "area"]

    return load_df


def _load_insert_element_if_necessary(load_df, at):
    """
    Insert an event at the specified point that conserve data consistency
    for "area" and "load" values
    """
    if len(load_df[load_df.time == at]) == 0:
        prev_el = load_df[load_df.time <= at].tail(1)
        new_el = prev_el.copy()
        next_el = load_df[load_df.time >= at].head(1)
        new_el.time = at
        new_el.area = float(new_el.load) * float(next_el.time - at)
        load_df.loc[prev_el.index, "area"] = \
            float(prev_el.load) * float(at - prev_el.time)
        load_df.loc[len(load_df)] = [
            float(new_el.time),
            float(new_el.load),
            float(new_el.area)]
        load_df = load_df.sort_values(by=["time"])
    return load_df


def load_mean(df, begin=None, end=None):
    """ Compute the mean load area from begin to end. """
    load_df = df.reset_index()
    max_to = max(load_df.time)
    if end is None:
        end = max_to
    elif end > max_to:
        raise ValueError("computing mean load after the "
                         "last event ({}) is NOT IMPLEMENTED".format(max_to))
    min_to = load_df.time.iloc[0]
    if begin is None:
        begin = min_to
    elif begin < min_to:
        raise ValueError("computing mean load befor the "
                         "first event ({}) is NOT IMPLEMENTED".format(min_to))

    load_df = _load_insert_element_if_necessary(load_df, begin)
    load_df = _load_insert_element_if_necessary(load_df, end)

    u = load_df[(load_df.time < end) & (begin <= load_df.time)]

    return u.area.sum()/(end - begin)


def fragmentation(free_resources_gaps, p=2):
    """
    Input is a resource indexed list where each element is a numpy
    array of free slots.

    This metrics definition comes from Gher and Shneider CCGRID 2009.
    """
    f = free_resources_gaps
    frag = pd.Series()
    for i, fi in enumerate(f):
        if fi.size == 0:
            frag_i = 0
        else:
            frag_i = 1 - (sum(fi**p) / sum(fi)**p)
        frag.set_value(i, frag_i)
    return frag


def fragmentation_reis(free_resources_gaps, time, p=2):
    f = free_resources_gaps
    frag = pd.Series()
    for i, fi in enumerate(f):
        if fi.size == 0:
            frag_i = 0
        else:
            frag_i = 1 - (sqrt(sum(fi**p)) / time * len(f))
        frag.set_value(i, frag_i)
    return frag
