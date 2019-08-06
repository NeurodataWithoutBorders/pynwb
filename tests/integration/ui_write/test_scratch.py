from pynwb.core import ScratchData
from pynwb import NWBFile, NWBHDF5IO, TimeSeries

from . import base

import pandas as pd
import numpy as np
from numpy.testing import assert_array_equal


class TestScratchData(base.TestMapRoundTrip):

    def setUpContainer(self):
        return ScratchData('foo', [1, 2, 3, 4], notes='test scratch')

    def addContainer(self, nwbfile):
        nwbfile.add_scratch(self.container)

    def getContainer(self, nwbfile):
        return nwbfile.get_scratch('foo', convert=False)

    def roundtripScratch(self, data, case):
        self.filename = 'test_scratch_%s.nwb' % case
        description = 'a file to test writing and reading a scratch data of type %s' % case
        identifier = 'TEST_scratch_%s' % case
        nwbfile = NWBFile(description, identifier, self.start_time, file_create_date=self.create_date)
        nwbfile.add_scratch(data, name='foo', notes='test scratch')

        self.writer = NWBHDF5IO(self.filename, mode='w')
        self.writer.write(nwbfile)
        self.writer.close()

        self.reader = NWBHDF5IO(self.filename, mode='r')
        self.read_nwbfile = self.reader.read()
        return self.read_nwbfile.get_scratch('foo')

    def test_scratch_convert_list(self):
        data = [1, 2, 3, 4]
        ret = self.roundtripScratch(data, 'list')
        assert_array_equal(data, ret)
        self.validate()

    def test_scratch_convert_ndarray(self):
        data = np.array([1, 2, 3, 4])
        ret = self.roundtripScratch(data, 'ndarray')
        assert_array_equal(data, ret)
        self.validate()

    def test_scratch_convert_DataFrame(self):
        data = pd.DataFrame(data={'col1': [1, 2, 3, 4], 'col2': ['a', 'b', 'c', 'd']})
        warn_msg = 'Notes argument is ignored when adding a pandas DataFrame to scratch'
        with self.assertWarnsRegex(UserWarning, warn_msg):
            ret = self.roundtripScratch(data, 'DataFrame')
        assert_array_equal(data.values, ret.values)
        assert_array_equal(data.index.values, ret.index.values)
        self.validate()

    def test_scratch_container(self, validate=True, **kwargs):
        data = TimeSeries('test_ts', [1, 2, 3, 4, 5], unit='unit', timestamps=[1.1, 1.2, 1.3, 1.4, 1.5])
        nwbfile = NWBFile('test', 'test', self.start_time, file_create_date=self.create_date)

        nwbfile.add_scratch(data, **kwargs)

        self.writer = NWBHDF5IO(self.filename, mode='w')
        self.writer.write(nwbfile)
        self.writer.close()

        self.reader = NWBHDF5IO(self.filename, mode='r')
        self.read_nwbfile = self.reader.read()
        ret = self.read_nwbfile.get_scratch('test_ts')

        self.assertContainerEqual(data, ret)
        if validate:
            self.validate()

    def test_scratch_container_with_name(self):
        warn_msg = 'Name argument is ignored when adding an NWBContainer to scratch'
        with self.assertWarnsRegex(UserWarning, warn_msg):
            self.test_scratch_container(validate=False, name='foo')

    def test_scratch_container_with_notes(self):
        warn_msg = 'Notes argument is ignored when adding an NWBContainer to scratch'
        with self.assertWarnsRegex(UserWarning, warn_msg):
            self.test_scratch_container(validate=False, notes='test scratch')
