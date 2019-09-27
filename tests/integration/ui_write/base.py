import unittest2 as unittest
from datetime import datetime
from dateutil.tz import tzlocal, tzutc
import os
import numpy as np
import h5py
import numpy.testing as npt

from pynwb import get_manager, NWBFile, NWBHDF5IO, validate as pynwb_validate
from pynwb.testing import remove_test_file
from hdmf.backends.hdf5 import HDF5IO

from hdmf.container import Data, Container

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

    @unittest.skip("deprecated")
    def test_build(self):
        """
        As of 20190110, this test has been deprecated. Maintaining hardcoded builder objects has become
        increasingly difficult, and offers little in the way of debugging and identifying problems
        """
        try:
            self.builder = self.setUpBuilder()
        except unittest.SkipTest:
            raise unittest.SkipTest("cannot run construct test for %s -- setUpBuilder not implemented" %
                                    self.__class__.__name__)
        self.maxDiff = None
        result = self.manager.build(self.container)
        # do something here to validate the result Builder against the spec
        self.assertDictEqual(result, self.builder)

    @unittest.skip("deprecated")
    def test_construct(self):
        """
        As of 20190110, this test has been deprecated. Maintaining hardcoded builder objects has become
        increasingly difficult, and offers little in the way of debugging and identifying problems
        """
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
        for nwbfield in getattr(container1, container1._fieldsname):
            with self.subTest(nwbfield=nwbfield, container_type=type1.__name__):
                f1 = getattr(container1, nwbfield)
                f2 = getattr(container2, nwbfield)
                if isinstance(f1, h5py.Dataset):
                    f1 = f1[()]
                if isinstance(f1, (tuple, list, np.ndarray)):
                    if len(f1) > 0:
                        if isinstance(f1[0], Container):
                            for sub1, sub2 in zip(f1, f2):
                                self.assertContainerEqual(sub1, sub2)
                        elif isinstance(f1[0], Data):
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
                elif isinstance(f1, dict) and len(f1) and isinstance(next(iter(f1.values())), Container):
                    f1_keys = set(f1.keys())
                    f2_keys = set(f2.keys())
                    self.assertSetEqual(f1_keys, f2_keys)
                    for k in f1_keys:
                        with self.subTest(module_name=k):
                            self.assertContainerEqual(f1[k], f2[k])
                elif isinstance(f1, Container):
                    self.assertContainerEqual(f1, f2)
                elif isinstance(f1, Data) or isinstance(f2, Data):
                    if isinstance(f1, Data) and isinstance(f2, Data):
                        self.assertDataEqual(f1, f2)
                    elif isinstance(f1, Data):
                        self.assertTrue(np.array_equal(f1.data, f2))
                    elif isinstance(f2, Data):
                        self.assertTrue(np.array_equal(f1.data, f2))
                else:
                    if isinstance(f1, (float, np.float32, np.float16)):
                        npt.assert_almost_equal(f1, f2)
                    else:
                        self.assertEqual(f1, f2)

    def assertDataEqual(self, data1, data2):
        self.assertEqual(type(data1), type(data2))
        self.assertEqual(len(data1), len(data2))


class TestMapRoundTrip(TestMapNWBContainer):

    _required_tests = ('test_roundtrip',)
    run_injected_file_test = False

    def setUp(self):
        super(TestMapRoundTrip, self).setUp()
        self.object_id = self.container.object_id
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
        remove_test_file(self.filename)

    def roundtripContainer(self, cache_spec=False):
        description = 'a file to test writing and reading a %s' % self.container_type
        identifier = 'TEST_%s' % self.container_type
        nwbfile = NWBFile(description, identifier, self.start_time, file_create_date=self.create_date)
        self.addContainer(nwbfile)

        self.writer = HDF5IO(self.filename, manager=get_manager(), mode='w')
        self.writer.write(nwbfile, cache_spec=cache_spec)
        self.writer.close()
        self.reader = HDF5IO(self.filename, manager=get_manager(), mode='r')
        self.read_nwbfile = self.reader.read()

        try:
            tmp = self.getContainer(self.read_nwbfile)
            return tmp
        except Exception as e:
            self.reader.close()
            self.reader = None
            raise e

    def test_roundtrip(self):
        self.read_container = self.roundtripContainer()
        # make sure we get a completely new object
        self.assertIsNotNone(str(self.container))  # added as a test to make sure printing works
        self.assertIsNotNone(str(self.read_container))
        self.assertNotEqual(id(self.container), id(self.read_container))
        self.assertIs(self.read_nwbfile.objects[self.container.object_id], self.read_container)
        self.assertContainerEqual(self.read_container, self.container)
        self.validate()

    def validate(self):
        # validate created file
        if os.path.exists(self.filename):
            with NWBHDF5IO(self.filename, mode='r') as io:
                errors = pynwb_validate(io)
                if errors:
                    for err in errors:
                        raise Exception(err)

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
