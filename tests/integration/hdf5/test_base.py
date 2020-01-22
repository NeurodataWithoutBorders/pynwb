import numpy as np
from datetime import datetime
from dateutil.tz import tzlocal

from pynwb import TimeSeries, NWBFile, NWBHDF5IO
from pynwb.testing import AcquisitionH5IOMixin, TestCase


class TestTimeSeriesIO(AcquisitionH5IOMixin, TestCase):

    def setUpContainer(self):
        """ Return the test TimeSeries to read/write """
        return TimeSeries('test_timeseries', list(range(100, 200, 10)),
                          'SIunit', timestamps=list(range(10)), resolution=0.1)


class TestTimeSeriesLinking(TestCase):

    def test_timestamps_linking(self):
        ''' Test that timestamps get linked to in TimeSeries '''
        tsa = TimeSeries(name='a', data=np.linspace(0, 1, 1000), timestamps=np.arange(1000), unit='m')
        tsb = TimeSeries(name='b', data=np.linspace(0, 1, 1000), timestamps=tsa, unit='m')
        nwbfile = NWBFile(identifier='foo',
                          session_start_time=datetime(2017, 5, 1, 12, 0, 0, tzinfo=tzlocal()),
                          session_description='bar')
        nwbfile.add_acquisition(tsa)
        nwbfile.add_acquisition(tsb)
        filename = 'test_timestamps_linking.nwb'
        with NWBHDF5IO(filename, 'w') as io:
            io.write(nwbfile)
        with NWBHDF5IO(filename, 'r') as io:
            nwbfile = io.read()
        tsa = nwbfile.acquisition['a']
        tsb = nwbfile.acquisition['b']
        self.assertIs(tsa.timestamps, tsb.timestamps)
