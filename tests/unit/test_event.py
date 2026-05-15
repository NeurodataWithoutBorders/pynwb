import numpy as np
from datetime import datetime
from dateutil.tz import tzlocal

from hdmf.common import MeaningsTable, VectorData

from pynwb import NWBFile
from pynwb.event import TimestampVectorData, DurationVectorData, EventsTable
from pynwb.testing import TestCase


class TestTimestampVectorData(TestCase):
    """Unit tests for TimestampVectorData"""

    def test_init(self):
        """Test basic initialization"""
        ts = TimestampVectorData(name='timestamps', description='timestamps in seconds', data=[1.0, 2.0, 3.0])
        self.assertEqual(ts.name, 'timestamps')
        self.assertListEqual(ts.data, [1.0, 2.0, 3.0])
        self.assertEqual(ts.unit, 'seconds')
        self.assertIsNone(ts.resolution)
        self.assertEqual(ts.description, 'timestamps in seconds')

    def test_init_with_resolution(self):
        """Test initialization with resolution"""
        ts = TimestampVectorData(name='timestamps', description='timestamps in seconds', data=[1.0, 2.0],
                                resolution=0.001)
        self.assertEqual(ts.resolution, 0.001)


class TestDurationVectorData(TestCase):
    """Unit tests for DurationVectorData"""

    def test_init(self):
        """Test basic initialization"""
        dur = DurationVectorData(name='durations', description='durations in seconds', data=[0.5, 1.0, 1.5])
        self.assertEqual(dur.name, 'durations')
        self.assertListEqual(dur.data, [0.5, 1.0, 1.5])
        self.assertEqual(dur.unit, 'seconds')
        self.assertIsNone(dur.resolution)
        self.assertEqual(dur.description, 'durations in seconds')

    def test_init_with_resolution(self):
        """Test initialization with resolution"""
        dur = DurationVectorData(name='durations', description='durations in seconds', data=[0.5], resolution=0.001)
        self.assertEqual(dur.resolution, 0.001)


class TestEventsTable(TestCase):
    """Unit tests for EventsTable"""

    def test_init(self):
        """Test basic initialization"""
        table = EventsTable(name='events', description='test events')
        self.assertEqual(table.name, 'events')
        self.assertEqual(table.description, 'test events')
        self.assertIsNone(table.source_description)
        self.assertEqual(len(table), 0)

    def test_init_with_source_description(self):
        """Test initialization with source_description"""
        table = EventsTable(name='events', description='test events',
                            source_description='Acquisition system')
        self.assertEqual(table.source_description, 'Acquisition system')

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

    def test_init_with_meanings_tables(self):
        """Test that meanings_tables is forwarded through EventsTable.__init__."""
        timestamp_col = TimestampVectorData(
            name='timestamp', description='ts', data=[1.0, 2.0]
        )
        annotation_col = VectorData(
            name='annotation', description='annotations', data=['go', 'stop']
        )
        meanings = MeaningsTable(
            target=annotation_col,
            description='Meanings of the annotation values.',
        )
        meanings.add_row(value='go', meaning='start trial')
        meanings.add_row(value='stop', meaning='end trial')

        table = EventsTable(
            name='events',
            description='test events',
            columns=[timestamp_col, annotation_col],
            meanings_tables=[meanings],
        )
        self.assertIn('annotation_meanings', table.meanings_tables)
        self.assertIs(table.meanings_tables['annotation_meanings'], meanings)


class TestNWBFileMergeEvents(TestCase):
    """Unit tests for NWBFile.merge_events_tables and NWBFile.get_all_events"""

    def _make_nwbfile(self):
        return NWBFile(
            session_description='test',
            identifier='test_merge_events',
            session_start_time=datetime(2021, 1, 1, tzinfo=tzlocal()),
        )

    def _make_table(self, name, timestamps, **extra_cols):
        table = EventsTable(name=name, description=f'{name} events')
        for col_name in extra_cols:
            table.add_column(name=col_name, description=col_name)
        for i, ts in enumerate(timestamps):
            row = {'timestamp': ts}
            for col_name, values in extra_cols.items():
                row[col_name] = values[i]
            table.add_event(**row)
        return table

    def test_merge_events_tables(self):
        """merge_events_tables returns a DataFrame indexed by timestamp with all rows."""
        t1 = self._make_table('licks', [1.0, 2.0])
        t2 = self._make_table('rewards', [3.0, 4.0])
        nwbfile = self._make_nwbfile()
        result = nwbfile.merge_events_tables([t1, t2])
        self.assertEqual(result.index.name, 'timestamp')
        np.testing.assert_array_equal(sorted(result.index), [1.0, 2.0, 3.0, 4.0])

    def test_merge_events_tables_fills_missing_columns_with_nan(self):
        """Columns absent from some tables are filled with NaN."""
        t1 = self._make_table('licks', [1.0], annotation=['lick'])
        t2 = self._make_table('rewards', [2.0])
        nwbfile = self._make_nwbfile()
        result = nwbfile.merge_events_tables([t1, t2])
        self.assertIn('annotation', result.columns)
        self.assertEqual(result.loc[1.0, 'annotation'], 'lick')
        self.assertTrue(np.isnan(result.loc[2.0, 'annotation']))

    def test_get_all_events(self):
        """get_all_events merges all tables in NWBFile.events."""
        t1 = self._make_table('licks', [1.0, 2.0])
        t2 = self._make_table('rewards', [3.0])
        nwbfile = self._make_nwbfile()
        nwbfile.add_events_table(t1)
        nwbfile.add_events_table(t2)
        result = nwbfile.get_all_events()
        self.assertEqual(result.index.name, 'timestamp')
        self.assertEqual(len(result), 3)

    def test_get_all_events_empty(self):
        """get_all_events returns an empty DataFrame when no events tables exist."""
        nwbfile = self._make_nwbfile()
        result = nwbfile.get_all_events()
        self.assertIsInstance(result, type(result))
        self.assertEqual(len(result), 0)
