from datetime import datetime
from dateutil.tz import tzlocal

from hdmf.utils import docval, call_docval_func

from pynwb import NWBFile, TimeSeries, available_namespaces
from pynwb.core import NWBContainer, LabelledDict
from pynwb.testing import TestCase


class MyTestClass(NWBContainer):

    __nwbfields__ = ('prop1', 'prop2')

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this container'})
    def __init__(self, **kwargs):
        call_docval_func(super(MyTestClass, self).__init__, kwargs)
        self.prop1 = 'test1'


class TestNWBContainer(TestCase):

    def test_constructor(self):
        """Test constructor
        """
        obj = MyTestClass('obj1')
        self.assertEqual(obj.name, 'obj1')
        obj.prop2 = 'test2'

    def test_nwbfields(self):
        """Test that getters and setters work for nwbfields
        """
        obj = MyTestClass('obj1')
        obj.prop2 = 'test2'
        self.assertEqual(obj.prop1, 'test1')
        self.assertEqual(obj.prop2, 'test2')


class TestPrint(TestCase):

    def test_print_file(self):
        nwbfile = NWBFile(session_description='session_description',
                          identifier='identifier', session_start_time=datetime.now(tzlocal()))
        ts = TimeSeries('name', [1., 2., 3.] * 1000, timestamps=[1, 2, 3])
        ts2 = TimeSeries('name2', [1, 2, 3] * 1000, timestamps=[1, 2, 3])
        expected = """name pynwb.base.TimeSeries at 0x%d
Fields:
  comments: no comments
  conversion: 1.0
  data: [1. 2. 3. ... 1. 2. 3.]
  description: no description
  interval: 1
  resolution: -1.0
  timestamps: [1 2 3]
  timestamps_unit: seconds
"""
        expected %= id(ts)
        self.assertEqual(str(ts), expected)
        nwbfile.add_acquisition(ts)
        nwbfile.add_acquisition(ts2)
        nwbfile.add_epoch(start_time=1.0, stop_time=10.0, tags=['tag1', 'tag2'])
        expected_re = r"""root pynwb\.file\.NWBFile at 0x\d+
Fields:
  acquisition: {
    name <class 'pynwb\.base\.TimeSeries'>,
    name2 <class 'pynwb\.base\.TimeSeries'>
  }
  epoch_tags: {
    tag1,
    tag2
  }
  epochs: epochs <class 'pynwb.epoch.TimeIntervals'>
  file_create_date: \[datetime.datetime\(.*\)\]
  identifier: identifier
  session_description: session_description
  session_start_time: .*
  timestamps_reference_time: .*
"""
        self.assertRegex(str(nwbfile), expected_re)


class TestAvailableNamespaces(TestCase):
    def test_available_namespaces(self):
        self.assertEqual(available_namespaces(), ('hdmf-common', 'core'))


class TestLabelledDict(TestCase):

    def setUp(self):
        self.name = 'name'
        self.container = TimeSeries(self.name, [1., 2., 3.] * 1000, timestamps=[1, 2, 3])
        self.object_id = self.container.object_id

    def test_add_default(self):
        ld = LabelledDict('test_dict')
        ld.add(self.container)
        self.assertIs(ld[self.name], self.container)

    def test_add_nondefault(self):
        ld = LabelledDict('test_dict', def_key_name='object_id')
        ld.add(self.container)
        self.assertIs(ld[self.object_id], self.container)
