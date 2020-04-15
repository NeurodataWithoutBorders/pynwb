import numpy as np
from datetime import datetime
from dateutil.tz import tzlocal

from pynwb import TimeSeries, NWBFile, NWBHDF5IO
from pynwb.testing import AcquisitionH5IOMixin, TestCase, remove_test_file


class TestTimeSeriesIO(AcquisitionH5IOMixin, TestCase):

    def setUpContainer(self):
        """ Return the test TimeSeries to read/write """
        return TimeSeries(
            name='test_timeseries',
            data=list(range(1000)),
            unit='SIunit',
            timestamps=np.arange(1000.),
            resolution=0.1
        )


class TestTimeSeriesLinking(TestCase):

    def setUp(self):
        self.path = 'test_timestamps_linking.nwb'

    def tearDown(self):
        remove_test_file(self.path)

    def test_timestamps_linking(self):
        ''' Test that timestamps get linked to in TimeSeries '''
        tsa = TimeSeries(name='a', data=np.linspace(0, 1, 1000), timestamps=np.arange(1000.), unit='m')
        tsb = TimeSeries(name='b', data=np.linspace(0, 1, 1000), timestamps=tsa, unit='m')
        nwbfile = NWBFile(identifier='foo',
                          session_start_time=datetime(2017, 5, 1, 12, 0, 0, tzinfo=tzlocal()),
                          session_description='bar')
        nwbfile.add_acquisition(tsa)
        nwbfile.add_acquisition(tsb)
        with NWBHDF5IO(self.path, 'w') as io:
            io.write(nwbfile)
        with NWBHDF5IO(self.path, 'r') as io:
            nwbfile = io.read()
        tsa = nwbfile.acquisition['a']
        tsb = nwbfile.acquisition['b']
        self.assertIs(tsa.timestamps, tsb.timestamps)
