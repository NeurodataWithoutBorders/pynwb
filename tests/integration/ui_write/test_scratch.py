from pynwb.core import DynamicTable, ScratchData
import pynwb

from . import base

import pandas as pd
from pandas.testing import assert_frame_equal
import numpy as np
from numpy.testing import assert_array_equal


class TestScratchData(base.TestMapRoundTrip):

    def setUpContainer(self):
        # this will get ignored
        return ScratchData('foo', [1, 2, 3, 4], notes='test scratch')

    def addContainer(self, nwbfile):
        nwbfile.add_scratch(self.container)

    def getContainer(self, nwbfile):
        return nwbfile.get_scratch('foo')

    def roundtripScratch(self, data, case):
        filename = 'test_scratch_%s.nwb' % case
        description = 'a file to test writing and reading a scratch data of type %s' % case
        identifier = 'TEST_scratch_%s' % case
        nwbfile = NWBFile(description, identifier, self.start_time, file_create_date=self.create_date)
        nwbfile.add_scratch('foo', , notes='test scratch')

        writer = HDF5IO(filename, manager=get_manager(), mode='w')
        writer.write(nwbfile, cache_spec=cache_spec)
        writer.close()
        reader = HDF5IO(filename, manager=get_manager(), mode='r')
        read_nwbfile = reader.read()

        ret = read_nwbfile.get_scratch('foo')
        reader.close()
        return ret

    def test_scratch_convert_list(self):
        data = [1,2,3,4]
        ret = self.roundtripScratch(data, 'list')
        self.assertListEqual(data, ret)

    def test_scratch_convert_ndarray(self):
        data = np.array([1,2,3,4])
        ret = self.roundtripScratch(data, 'ndarray')
        assert_array_equal(data, ret)

    def test_scratch_convert_DataFrame(self):
        data = pd.DataFrame(data={'col1':[1,2,3,4], 'col2':['a', 'b', 'c', 'd']})
        ret = self.roundtripScratch(data, 'DataFrame')
        assert_frame_equal(data, ret)
