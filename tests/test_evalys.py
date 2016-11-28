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

    def test_fragmentation(self):
        js_vh = evalys.JobSet.from_csv("./tests/test_frag_very_high.csv")
        assert js_vh.fragmentation().mean() > 0.85

        js_h = evalys.JobSet.from_csv("./tests/test_frag_high.csv")
        assert js_h.fragmentation().mean() > 0.80
        assert js_h.fragmentation().mean() < js_vh.fragmentation().mean()

        js_l = evalys.JobSet.from_csv("./tests/test_frag_lower.csv")
        assert js_l.fragmentation().mean() < 0.80
        assert js_l.fragmentation().mean() < js_h.fragmentation().mean()

    @classmethod
    def teardown_class(cls):
        pass
