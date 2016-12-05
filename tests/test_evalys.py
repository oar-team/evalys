#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

test_evalys
----------------------------------

Tests for `evalys` module.
"""

import unittest

from evalys import evalys


class TestEvalys(unittest.TestCase):

    @classmethod
    def setup_class(cls):
        pass

    def test_jobset_import_export(self):
        from evalys.jobset import JobSet
        js = JobSet.from_csv("./examples/jobs.csv")
        js.to_csv("/tmp/jobs.csv")
        js0 = JobSet.from_csv("/tmp/jobs.csv")
        assert js.df.equals(js0.df)

    def test_fragmentation(self):
        js_vh = evalys.JobSet.from_csv("./tests/test_frag_very_high.csv")
        very_high_frag = js_vh.fragmentation(end_time=500).mean()
        assert very_high_frag >= 0.90

        js_h = evalys.JobSet.from_csv("./tests/test_frag_high.csv")
        high_frag = js_h.fragmentation(end_time=500).mean()
        assert high_frag >= 0.80
        assert high_frag < very_high_frag

        js_l = evalys.JobSet.from_csv("./tests/test_frag_lower.csv")
        lower_frag = js_l.fragmentation(end_time=500).mean()
        assert lower_frag < high_frag

        js_end = evalys.JobSet.from_csv("./tests/test_frag_end.csv")
        end_frag = js_end.fragmentation(end_time=500).mean()
        assert end_frag == 0.0

        js_begin = evalys.JobSet.from_csv("./tests/test_frag_begin.csv")
        begin_frag = js_begin.fragmentation(end_time=500).mean()
        assert begin_frag == 0.0

        js_small_gaps = evalys.JobSet.from_csv(
            "./tests/test_frag_small_gaps.csv")
        assert js_small_gaps.fragmentation(end_time=500).mean() < 0.1

        # test empty resources
        assert js_begin.fragmentation(begin_time=260).mean() == 0

        # test only one resources
        assert js_end.fragmentation(begin_time=60, end_time=260).mean() == 0

    def test_utilisation(self):
        js = evalys.JobSet.from_csv("./tests/test_frag_very_high.csv")
        util = js.mean_utilisation(begin_time=200, end_time=250)
        assert util == 0.7
        util = js.mean_utilisation(begin_time=200, end_time=235)
        assert util == 1
        util = js.mean_utilisation(begin_time=235, end_time=250)
        assert util == 0
        # Test when no event at begin or end
        util = js.mean_utilisation(begin_time=210, end_time=260)
        assert util == 0.7

    def test_cumulative_waiting_time(self):
        from evalys.metrics import cumulative_waiting_time
        js_begin = evalys.JobSet.from_csv("./tests/test_frag_begin.csv")
        assert cumulative_waiting_time(js_begin.df).max() == 62.5 + 125.0 + 187.5

    @classmethod
    def teardown_class(cls):
        pass
