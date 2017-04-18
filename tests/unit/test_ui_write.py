import unittest
import numpy as np
import json

from pynwb.io.build.builders import GroupBuilder, DatasetBuilder
from pynwb.io import BuildManager
from pynwb import TimeSeries

class SetEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, set) or isinstance(o, frozenset):
            return list(o)
        else:
            return json.JSONEncoder.default(self, o)

class TestBuildTimeSeries(unittest.TestCase):


    def setUp(self):
        self.manager = BuildManager()

    def test_build_base_timeseries(self):
        ts = TimeSeries('test_timeseries', 'example_source', list(range(100,200,10)), 'SIunit', timestamps=list(range(10)), resolution=0.1)
        expected = GroupBuilder('test_timeseries',
                                attributes={'ancestry': 'TimeSeries',
                                            'source': 'example_source',
                                            'neurodata_type': 'TimeSeries',
                                            'help': 'General purpose TimeSeries'},
                                datasets={'data': DatasetBuilder('data', list(range(100,200,10)),
                                                                 attributes={'unit': 'SIunit',
                                                                             'conversion': 1.0,
                                                                             'resolution': 0.1}),
                                          'timestamps': DatasetBuilder('timestamps', list(range(10)),
                                                                 attributes={'unit': 'Seconds', 'interval': 1})})
        result = self.manager.build(ts)
        #print(json.dumps(result, indent=2, cls=SetEncoder))
        #print(json.dumps(expected, indent=2, cls=SetEncoder))
        self.assertDictEqual(result, expected)


