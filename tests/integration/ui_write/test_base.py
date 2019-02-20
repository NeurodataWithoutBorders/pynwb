import numpy as np
import datetime as datetime
import numpy.testing

from pynwb.form.build import GroupBuilder, DatasetBuilder

from pynwb import TimeSeries, NWBFile, NWBHDF5IO

from . import base


class TestTimeSeriesIO(base.TestDataInterfaceIO):

    def setUpContainer(self):
        return TimeSeries('test_timeseries', list(range(100, 200, 10)),
                          'SIunit', timestamps=list(range(10)), resolution=0.1)

    def setUpBuilder(self):
        return GroupBuilder('test_timeseries',
                            attributes={'namespace': base.CORE_NAMESPACE,
                                        'neurodata_type': 'TimeSeries',
                                        'description': 'no description',
                                        'comments': 'no comments',
                                        'help': 'General time series object'},
                            datasets={'data': DatasetBuilder('data', list(range(100, 200, 10)),
                                                             attributes={'unit': 'SIunit',
                                                                         'conversion': 1.0,
                                                                         'resolution': 0.1}),
                                      'timestamps': DatasetBuilder('timestamps', list(range(10)),
                                                                   attributes={'unit': 'Seconds', 'interval': 1})})

    def addContainer(self, nwbfile):
        ''' Should take an NWBFile object and add the container to it '''
        nwbfile.add_acquisition(self.container)

    def getContainer(self, nwbfile):
        ''' Should take an NWBFile object and return the Container'''
        return nwbfile.get_acquisition(self.container.name)

    def test_timestamps_linking(self):
        ''' Test that timestamps get linked to in TimeSeries '''
        path = 'test_timestamps_linking.nwb'
        tsa = TimeSeries(name='a', data=np.linspace(0, 1, 1000), timestamps=np.arange(1000), unit='m')
        tsb = TimeSeries(name='b', data=np.linspace(0, 1, 1000), timestamps=tsa, unit='m')
        nwbfile = NWBFile(identifier='foo', session_start_time=datetime.datetime.now(), session_description='bar')
        nwbfile.add_acquisition(tsa)
        nwbfile.add_acquisition(tsb)
        io = NWBHDF5IO(path, 'w')
        io.write(nwbfile)
        io.close()
        io = NWBHDF5IO(path, 'r')
        nwbfile = io.read()
        tsa = nwbfile.acquisition['a']
        tsb = nwbfile.acquisition['b']
        self.assertIs(tsa.timestamps, tsb.timestamps)

    def test_align_by_trials(self):
        nwbfile = NWBFile(identifier='foo', session_start_time=datetime.datetime.now(), session_description='bar')
        nwbfile.add_trial(start_time=5., stop_time=10.)
        nwbfile.add_trial(start_time=15., stop_time=20.)
        ts = TimeSeries(name='a', data=np.arange(1000), timestamps=np.arange(1000), unit='m')
        nwbfile.add_acquisition(ts)
        numpy.testing.assert_equal(ts.align_by_trials(), [[6, 7, 8, 9, 10], [16, 17, 18, 19, 20]])
