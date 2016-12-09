def cut_workload(workload_df, begin_time, end_time):
    """
    Extract any workload dataframe between begin_time and end_time.
    Datafram must contain 'submission_time', 'waiting_time' and
    'execution_time' + 'jobID'  columns.

    Jobs that are queued (submitted but not running) before `begin_time`
    and jobs that are running before `begin_time` and/or after `end_time`
    are cut to fit in this time slice.

    Example with :py:class:`evalys.Workload`:

    >>> from evalys.workload import Workload
    >>> w = Workload.from_csv("./examples/UniLu-Gaia-2014-2.swf")
    >>> cut_w = cut_workload(w.df, 500000, 600000)

    Example with :py:class:`evalys.JobSet`:

    >>> from evalys.jobset import JobSet
    >>> js = JobSet.from_csv("./examples/jobs.csv")
    >>> cut_js = cut_workload(js.df, 1000, 2000)

    """
    assert begin_time < end_time

    # reindex workload by start time to extract easily
    df = workload_df.copy()
    df['starting_time'] = df['submission_time'] + df['waiting_time']
    df = df.sort_values(by='submission_time').set_index(['submission_time'],
                                                        drop=False)

    # find closest index
    begin = df.index.searchsorted(begin_time)
    end = df.index.searchsorted(end_time)

    # Extract jobs that start in the period
    to_export = df.iloc[begin:end]

    # Get job in queue (submission before period begin and start in the period)
    queued_jobs = df[(df["submission_time"] < begin_time)
                     & (df["starting_time"] >= begin_time)]

    # Get running jobs (start before and stop during or after the period)
    running_jobs = df[
        (df["starting_time"] < begin_time) &
        (df["starting_time"] + df["execution_time"] > begin_time)]

    # return dataframe sorted without starting_time column and a proper index
    return {
        "workload": to_export.sort_values(by="jobID").reset_index(drop=True),
        "queue": queued_jobs.sort_values(by="jobID").reset_index(drop=True),
        "running": running_jobs.sort_values(by="jobID").reset_index(drop=True)}
