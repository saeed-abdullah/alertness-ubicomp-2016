# -*- coding: utf-8 -*-

"""
    alertness.test.pvt_test
    ~~~~~~~~~~~~~~~~~~~~~~~

    Unit testing for pvt module.

    :copyright: (c) 2016 by Saeed Abdullah.
"""

from alertness import pvt
from functools import partial
import numpy as np
import pandas as pd
import unittest


class PvtTest(unittest.TestCase):

    def test_outlier_filtering(self):
            l = [11171.0, 119425.0, 270.5, 250.0, 258.5]
            df = pd.DataFrame(l, columns=["x"])
            filtering_f = partial(pvt.sd_based_outlier_filtering,
                                  factor=1.2)
            df2 = pvt.outlier_filtering(df, filtering_col="x",
                                        filtering_f=filtering_f,
                                        is_recursive=True)
            expected = sorted(l)[:-2]
            self.assertEquals(len(df2), len(expected))
            self.assertEquals(expected[0], df2.x.min())
            self.assertEquals(expected[-1], df2.x.max())

            filtering_f = partial(pvt.sd_based_outlier_filtering,
                                  factor=2)
            df2 = pvt.outlier_filtering(df, filtering_col="x",
                                        filtering_f=filtering_f,
                                        is_recursive=True)

            self.assertEquals(len(df2), len(l))
            self.assertEquals(np.min(l), df2.x.min())
            self.assertEquals(np.max(l), df2.x.max())

            filtering_f = lambda z: z <= 250.0
            df2 = pvt.outlier_filtering(df, filtering_col="x",
                                        filtering_f=filtering_f,
                                        is_recursive=True)

            self.assertEquals(len(df2), 1)
            self.assertEquals(df2.x.min(), 250.0)

    def _assert_dataframe_equality(self, df1, df2, float_cols):
        """
        Checks for equality between two dataframes.

        For columns containing float values, it uses
        `np.isclose`.

        Parameters
        ----------
        df1 : DataFrame
            First data frame.
        df2 : DataFrame
            Second data frame

        float_cols : iterables
            Columns with float values
        """

        self.assertTrue(np.all(df1.columns == df2.columns))

        for c in df1.columns:
            if c in float_cols:
                self.assertTrue(np.allclose(df1[c], df2[c]))
            else:
                self.assertTrue(np.all(df1[c] == df2[c]))

    def test_get_pvt_score_per_session(self):
        l = [{'response_time': 10, 'user_id': 1, 'session': 1},
             {'response_time': 20, 'user_id': 1, 'session': 1},
             {'response_time': 25, 'user_id': 1, 'session': 1},
             {'response_time': 40, 'user_id': 1, 'session': 2},
             {'response_time': 60, 'user_id': 2, 'session': 100}]

        df = pd.DataFrame(l)

        # median
        e = [{'response_time': 20, 'user_id': 1, 'session': 1},
             {'response_time': 40, 'user_id': 1, 'session': 2},
             {'response_time': 60, 'user_id': 2, 'session': 100}]

        actual = pvt.get_pvt_score_per_session(df)
        expected = pd.DataFrame(e)
        self._assert_dataframe_equality(actual, expected,
                                        float_cols=['response_time'])

        # mean
        e = [{'response_time': 18.3333, 'user_id': 1, 'session': 1},
             {'response_time': 40, 'user_id': 1, 'session': 2},
             {'response_time': 60, 'user_id': 2, 'session': 100}]

        actual = pvt.get_pvt_score_per_session(df, scoring_f='mean')
        expected = pd.DataFrame(e)
        self._assert_dataframe_equality(actual, expected,
                                        float_cols=['response_time'])
