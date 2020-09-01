import pandas as pd
import numpy as np
from numpy.testing import assert_array_equal

from pynwb import NWBFile, NWBHDF5IO, TimeSeries
from pynwb.core import ScratchData
from pynwb.testing import NWBH5IOMixin, TestCase


class TestScratchDataIO(NWBH5IOMixin, TestCase):

    def setUpContainer(self):
        """ Return the test ScratchData to read/write """
        return ScratchData(name='foo', data=[1, 2, 3, 4], notes='test scratch')

    def addContainer(self, nwbfile):
        """ Add the test ScratchData to the given NWBFile """
        nwbfile.add_scratch(self.container)

    def getContainer(self, nwbfile):
        """ Return the test ScratchData from the given NWBFile """
        return nwbfile.get_scratch('foo', convert=False)

    def roundtrip_scratch(self, data, case, **kwargs):
        self.filename = 'test_scratch_%s.nwb' % case
        description = 'a file to test writing and reading a scratch data of type %s' % case
        identifier = 'TEST_scratch_%s' % case
        nwbfile = NWBFile(session_description=description,
                          identifier=identifier,
                          session_start_time=self.start_time,
                          file_create_date=self.create_date)
        nwbfile.add_scratch(data, name='foo', notes='test scratch', **kwargs)

        self.writer = NWBHDF5IO(self.filename, mode='w')
        self.writer.write(nwbfile)
        self.writer.close()

        self.reader = NWBHDF5IO(self.filename, mode='r')
        self.read_nwbfile = self.reader.read()
        return self.read_nwbfile.get_scratch('foo')

    def test_scratch_convert_list(self):
        data = [1, 2, 3, 4]
        ret = self.roundtrip_scratch(data, 'list')
        assert_array_equal(data, ret)
        self.validate()

    def test_scratch_convert_ndarray(self):
        data = np.array([1, 2, 3, 4])
        ret = self.roundtrip_scratch(data, 'ndarray')
        assert_array_equal(data, ret)
        self.validate()

    def test_scratch_convert_DataFrame(self):
        data = pd.DataFrame(data={'col1': [1, 2, 3, 4], 'col2': ['a', 'b', 'c', 'd']})
        warn_msg = 'Notes argument is ignored when adding a pandas DataFrame to scratch'
        with self.assertWarnsWith(UserWarning, warn_msg):
            ret = self.roundtrip_scratch(data, 'DataFrame')
        assert_array_equal(data.values, ret.values)
        assert_array_equal(data.index.values, ret.index.values)
        self.validate()

    def test_scratch_convert_DataFrame_table_desc(self):
        """Test round trip convert of DataFrame with a table description"""
        data = pd.DataFrame(data={'col1': [1, 2, 3, 4], 'col2': ['a', 'b', 'c', 'd']})

        case = 'dataframe_desc'
        self.filename = 'test_scratch_%s.nwb' % case
        description = 'a file to test writing and reading a scratch data of type %s' % case
        identifier = 'TEST_scratch_%s' % case
        nwbfile = NWBFile(session_description=description,
                          identifier=identifier,
                          session_start_time=self.start_time,
                          file_create_date=self.create_date)
        nwbfile.add_scratch(data, name='foo', table_description='my_table')

        self.writer = NWBHDF5IO(self.filename, mode='w')
        self.writer.write(nwbfile)
        self.writer.close()

        self.reader = NWBHDF5IO(self.filename, mode='r')
        self.read_nwbfile = self.reader.read()

        ret = self.read_nwbfile.get_scratch('foo', convert=False)
        ret_df = ret.to_dataframe()
        self.assertEqual(ret.description, 'my_table')
        assert_array_equal(data.values, ret_df.values)
        assert_array_equal(data.index.values, ret_df.index.values)
        self.validate()

    def _test_scratch_container(self, validate=True, **kwargs):
        data = TimeSeries(name='test_ts', data=[1, 2, 3, 4, 5], unit='unit', timestamps=[1.1, 1.2, 1.3, 1.4, 1.5])
        nwbfile = NWBFile(session_description='test', identifier='test', session_start_time=self.start_time,
                          file_create_date=self.create_date)

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

    def test_scratch_container(self):
        self._test_scratch_container(validate=True)

    def test_scratch_container_with_name(self):
        warn_msg = 'Name argument is ignored when adding an NWBContainer to scratch'
        with self.assertWarnsWith(UserWarning, warn_msg):
            self._test_scratch_container(validate=False, name='foo')

    def test_scratch_container_with_notes(self):
        warn_msg = 'Notes argument is ignored when adding an NWBContainer to scratch'
        with self.assertWarnsWith(UserWarning, warn_msg):
            self._test_scratch_container(validate=False, notes='test scratch')
