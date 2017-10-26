import unittest2 as unittest
from datetime import datetime
import os
import numpy as np

from pynwb import NWBContainer, get_build_manager, NWBFile, NWBData
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

    def setUp(self):
        self.__manager = get_manager()
        self.__container = self.setUpContainer()
        self.__builder = self.setUpBuilder()

    @property
    def manager(self):
        return self.__manager

    @property
    def container(self):
        return self.__container

    @property
    def builder(self):
        return self.__builder

    def test_build(self):
        # raise Exception
        self.maxDiff = None
        result = self.manager.build(self.container)
        # do something here to validate the result Builder against the spec
        self.assertDictEqual(result, self.builder)

    def test_construct(self):
        result = self.manager.construct(self.builder)
        self.assertContainerEqual(result, self.container)

    def setUpBuilder(self):
        ''' Should return the Builder that represents the Container'''
        raise unittest.SkipTest('Cannot run test unless setUpBuilder is implemented')

    def setUpContainer(self):
        ''' Should return the Container to build and read/write'''
        raise unittest.SkipTest('Cannot run test unless setUpContainer is implemented')

    def assertContainerEqual(self, container1, container2):
        type1 = type(container1)
        type2 = type(container2)
        self.assertEqual(type1, type2)
        for nwbfield in container1.__nwbfields__:
            with self.subTest(nwbfield=nwbfield, container_type=type1.__name__):
                f1 = getattr(container1, nwbfield)
                f2 = getattr(container2, nwbfield)
                if isinstance(f1, (tuple, list, np.ndarray)):
                    if len(f1) > 0 and isinstance(f1[0], NWBContainer):
                        for sub1, sub2 in zip(f1,f2):
                            self.assertContainerEqual(sub1, sub2)
                        continue
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
                elif isinstance(f1, NWBData):
                    self.assertDataEqual(f1, f2)
                else:
                    self.assertEqual(f1, f2)

    def assertDataEqual(self, data1, data2):
        self.assertEqual(type(data1), type(data2))
        self.assertEqual(len(data1), len(data2))


class TestMapRoundTrip(TestMapNWBContainer):

    def setUp(self):
        super(TestMapRoundTrip, self).setUp()
        self.start_time = datetime(1971, 1, 1, 12, 0, 0)
        self.create_date = datetime(2018, 4, 15, 12, 0, 0)
        self.container_type = self.container.__class__.__name__
        self.filename = 'test_%s.nwb' % self.container_type

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_roundtrip(self):
        description = 'a file to test writing and reading a %s' % self.container_type
        source = 'test_roundtrip for %s' % self.container_type
        identifier = 'TEST_%s' % self.container_type
        nwbfile = NWBFile(source, description, identifier, self.start_time, file_create_date=self.create_date)
        self.addContainer(nwbfile)
        io = HDF5IO(self.filename, self.manager)
        io.write(nwbfile)
        try:
            read_nwbfile = io.read()
            read_container = self.getContainer(read_nwbfile)
            self.assertContainerEqual(self.container, read_container)
        finally:
            io.close()

    def addContainer(self, nwbfile):
        ''' Should take an NWBFile object and add the container to it '''
        raise unittest.SkipTest('Cannot run test unless addContainer is implemented')

    def getContainer(self, nwbfile):
        ''' Should take an NWBFile object and return the Container'''
        raise unittest.SkipTest('Cannot run test unless getContainer is implemented')
