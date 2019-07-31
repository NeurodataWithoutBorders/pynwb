from pynwb.core import ScratchData

from pynwb import NWBFile, NWBHDF5IO

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
        filename = 'test_scratch_%s.nwb' % case
        description = 'a file to test writing and reading a scratch data of type %s' % case
        identifier = 'TEST_scratch_%s' % case
        nwbfile = NWBFile(description, identifier, self.start_time, file_create_date=self.create_date)
        nwbfile.add_scratch(data, name='foo', notes='test scratch')

        writer = NWBHDF5IO(filename, mode='w')
        writer.write(nwbfile)
        writer.close()
        reader = NWBHDF5IO(filename, mode='r')
        read_nwbfile = reader.read()

        ret = read_nwbfile.get_scratch('foo')
        reader.close()
        return ret

    def test_scratch_convert_list(self):
        data = [1, 2, 3, 4]
        ret = self.roundtripScratch(data, 'list')
        assert_array_equal(data, ret)

    def test_scratch_convert_ndarray(self):
        data = np.array([1, 2, 3, 4])
        ret = self.roundtripScratch(data, 'ndarray')
        assert_array_equal(data, ret)

    def test_scratch_convert_DataFrame(self):
        data = pd.DataFrame(data={'col1': [1, 2, 3, 4], 'col2': ['a', 'b', 'c', 'd']})
        ret = self.roundtripScratch(data, 'DataFrame')
        assert_array_equal(data.values, ret.values)
        assert_array_equal(data.index.values, ret.index.values)
