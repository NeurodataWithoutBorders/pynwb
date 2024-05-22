from datetime import datetime
from dateutil.tz import tzlocal

import numpy as np
from hdmf.utils import docval

from pynwb import NWBFile, TimeSeries, available_namespaces
from pynwb.core import NWBContainer, NWBData
from pynwb.testing import TestCase


class MyTestClass(NWBContainer):

    __nwbfields__ = ("prop1", "prop2")

    @docval({"name": "name", "type": str, "doc": "The name of this container"})
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.prop1 = "test1"


class TestNWBContainer(TestCase):
    def test_constructor(self):
        """Test constructor
        """
        obj = MyTestClass("obj1")
        self.assertEqual(obj.name, "obj1")
        obj.prop2 = "test2"

    def test_nwbfields(self):
        """Test that getters and setters work for nwbfields
        """
        obj = MyTestClass("obj1")
        obj.prop2 = "test2"
        self.assertEqual(obj.prop1, "test1")
        self.assertEqual(obj.prop2, "test2")

    def test_get_data_type(self):
        obj = NWBContainer("obj1")
        dt = obj.data_type
        self.assertEqual(dt, 'NWBContainer')


class MyNWBData(NWBData):

    __nwbfields__ = ("data", )

    @docval(
        {"name": "name", "type": str, "doc": "The name of this container"},
        {"name": "data", "type": ("array_data", "data"), "doc": "any data"},
    )
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class TestNWBData(TestCase):
    def test_constructor(self):
        """Test constructor
        """
        obj = MyNWBData("obj1", data=[[1, 2, 3], [1, 2, 3]])
        self.assertEqual(obj.name, "obj1")

    def test_append_list(self):

        obj = MyNWBData("obj1", data=[[1, 2, 3], [1, 2, 3]])
        obj.append([4, 5, 6])
        np.testing.assert_array_equal(obj.data, [[1, 2, 3], [1, 2, 3], [4, 5, 6]])

    def test_append_ndarray_2d(self):
        obj = MyNWBData("obj1", data=np.array([[1, 2, 3], [1, 2, 3]]))
        obj.append([4, 5, 6])
        np.testing.assert_array_equal(obj.data, [[1, 2, 3], [1, 2, 3], [4, 5, 6]])

        def test_append_ndarray_1d(self):
            obj = MyNWBData("obj1", data=np.array([1, 2, 3]))
            obj.append([4])
            np.testing.assert_array_equal(obj.data, [1, 2, 3, 4])

    def test_extend_list(self):
        obj = MyNWBData("obj1", data=[[1, 2, 3], [1, 2, 3]])
        obj.extend([[4, 5, 6]])
        np.testing.assert_array_equal(obj.data, [[1, 2, 3], [1, 2, 3], [4, 5, 6]])

    def test_extend_ndarray_1d(self):
        obj = MyNWBData("obj1", data=np.array([1, 2, 3]))
        obj.extend([4, 5, 6])
        np.testing.assert_array_equal(obj.data, [1, 2, 3, 4, 5, 6])

    def test_extend_ndarray_2d(self):
        obj = MyNWBData("obj1", data=np.array([[1, 2, 3], [1, 2, 3]]))
        obj.extend([[4, 5, 6]])
        np.testing.assert_array_equal(obj.data, [[1, 2, 3], [1, 2, 3], [4, 5, 6]])


class TestPrint(TestCase):
    def test_print_file(self):
        nwbfile = NWBFile(
            session_description="session_description",
            identifier="identifier",
            session_start_time=datetime.now(tzlocal()),
        )
        ts1 = TimeSeries(
            name="name1",
            data=[1000, 2000, 3000],
            unit="unit",
            timestamps=[1.0, 2.0, 3.0],
        )
        ts2 = TimeSeries(
            name="name2",
            data=[1000, 2000, 3000],
            unit="unit",
            timestamps=[1.0, 2.0, 3.0],
        )
        expected = """name1 pynwb.base.TimeSeries at 0x%d
Fields:
  comments: no comments
  conversion: 1.0
  data: [1000 2000 3000]
  description: no description
  interval: 1
  offset: 0.0
  resolution: -1.0
  timestamps: [1. 2. 3.]
  timestamps_unit: seconds
  unit: unit
"""
        expected %= id(ts1)
        self.assertEqual(str(ts1), expected)
        nwbfile.add_acquisition(ts1)
        nwbfile.add_acquisition(ts2)
        nwbfile.add_epoch(start_time=1.0, stop_time=10.0, tags=["tag1", "tag2"])
        expected_re = r"""root pynwb\.file\.NWBFile at 0x\d+
Fields:
  acquisition: {
    name1 <class 'pynwb\.base\.TimeSeries'>,
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
        self.assertEqual(
            available_namespaces(), ("hdmf-common", "hdmf-experimental", "core")
        )
