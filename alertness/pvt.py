# -*- coding: utf-8 -*-

"""
    alertness.pvt
    ~~~~~~~~~~~~~

    Calculates alertness from Psychomotor Vigilance Test (PVT)

    :copyright: (c) 2016 by Saeed Abdullah.
"""

import functools
import numpy as np
import pandas as pd


def sd_based_outlier_filtering(col, factor=2.5):
    """
    Performs SD based outlier filtering.

    It uses mean ± factor * SD as the threshold window. Any values
    outside of the window is considered as outlier.

    To use with different window size in outlier_filtering,
    `functools.partial` might be useful.

    Parameters
    ---------
    col : Series
        Filtering column

    factor : float
        Threshold window size. Default is 2.5

    Returns
    -------
    Series
        A Boolean Series where False indicates outlier values.
    """

    threshold = col.std() * factor
    min_val, max_val = col.mean() - threshold, col.mean() + threshold
    return col.map(lambda z: min_val < z < max_val)


def outlier_filtering(df, filtering_col,
                      filtering_f,
                      is_recursive=True):
    """
    Filters outlier from the given DataFrame.

    The filtering function takes the column as input and returns
    Boolean value for each row. Only rows with True values
    are retained.

    Parameters
    ----------
    df : DataFrame.

    filtering_col : str
        Filtering column name. It should contain comparable values

    filtering_f : function
        Filtering function. This function should take
        the filtering column and return Boolean value
        for each row with `False` values indicating outliers
        that should be discarded.

    is_recursive : bool
        If the filtering should be recursively applied
        until all values are consistent. Default is True.

    Returns
    -------
    DataFrame
        A filtered DataFrame.
    """

    col = df[filtering_col]

    df2 = df[filtering_f(col)]

    if is_recursive:
        # Check if all the values are consistent (no filtering would
        # happen in that case)
        if len(df) == len(df2):
            return df2
        else:
            return outlier_filtering(df2, filtering_col,
                                     filtering_f, is_recursive)
    else:
        return df2


def get_pvt_score_per_session(df, scoring_f='median',
                              response_c='response_time',
                              session_c='session',
                              user_c='user_id'):
        """
        Retrieves PVT score from each individual session.

        Each individual session contains multiple reaction time
        test. This function aggregates these responses (i.e.,
        MRT_s,p as described in the README).

        Parameters
        ----------
        df : DataFrame

        scoring_f : str
            Scoring function used to aggregate response time.
            It can be either 'median' or 'mean'. Default
            is 'median'.

        response_c : str
            Name of column that contains response time of each
            PVT task. Default is `response_time`.

        session_c : str
            Column name in the given data frame that indicates
            id of each session. These values are used to
            group response times a given session. Default is
            `session`.

        user_c : str
            Column name indicating user id. Default is `user_id`.


        Returns
        -------
        DataFrame:
            DataFrame with aggregated value for each session for
            each user.
        """

        l = []

        if scoring_f == 'median':
            func = np.median
        elif scoring_f == 'mean':
            func = np.mean
        else:
            raise ValueError('Unknown function: {0}'.format(scoring_f))

        # First group by user id
        for k, v in df.groupby(user_c):
            # then group by session ids
            for k1, v1 in v.groupby(session_c):
                # aggregated values
                aggr = func(v1[response_c])
                l.append({user_c: k, session_c: k1,
                          response_c: aggr})

        return pd.DataFrame(l)


def get_relative_response_time(df, scoring_f='mean',
                               user_c='user_id',
                               response_c='response_time'):
    """
    Gets performance based on individual baseline.

    This function calculates performance using the following steps:
        1. Groups the row by user id
        2. Apply the given function to calculate individual baseline
        2. Gets the percentage deviation from individual baseline.
           This would give us performance measurement — positive means
           better performance and negative means worse.

    Parameters
    ---------

    df : DataFrame

    scoring_f : str
        Scoring function to be used. Options are 'mean' and 'median'.
        Default is 'mean'.

    user_c : str
        Name of column with user id as values.

    response_c : str
        Name of column with aggregated response time over each session.
        In other words, these values are returned from
        `get_pvt_score_per_session`.

    Returns
    -------
    Series
        Relative response time (RRT) values indicating alertness.
    """
    if scoring_f == 'mean':
        func = np.mean
    elif scoring_f == 'median':
        func = np.median
    else:
        raise ValueError('Unknown function: {0}'.format(scoring_f))

    g = df[response_c].groupby(df[user_c])

    # percentage deviation from baseline
    return g.apply(lambda x: 100 * (func(x) - x)/func(x))


def process_pvt(df, response_c='response_time',
                user_c='user_id',
                filtering_factor=2.5,
                session_f='median',
                baseline_f='mean'):
    """
    Computes alertness score from raw PVT score.

    This function:
        1. Establish the performance in a given session
           using session_f
        2. If filtering_factor is provided, filters outliers
           for each individual using threshold mean ± filtering_factor * SD.
        2. For each individual, it establish baseline
           from session scores using baseline_f.
        3. Then, it computes performance as the deviation
           from individual baseline.

    Parameters
    ---------
    df : DataFrame

    response_c : str
        Column name that contains response values from reaction
        time test.

    user_c : str
        Name of column containing user ids.

    filtering_factor: float
        Window range to determine outliers. If not `None`,
        then responses outside mean ± filtering_factor * SD
        for each individual will be removed.

    session_f : str
        Function to aggregate response time over a single
        session. Options are 'mean' and 'median'. Default
        is 'median'.

    baseline_f : str
        Function establish individual baseline. Options are
        'mean' and 'median'. Default is 'mean'.


    Returns
    ------
    r : DataFrame
        The column 'rrt' contains relative response time indicating
        alertness.
    """
    # remove early start
    df = df[df[response_c] > 0]

    pvt = get_pvt_score_per_session(df, scoring_f=session_f)

    if filtering_factor is not None:
        # Filtering outliers.
        r = None
        filtering_f = functools.partial(sd_based_outlier_filtering,
                                        factor=filtering_factor)
        for k, v in pvt.groupby(user_c):
            t = outlier_filtering(v, filtering_col=response_c,
                                  filtering_f=filtering_f)
            r = pd.concat([r, t])
    else:
        r = pvt

    # get performance
    r['rrt'] = get_relative_response_time(r, scoring_f=baseline_f)

    return r
