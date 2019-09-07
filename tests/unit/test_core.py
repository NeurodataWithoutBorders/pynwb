from datetime import datetime

import numpy as np
import pandas as pd
from pandas.util.testing import assert_frame_equal
import unittest2 as unittest
from dateutil.tz import tzlocal
from pynwb import NWBFile, TimeSeries, available_namespaces
from pynwb.core import NWBTable, LabelledDict


class TestPrint(unittest.TestCase):

    def test_print_file(self):
        nwbfile = NWBFile(session_description='session_description',
                          identifier='identifier', session_start_time=datetime.now(tzlocal()))
        ts = TimeSeries('name', [1., 2., 3.] * 1000, timestamps=[1, 2, 3])
        ts2 = TimeSeries('name2', [1, 2, 3] * 1000, timestamps=[1, 2, 3])
        expected = """name pynwb.base.TimeSeries at 0x%d
Fields:
  comments: no comments
  conversion: 1.0
  data: [1. 2. 3. ... 1. 2. 3.]
  description: no description
  interval: 1
  resolution: -1.0
  timestamps: [1 2 3]
  timestamps_unit: seconds
"""
        expected %= id(ts)
        self.assertEqual(str(ts), expected)
        nwbfile.add_acquisition(ts)
        nwbfile.add_acquisition(ts2)
        nwbfile.add_epoch(start_time=1.0, stop_time=10.0, tags=['tag1', 'tag2'])
        expected_re = r"""root pynwb\.file\.NWBFile at 0x\d+
Fields:
  acquisition: {
    name <class 'pynwb\.base\.TimeSeries'>,
    name2 <class 'pynwb\.base\.TimeSeries'>
  }
  epoch_tags: {
    tag1,
    tag2
  }
  epochs: epochs <class 'pynwb.epoch.TimeIntervals'>
  file_create_date: \[datetime.datetime\(.*\)\]
  identifier: identifier
  session_description: session_description
  session_start_time: .*
  timestamps_reference_time: .*
"""
        self.assertRegex(str(nwbfile), expected_re)


class TestAvailableNamespaces(unittest.TestCase):
    def test_available_namespaces(self):
        self.assertEqual(available_namespaces(), ('hdmf-common', 'core'))


class TestLabelledDict(unittest.TestCase):

    def setUp(self):
        self.name = 'name'
        self.container = TimeSeries(self.name, [1., 2., 3.] * 1000, timestamps=[1, 2, 3])
        self.object_id = self.container.object_id

    def test_add_default(self):
        ld = LabelledDict('test_dict')
        ld.add(self.container)
        self.assertIs(ld[self.name], self.container)

    def test_add_nondefault(self):
        ld = LabelledDict('test_dict', def_key_name='object_id')
        ld.add(self.container)
        self.assertIs(ld[self.object_id], self.container)
