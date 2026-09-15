import pandas as pd
import numpy as np
from numpy.testing import assert_array_equal

from pynwb import NWBFile, NWBHDF5IO, TimeSeries
from pynwb.core import ScratchData
from pynwb.testing import NWBH5IOMixin, TestCase


class TestScratchDataIO(NWBH5IOMixin, TestCase):

    def setUpContainer(self):
        """ Return the test ScratchData to read/write """
        return ScratchData(name='foo', data=[1, 2, 3, 4], description='test scratch')

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
        nwbfile.add_scratch(data, name='foo', **kwargs)

        self.writer = NWBHDF5IO(self.filename, mode='w')
        self.writer.write(nwbfile)
        self.writer.close()

        self.reader = NWBHDF5IO(self.filename, mode='r')
        self.read_nwbfile = self.reader.read()
        return self.read_nwbfile.get_scratch('foo')

    def test_scratch_convert_int(self):
        data = 2
        ret = self.roundtrip_scratch(data, 'int', description='test scratch')
        self.assertEqual(data, ret)
        self.validate()

    def test_scratch_convert_list(self):
        data = [1, 2, 3, 4]
        ret = self.roundtrip_scratch(data, 'list', description='test scratch')
        assert_array_equal(data, ret)
        self.validate()

    def test_scratch_convert_ndarray(self):
        data = np.array([1, 2, 3, 4])
        ret = self.roundtrip_scratch(data, 'ndarray', description='test scratch')
        assert_array_equal(data, ret)
        self.validate()

    def test_scratch_convert_DataFrame_table_desc(self):
        """Test round trip convert of DataFrame with a table description"""
        data = pd.DataFrame(data={'col1': [1, 2, 3, 4], 'col2': ['a', 'b', 'c', 'd']})
        self.roundtrip_scratch(data, 'DataFrame', description='my_table')
        ret = self.read_nwbfile.get_scratch('foo', convert=False)
        ret_df = ret.to_dataframe()
        self.assertEqual(ret.description, 'my_table')
        assert_array_equal(data.values, ret_df.values)
        assert_array_equal(data.index.values, ret_df.index.values)
        self.validate()

    def test_scratch_container(self):
        data = TimeSeries(
            name='test_ts',
            data=[1, 2, 3, 4, 5],
            unit='unit',
            timestamps=[1.1, 1.2, 1.3, 1.4, 1.5]
        )
        nwbfile = NWBFile(
            session_description='test',
            identifier='test',
            session_start_time=self.start_time,
            file_create_date=self.create_date
        )
        nwbfile.add_scratch(data)

        self.writer = NWBHDF5IO(self.filename, mode='w')
        self.writer.write(nwbfile)
        self.writer.close()

        self.reader = NWBHDF5IO(self.filename, mode='r')
        self.read_nwbfile = self.reader.read()
        ret = self.read_nwbfile.get_scratch('test_ts')

        self.assertContainerEqual(data, ret)
        self.validate()
