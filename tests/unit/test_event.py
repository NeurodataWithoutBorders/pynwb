import numpy as np

from pynwb.event import TimestampVectorData, DurationVectorData, EventsTable
from pynwb.testing import TestCase


class TestTimestampVectorData(TestCase):
    """Unit tests for TimestampVectorData"""

    def test_init(self):
        """Test basic initialization"""
        ts = TimestampVectorData(name='timestamps', data=[1.0, 2.0, 3.0])
        self.assertEqual(ts.name, 'timestamps')
        self.assertListEqual(ts.data, [1.0, 2.0, 3.0])
        self.assertEqual(ts.unit, 'seconds')
        self.assertIsNone(ts.resolution)
        self.assertEqual(ts.description, 'timestamps in seconds')

    def test_init_with_resolution(self):
        """Test initialization with resolution"""
        ts = TimestampVectorData(name='timestamps', data=[1.0, 2.0], resolution=0.001)
        self.assertEqual(ts.resolution, 0.001)

    def test_init_with_description(self):
        """Test initialization with custom description"""
        ts = TimestampVectorData(name='timestamps', description='custom description', data=[1.0])
        self.assertEqual(ts.description, 'custom description')


class TestDurationVectorData(TestCase):
    """Unit tests for DurationVectorData"""

    def test_init(self):
        """Test basic initialization"""
        dur = DurationVectorData(name='durations', data=[0.5, 1.0, 1.5])
        self.assertEqual(dur.name, 'durations')
        self.assertListEqual(dur.data, [0.5, 1.0, 1.5])
        self.assertEqual(dur.unit, 'seconds')
        self.assertIsNone(dur.resolution)
        self.assertEqual(dur.description, 'durations in seconds')

    def test_init_with_resolution(self):
        """Test initialization with resolution"""
        dur = DurationVectorData(name='durations', data=[0.5], resolution=0.001)
        self.assertEqual(dur.resolution, 0.001)

    def test_init_with_description(self):
        """Test initialization with custom description"""
        dur = DurationVectorData(name='durations', description='custom description', data=[0.5])
        self.assertEqual(dur.description, 'custom description')


class TestEventsTable(TestCase):
    """Unit tests for EventsTable"""

    def test_init(self):
        """Test basic initialization"""
        table = EventsTable(name='events', description='test events')
        self.assertEqual(table.name, 'events')
        self.assertEqual(table.description, 'test events')
        self.assertEqual(len(table), 0)

    def test_add_event_timestamp_only(self):
        """Test adding event with only timestamp"""
        table = EventsTable(name='events', description='test events')
        table.add_event(timestamp=1.0)
        self.assertEqual(len(table), 1)
        self.assertEqual(table['timestamp'][0], 1.0)

    def test_add_event_with_duration(self):
        """Test adding event with timestamp and duration"""
        table = EventsTable(name='events', description='test events')
        table.add_event(timestamp=1.0, duration=0.5)
        self.assertEqual(len(table), 1)
        self.assertEqual(table['timestamp'][0], 1.0)
        self.assertEqual(table['duration'][0], 0.5)

    def test_add_event_with_annotation(self):
        """Test adding event with annotation"""
        table = EventsTable(name='events', description='test events')
        table.add_event(timestamp=1.0, annotation='important event')
        self.assertEqual(len(table), 1)
        self.assertEqual(table['timestamp'][0], 1.0)
        self.assertEqual(table['annotation'][0], 'important event')

    def test_add_event_with_all_fields(self):
        """Test adding event with all fields"""
        table = EventsTable(name='events', description='test events')
        table.add_event(timestamp=1.0, duration=0.5, annotation='test')
        self.assertEqual(table['timestamp'][0], 1.0)
        self.assertEqual(table['duration'][0], 0.5)
        self.assertEqual(table['annotation'][0], 'test')

    def test_add_multiple_events(self):
        """Test adding multiple events"""
        table = EventsTable(name='events', description='test events')
        table.add_event(timestamp=1.0, duration=0.5, annotation='event 1')
        table.add_event(timestamp=2.0, duration=1.0, annotation='event 2')
        table.add_event(timestamp=3.0, duration=0.25, annotation='event 3')
        self.assertEqual(len(table), 3)

    def test_add_event_with_nan_duration(self):
        """Test adding event with NaN duration"""
        table = EventsTable(name='events', description='test events')
        table.add_event(timestamp=1.0, duration=float('nan'))
        self.assertTrue(np.isnan(table['duration'][0]))

    def test_timestamp_column_class(self):
        """Test that timestamp column uses TimestampVectorData"""
        table = EventsTable(name='events', description='test events')
        table.add_event(timestamp=1.0)
        self.assertIsInstance(table['timestamp'], TimestampVectorData)

    def test_duration_column_class(self):
        """Test that duration column is DurationVectorData"""
        table = EventsTable(name='events', description='test events')
        table.add_event(timestamp=1.0, duration=0.5)
        self.assertIsInstance(table['duration'], DurationVectorData)

    def test_to_dataframe(self):
        """Test converting to dataframe"""
        table = EventsTable(name='events', description='test events')
        table.add_event(timestamp=1.0, duration=0.5, annotation='event 1')
        table.add_event(timestamp=2.0, duration=1.0, annotation='event 2')
        df = table.to_dataframe()
        self.assertEqual(len(df), 2)
        np.testing.assert_array_equal(df['timestamp'], [1.0, 2.0])
        np.testing.assert_array_equal(df['duration'], [0.5, 1.0])
        np.testing.assert_array_equal(df['annotation'], ['event 1', 'event 2'])

    def test_add_event_extra_columns(self):
        """Test adding event with extra columns via allow_extra"""
        table = EventsTable(name='events', description='test events')
        table.add_column(name='event_type', description='type of event')
        table.add_event(timestamp=1.0, event_type='stimulus')
        self.assertEqual(table['event_type'][0], 'stimulus')
