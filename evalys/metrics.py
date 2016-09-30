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
    # convert to real time if start_time
    if start_timestamp:
        wt_cumsum.index = pd.to_datetime(
            df_sorted_by_starting_time['starting_time'])
    else:
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

    # convert timestamp to datetime
    event_df.index = pd.to_datetime(event_df['time'] +
                                    int(UnixStartTime), unit='s')

    return event_df.groupby(event_df.index).sum()[col_cumsum].cumsum()
