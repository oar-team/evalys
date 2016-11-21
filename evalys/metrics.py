import pandas as pd


def cumulative_waiting_time(dataframe, start_timestamp=None):
    '''
    Input: a DataFrame that contains a starting_time and a waiting_time
    column
    '''
    # Avoid side effect
    df = pd.DataFrame.copy(dataframe)
    df['starting_time'] = df['submission_time'] + df['waiting_time']
    df_sorted_by_starting_time = df.sort_values(by='starting_time')

    wt_cumsum = df_sorted_by_starting_time.waiting_time.cumsum()
    # Sort by starting time
    wt_cumsum.index = df_sorted_by_starting_time['starting_time']
    return wt_cumsum


def compute_load(dataframe, col_begin, col_end, col_cumsum,
                 UnixStartTime=0):
    # Avoid side effect
    df = pd.DataFrame.copy(dataframe)
    df['starting_time'] = df['submission_time'] + df['waiting_time']
    df['stop'] = df['starting_time'] + df['execution_time']

    df = df.sort_values(by=col_begin)

    # Cleaning:
    # - still running jobs (runtime = -1)
    # - not scheduled jobs (wait = -1)
    # - no procs allocated (proc_alloc = -1)
    max_time = df['stop'].max() + 1000
    df.ix[df['execution_time'] == -1, 'stop'] = max_time
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
        columns=["proc_alloc"])
    load_df["time"] = load_df.index

    # compute area
    load_df["area"] = - load_df["time"].diff(-1) * load_df[col_cumsum]
    del load_df["time"]

    return load_df


def _load_insert_element_if_necessary(load_df, at):
    if len(load_df[load_df.time == at]) == 0:
        prev_el = load_df[load_df.time <= at].tail(1)
        new_el = prev_el.copy()
        next_el = load_df[load_df.time >= at].head(1)
        new_el.time = at
        new_el.area = float(new_el.proc_alloc) * float(next_el.time - at)
        load_df.loc[prev_el.index, "area"] = \
            float(prev_el.proc_alloc) * float(at - prev_el.time)
        load_df.loc[len(load_df)] = [
            float(new_el.time),
            float(new_el.proc_alloc),
            float(new_el.area)]
        load_df = load_df.sort_values(by=["time"])
    return load_df


def load_mean(df, begin=None, end=None):
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

    u = load_df[load_df.time < end]
    u = u[begin <= u.time]

    return u.area.sum()/(end - begin)
