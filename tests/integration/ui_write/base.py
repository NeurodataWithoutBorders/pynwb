import unittest2 as unittest
from datetime import datetime
from dateutil.tz import tzlocal, tzutc
import os
import numpy as np

from pynwb import NWBContainer, get_manager, NWBFile, NWBData
from pynwb.form.backends.hdf5 import HDF5IO

CORE_NAMESPACE = 'core'

container_tests = dict()


def container_test(container):
    global container_tests

    def _dec(cls):
        container_tests[container] = cls
        return cls
    return _dec


class TestMapNWBContainer(unittest.TestCase):

    _required_tests = ('test_build', 'test_construct')

    def setUp(self):
        self.__manager = get_manager()
        self.container = self.setUpContainer()

    @property
    def required_tests(self):
        return self._required_tests

    @property
    def manager(self):
        return self.__manager

    def test_build(self):
        try:
            self.builder = self.setUpBuilder()
        except unittest.SkipTest:
            raise unittest.SkipTest("cannot run construct test for %s -- setUpBuilder not implemented" %
                                    self.__class__.__name__)
        self.maxDiff = None
        result = self.manager.build(self.container)
        # do something here to validate the result Builder against the spec
        self.assertDictEqual(result, self.builder)

    def test_construct(self):
        try:
            self.builder = self.setUpBuilder()
        except unittest.SkipTest:
            raise unittest.SkipTest("cannot run construct test for %s -- setUpBuilder not implemented" %
                                    self.__class__.__name__)
        result = self.manager.construct(self.builder)
        self.assertContainerEqual(result, self.container)

    def setUpBuilder(self):
        ''' Should return the Builder that represents the Container'''
        raise unittest.SkipTest('Cannot run test unless setUpBuilder is implemented')

    def setUpContainer(self):
        ''' Should return the Container to build and read/write'''
        raise unittest.SkipTest('Cannot run test unless setUpContainer is implemented')

    def assertContainerEqual(self, container1, container2):           # noqa: C901
        '''
        container1 is what was read or generated
        container2 is what is hardcoded in the TestCase
        '''
        type1 = type(container1)
        type2 = type(container2)
        self.assertEqual(type1, type2)
        for nwbfield in container1.__nwbfields__:
            with self.subTest(nwbfield=nwbfield, container_type=type1.__name__):
                f1 = getattr(container1, nwbfield)
                f2 = getattr(container2, nwbfield)
                if isinstance(f1, (tuple, list, np.ndarray)):
                    if len(f1) > 0:
                        if isinstance(f1[0], NWBContainer):
                            for sub1, sub2 in zip(f1, f2):
                                self.assertContainerEqual(sub1, sub2)
                        elif isinstance(f1[0], NWBData):
                            for sub1, sub2 in zip(f1, f2):
                                self.assertDataEqual(sub1, sub2)
                        continue
                    else:
                        self.assertEqual(len(f1), len(f2))
                        if len(f1) == 0:
                            continue
                        if isinstance(f1[0], float):
                                for v1, v2 in zip(f1, f2):
                                    self.assertAlmostEqual(v1, v2, places=6)
                        else:
                            self.assertTrue(np.array_equal(f1, f2))
                elif isinstance(f1, dict) and len(f1) and isinstance(next(iter(f1.values())), NWBContainer):
                    f1_keys = set(f1.keys())
                    f2_keys = set(f2.keys())
                    self.assertSetEqual(f1_keys, f2_keys)
                    for k in f1_keys:
                        with self.subTest(module_name=k):
                            self.assertContainerEqual(f1[k], f2[k])
                elif isinstance(f1, NWBContainer):
                    self.assertContainerEqual(f1, f2)
                elif isinstance(f1, NWBData) or isinstance(f2, NWBData):
                    if isinstance(f1, NWBData) and isinstance(f2, NWBData):
                        self.assertDataEqual(f1, f2)
                    elif isinstance(f1, NWBData):
                        self.assertTrue(np.array_equal(f1.data, f2))
                    elif isinstance(f2, NWBData):
                        self.assertTrue(np.array_equal(f1.data, f2))
                else:
                    if isinstance(f1, float):
                        self.assertAlmostEqual(f1, f2)
                    else:
                        self.assertEqual(f1, f2)

    def assertDataEqual(self, data1, data2):
        self.assertEqual(type(data1), type(data2))
        self.assertEqual(len(data1), len(data2))


class TestMapRoundTrip(TestMapNWBContainer):

    _required_tests = ('test_build', 'test_construct', 'test_roundtrip')
    run_injected_file_test = False

    def setUp(self):
        super(TestMapRoundTrip, self).setUp()
        self.container = self.setUpContainer()
        self.start_time = datetime(1971, 1, 1, 12, tzinfo=tzutc())
        self.create_date = datetime(2018, 4, 15, 12, tzinfo=tzlocal())
        self.container_type = self.container.__class__.__name__
        self.filename = 'test_%s.nwb' % self.container_type
        self.writer = None
        self.reader = None

    def tearDown(self):
        if self.writer is not None:
            self.writer.close()
        if self.reader is not None:
            self.reader.close()
        if os.path.exists(self.filename) and os.getenv("CLEAN_NWB", '1') not in ('0', 'false', 'FALSE', 'False'):
            os.remove(self.filename)

    def roundtripContainer(self):
        description = 'a file to test writing and reading a %s' % self.container_type
        identifier = 'TEST_%s' % self.container_type
        nwbfile = NWBFile(description, identifier, self.start_time, file_create_date=self.create_date)
        self.addContainer(nwbfile)

        self.writer = HDF5IO(self.filename, get_manager(), mode='w')
        self.writer.write(nwbfile)
        self.writer.close()
        self.reader = HDF5IO(self.filename, get_manager(), mode='r')
        read_nwbfile = self.reader.read()

        try:
            tmp = self.getContainer(read_nwbfile)
            return tmp
        except Exception as e:
            self.reader.close()
            self.reader = None
            raise e

    def test_roundtrip(self):
        self.read_container = self.roundtripContainer()
        # make sure we get a completely new object
        str(self.container)  # added as a test to make sure printing works
        self.assertNotEqual(id(self.container), id(self.read_container))
        self.assertContainerEqual(self.container, self.read_container)

    def addContainer(self, nwbfile):
        ''' Should take an NWBFile object and add the container to it '''
        raise unittest.SkipTest('Cannot run test unless addContainer is implemented')

    def getContainer(self, nwbfile):
        ''' Should take an NWBFile object and return the Container'''
        raise unittest.SkipTest('Cannot run test unless getContainer is implemented')


class TestDataInterfaceIO(TestMapRoundTrip):

    def addContainer(self, nwbfile):
        ''' Should take an NWBFile object and add the container to it '''
        nwbfile.add_acquisition(self.container)

    def getContainer(self, nwbfile):
        ''' Should take an NWBFile object and return the Container'''
        return nwbfile.get_acquisition(self.container.name)
