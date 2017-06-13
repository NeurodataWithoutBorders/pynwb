import unittest

from pynwb import NWBContainer, get_build_manager

CORE_NAMESPACE = 'core'

class TestNWBContainerIO(unittest.TestCase):

    def setUp(self):
        if type(self) == TestNWBContainerIO:
            raise unittest.SkipTest('TestNWBContainerIO must be extended with setUpBuilder and setUpContainer implemented')
        self.manager = get_build_manager()
        self.setUpContainer()
        self.setUpBuilder()

    def test_build(self):
        self.maxDiff = None
        result = self.manager.build(self.container)
        self.assertDictEqual(result, self.builder)

    def test_construct(self):
        result = self.manager.construct(self.builder)
        self.assertContainerEqual(result, self.container)

    def setUpBuilder(self):
        ''' Should set the attribute 'builder' on self '''
        if isinstance(self, TestNWBContainerIO):
            raise unittest.SkipTest('Cannot run test unless setUpBuilder is implemented')

    def setUpContainer(self):
        ''' Should set the attribute 'container' on self '''
        if isinstance(self, TestNWBContainerIO):
            raise unittest.SkipTest('Cannot run test unless setUpContainer is implemented')

    def assertContainerEqual(self, container1, container2):
        type1 = type(container1)
        type2 = type(container2)
        self.assertEqual(type1, type2)
        for nwbfield in container1.__nwbfields__:
            with self.subTest(nwbfield=nwbfield, container_type=type1.__name__):
                f1 = getattr(container1, nwbfield)
                f2 = getattr(container2, nwbfield)
                if isinstance(f1, tuple) or isinstance(f1, list):
                    if len(f1) > 0 and isinstance(f1[0], NWBContainer):
                        for sub1, sub2 in zip(f1,f2):
                            self.assertContainerEqual(sub1, sub2)
                        continue
                    else:
                        self.assertSequenceEqual(f1, f2)
                elif isinstance(f1, dict) and len(f1) and isinstance(next(iter(f1.values())), NWBContainer):
                    f1_keys = set(f1.keys())
                    f2_keys = set(f2.keys())
                    self.assertSetEqual(f1_keys, f2_keys)
                    for k in f1_keys:
                        with self.subTest(module_name=k):
                            self.assertContainerEqual(f1[k], f2[k])
                elif isinstance(f1, NWBContainer):
                    self.assertContainerEqual(f1, f2)
                else:
                    self.assertEqual(f1, f2)

