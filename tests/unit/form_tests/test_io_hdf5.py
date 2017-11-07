import unittest
from datetime import datetime
import os
from h5py import File, Dataset
from six import text_type

from pynwb.form.backends.hdf5 import HDF5IO
from pynwb.form.build import GroupBuilder, DatasetBuilder, LinkBuilder, BuildManager, TypeMap
from pynwb.form.spec import NamespaceCatalog

from numbers import Number

import json
import numpy as np


class HDF5Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Dataset):
            ret = None
            for t in (list, str):
                try:
                    ret = t(obj)
                    break
                except:  # noqa: F722
                    pass
            if ret is None:
                return obj
            else:
                return ret
        elif isinstance(obj, np.int64):
            return int(obj)
        elif isinstance(obj, bytes):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


class GroupBuilderTestCase(unittest.TestCase):
    '''
    A TestCase class for comparing GroupBuilders.
    '''

    def __is_scalar(self, obj):
        if hasattr(obj, 'shape'):
            return len(obj.shape) == 0
        else:
            if any(isinstance(obj, t) for t in (int, str, float, bytes, text_type)):
                return True
        return False

    def __convert_h5_scalar(self, obj):
        if isinstance(obj, Dataset):
            return obj[...]
        return obj

    def __compare_attr_dicts(self, a, b):
        reasons = list()
        b_keys = set(b.keys())
        for k in a:
            if k not in b:
                reasons.append("'%s' attribute missing from second dataset" % k)
            else:
                if a[k] != b[k]:
                    reasons.append("'%s' attribute on datasets not equal" % k)
                b_keys.remove(k)
        for k in b_keys:
            reasons.append("'%s' attribute missing from first dataset" % k)
        return reasons

    def __compare_dataset(self, a, b):
        reasons = self.__compare_attr_dicts(a.attributes, b.attributes)
        if not self.__compare_data(a.data, b.data):
            reasons.append("dataset '%s' not equal" % a.name)
        return reasons

    def __compare_data(self, a, b):
        if isinstance(a, Number) and isinstance(b, Number):
            return a == b
        elif isinstance(a, Number) != isinstance(b, Number):
            return False
        else:
            a_scalar = self.__is_scalar(a)
            b_scalar = self.__is_scalar(b)
            if a_scalar and b_scalar:
                return self.__convert_h5_scalar(a_scalar) == self.__convert_h5_scalar(b_scalar)
            elif a_scalar != b_scalar:
                return False
            if len(a) == len(b):
                for i in range(len(a)):
                    if not self.__compare_data(a[i], b[i]):
                        return False
            else:
                return False
        return True

    def __fmt(self, val):
        return "%s (%s)" % (val, type(val))

    def __assert_helper(self, a, b):
        reasons = list()
        b_keys = set(b.keys())
        for k, a_sub in a.items():
            if k in b:
                b_sub = b[k]
                b_keys.remove(k)
                if isinstance(a_sub, LinkBuilder) and isinstance(a_sub, LinkBuilder):
                    a_sub = a_sub['target']
                    b_sub = b_sub['target']
                elif isinstance(a_sub, LinkBuilder) != isinstance(a_sub, LinkBuilder):
                    reasons.append('%s != %s' % (a_sub, b_sub))
                if isinstance(a_sub, DatasetBuilder) and isinstance(a_sub, DatasetBuilder):
                    # if not self.__compare_dataset(a_sub, b_sub):
                    #    reasons.append('%s != %s' % (a_sub, b_sub))
                    reasons.extend(self.__compare_dataset(a_sub, b_sub))
                elif isinstance(a_sub, GroupBuilder) and isinstance(a_sub, GroupBuilder):
                    reasons.extend(self.__assert_helper(a_sub, b_sub))
                else:
                    if a_sub != b_sub:
                        reasons.append('%s != %s' % (self.__fmt(a_sub), self.__fmt(b_sub)))
            else:
                reasons.append("'%s' not in both" % k)
        for k in b_keys:
            reasons.append("'%s' not in both" % k)
        return reasons

    def assertBuilderEqual(self, a, b):
        ''' Tests that two GroupBuilders are equal '''
        reasons = self.__assert_helper(a, b)
        if len(reasons):
            raise AssertionError(', '.join(reasons))
        return True


class TestHDF5Writer(GroupBuilderTestCase):

    def setUp(self):
        self.manager = BuildManager(TypeMap(NamespaceCatalog()))
        self.path = "test_pynwb_io_hdf5.h5"
        self.start_time = datetime(1970, 1, 1, 12, 0, 0)
        self.create_date = datetime(2017, 4, 15, 12, 0, 0)

        ts_builder = GroupBuilder('test_timeseries',
                                  attributes={'ancestry': 'TimeSeries',
                                              'source': 'example_source',
                                              'neurodata_type': 'TimeSeries',
                                              'help': 'General purpose TimeSeries'},
                                  datasets={'data': DatasetBuilder('data', list(range(100, 200, 10)),
                                                                   attributes={'unit': 'SIunit',
                                                                               'conversion': 1.0,
                                                                               'resolution': 0.1}),
                                            'timestamps': DatasetBuilder(
                                                'timestamps', list(range(10)),
                                                attributes={'unit': 'Seconds', 'interval': 1})})
        self.builder = GroupBuilder(
            'root',
            groups={'acquisition':
                    GroupBuilder('acquisition',
                                 groups={'timeseries':
                                         GroupBuilder('timeseries',
                                                      groups={'test_timeseries': ts_builder}),
                                         'images': GroupBuilder('images')}),
                    'analysis': GroupBuilder('analysis'),
                    'epochs': GroupBuilder('epochs'),
                    'general': GroupBuilder('general'),
                    'processing': GroupBuilder('processing'),
                    'stimulus': GroupBuilder(
                        'stimulus',
                        groups={'presentation':
                                GroupBuilder('presentation'),
                                'templates': GroupBuilder('templates')})},
            datasets={'file_create_date': DatasetBuilder('file_create_date', [str(self.create_date)]),
                      'identifier': DatasetBuilder('identifier', 'TEST123'),
                      'session_description': DatasetBuilder('session_description', 'a test NWB File'),
                      'nwb_version': DatasetBuilder('nwb_version', '1.0.6'),
                      'session_start_time': DatasetBuilder('session_start_time', str(self.start_time))},
            attributes={'neurodata_type': 'NWBFile'})

    def tearDown(self):
        if os.path.exists(self.path):
            os.remove(self.path)

    def check_fields(self):
        f = File(self.path)
        self.assertIn('acquisition', f)
        self.assertIn('analysis', f)
        self.assertIn('epochs', f)
        self.assertIn('general', f)
        self.assertIn('processing', f)
        self.assertIn('file_create_date', f)
        self.assertIn('identifier', f)
        self.assertIn('session_description', f)
        self.assertIn('nwb_version', f)
        self.assertIn('session_start_time', f)
        acq = f.get('acquisition')
        self.assertIn('images', acq)
        self.assertIn('timeseries', acq)
        ts = acq.get('timeseries')
        self.assertIn('test_timeseries', ts)

    def test_write_builder(self):
        writer = HDF5IO(self.path, self.manager)
        writer.write_builder(self.builder)
        writer.close()
        self.check_fields()

    def test_write_context_manager(self):
        with HDF5IO(self.path, self.manager) as writer:
            writer.write_builder(self.builder)
        self.check_fields()

    def test_read_builder(self):
        self.maxDiff = None
        io = HDF5IO(self.path, self.manager)
        io.write_builder(self.builder)
        builder = io.read_builder()
        self.assertBuilderEqual(builder, self.builder)
        io.close()
