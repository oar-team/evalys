def cut_workload(workload_df, begin_time, end_time):
    """ FIXME: Not working yet...
    Extract any workload dataframe between begin_time and end_time.
    Datafram must contain 'submission_time', 'waiting_time' and
    'execution_time' columns.

    Jobs that are queued (submitted but not running) before `begin_time`
    and jobs that are running before `begin_time` and/or after `end_time`
    are cut to fit in this time slice.

    Example with evalys.Workload:
    >>> w = Workload.from_csv("./examples/UniLu-Gaia-2014-2.swf")
    >>> cut_workload(w.df, 0, 10000)

    Example with evalys.JobSet:
    >>> js = JobSet.from_csv("./examples/jobs.csv")
    >>> cut_workload(js.df, 0, 10000)

    """
    assert begin_time < end_time

    # reindex workload by start time to extract easily
    df = workload_df.copy()
    df['starting_time'] = df['submission_time'] + df['waiting_time']
    df = df.sort_values(by='starting_time').set_index(['starting_time'],
                                                      drop=False)

    # find closest index
    begin = df.index.searchsorted(begin_time)
    end = df.index.searchsorted(end_time)

    # Extract jobs that start in the period
    to_export = df[begin:end]

    # Cut submission at begin
    to_export.loc[to_export["submission_time"] < begin_time,
                  "submission_time"] = begin_time
    # Import jobs that start before and stop during or after the period
    to_export.append(df[
        (df["starting_time"] < begin_time) &
        (df["starting_time"] + df["execution_time"] > begin_time)])

    # Cut running jobs at the beginning
    to_export.loc[to_export["starting_time"] < begin_time,
                  "submission_time"] = begin_time

    if not to_export.empty:
        # Cut running jobs at the end
        to_export.loc[to_export["starting_time"] + to_export["execution_time"] > end_time,
                      "finish_time"] = end_time

        to_export.loc[to_export["finish_time"].isna(),"execution_time"] = to_export["finish_time"] - to_export["starting_time"]

    # return dataframe sorted without starting_time column and a proper index
    return to_export.sort_values(by="jobID").reset_index(drop=True)
