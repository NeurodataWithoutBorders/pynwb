from pynwb.form.build import GroupBuilder, DatasetBuilder

from pynwb import TimeSeries

from . import base


@base.container_test(TimeSeries)
class TestTimeSeriesIO(base.TestMapRoundTrip):

    def setUpContainer(self):
        return TimeSeries('test_timeseries', 'example_source', list(range(100, 200, 10)),
                          'SIunit', timestamps=list(range(10)), resolution=0.1)

    def setUpBuilder(self):
        return GroupBuilder('test_timeseries',
                            attributes={'source': 'example_source',
                                        'namespace': base.CORE_NAMESPACE,
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