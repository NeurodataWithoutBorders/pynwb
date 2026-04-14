"""Integration tests for EventsTable roundtrip through NWBFile.events."""
import numpy as np
import tempfile
import os

from pynwb import NWBHDF5IO, NWBFile
from pynwb.event import TimestampVectorData, DurationVectorData, EventsTable
from pynwb.testing import TestCase
from datetime import datetime
from dateutil.tz import tzlocal


class TestEventsTableRoundtrip(TestCase):
    """Test roundtrip for EventsTable through HDF5"""

    def setUp(self):
        self.path = tempfile.mktemp(suffix='.nwb')

    def tearDown(self):
        if os.path.exists(self.path):
            os.remove(self.path)

    def _create_nwbfile(self):
        return NWBFile(
            session_description='test session',
            identifier='test_events_001',
            session_start_time=datetime(2021, 1, 1, tzinfo=tzlocal())
        )

    def test_basic_roundtrip(self):
        """Test basic EventsTable roundtrip through NWBFile"""
        # Create table
        table = EventsTable(
            name='test_events',
            description='Test events table'
        )
        table.add_event(timestamp=1.0, duration=0.5, annotation='event 1')
        table.add_event(timestamp=2.0, duration=1.0, annotation='event 2')

        # Write
        nwbfile = self._create_nwbfile()
        nwbfile.add_events_table(table)
        with NWBHDF5IO(self.path, 'w') as io:
            io.write(nwbfile)

        # Read back
        with NWBHDF5IO(self.path, 'r') as io:
            read_nwbfile = io.read()
            read_table = read_nwbfile.events['test_events']

            # Verify
            self.assertEqual(len(read_table), 2)
            np.testing.assert_array_equal(read_table['timestamp'].data[:], [1.0, 2.0])
            np.testing.assert_array_equal(read_table['duration'].data[:], [0.5, 1.0])
            self.assertEqual(read_table['annotation'].data[0], 'event 1')
            self.assertEqual(read_table['annotation'].data[1], 'event 2')

    def test_roundtrip_column_types(self):
        """Test that column types are preserved after roundtrip"""
        table = EventsTable(
            name='test_events',
            description='Test events table'
        )
        table.add_event(timestamp=1.0, duration=0.5)

        nwbfile = self._create_nwbfile()
        nwbfile.add_events_table(table)
        with NWBHDF5IO(self.path, 'w') as io:
            io.write(nwbfile)

        with NWBHDF5IO(self.path, 'r') as io:
            read_nwbfile = io.read()
            read_table = read_nwbfile.events['test_events']

            self.assertIsInstance(read_table['timestamp'], TimestampVectorData)
            self.assertIsInstance(read_table['duration'], DurationVectorData)

    def test_roundtrip_units(self):
        """Test that units are preserved after roundtrip"""
        table = EventsTable(
            name='test_events',
            description='Test events table'
        )
        table.add_event(timestamp=1.0, duration=0.5)

        nwbfile = self._create_nwbfile()
        nwbfile.add_events_table(table)
        with NWBHDF5IO(self.path, 'w') as io:
            io.write(nwbfile)

        with NWBHDF5IO(self.path, 'r') as io:
            read_nwbfile = io.read()
            read_table = read_nwbfile.events['test_events']

            self.assertEqual(read_table['timestamp'].unit, 'seconds')
            self.assertEqual(read_table['duration'].unit, 'seconds')

    def test_roundtrip_with_nan_duration(self):
        """Test roundtrip with NaN duration values"""
        table = EventsTable(
            name='test_events',
            description='Test events table'
        )
        table.add_event(timestamp=1.0, duration=0.5, annotation='has duration')
        table.add_event(timestamp=2.0, duration=float('nan'), annotation='nan duration')
        table.add_event(timestamp=3.0, duration=float('nan'), annotation='also nan')

        nwbfile = self._create_nwbfile()
        nwbfile.add_events_table(table)
        with NWBHDF5IO(self.path, 'w') as io:
            io.write(nwbfile)

        with NWBHDF5IO(self.path, 'r') as io:
            read_nwbfile = io.read()
            read_table = read_nwbfile.events['test_events']

            durations = read_table['duration'].data[:]
            self.assertEqual(durations[0], 0.5)
            self.assertTrue(np.isnan(durations[1]))
            self.assertTrue(np.isnan(durations[2]))

    def test_roundtrip_timestamps_only(self):
        """Test roundtrip with only timestamps (no optional columns)"""
        table = EventsTable(
            name='test_events',
            description='Test events table'
        )
        table.add_event(timestamp=1.0)
        table.add_event(timestamp=2.0)
        table.add_event(timestamp=3.0)

        nwbfile = self._create_nwbfile()
        nwbfile.add_events_table(table)
        with NWBHDF5IO(self.path, 'w') as io:
            io.write(nwbfile)

        with NWBHDF5IO(self.path, 'r') as io:
            read_nwbfile = io.read()
            read_table = read_nwbfile.events['test_events']

            self.assertEqual(len(read_table), 3)
            np.testing.assert_array_equal(read_table['timestamp'].data[:], [1.0, 2.0, 3.0])
            # Duration and annotation columns should not exist
            self.assertNotIn('duration', read_table.colnames)
            self.assertNotIn('annotation', read_table.colnames)

    def test_roundtrip_with_extra_columns(self):
        """Test roundtrip with user-defined extra columns"""
        table = EventsTable(
            name='test_events',
            description='Test events table'
        )
        table.add_column(name='event_type', description='Type of event')
        table.add_column(name='confidence', description='Confidence score')

        table.add_event(timestamp=1.0, event_type='stimulus', confidence=0.95)
        table.add_event(timestamp=2.0, event_type='response', confidence=0.85)

        nwbfile = self._create_nwbfile()
        nwbfile.add_events_table(table)
        with NWBHDF5IO(self.path, 'w') as io:
            io.write(nwbfile)

        with NWBHDF5IO(self.path, 'r') as io:
            read_nwbfile = io.read()
            read_table = read_nwbfile.events['test_events']

            self.assertIn('event_type', read_table.colnames)
            self.assertIn('confidence', read_table.colnames)
            self.assertEqual(read_table['event_type'].data[0], 'stimulus')
            self.assertEqual(read_table['confidence'].data[0], 0.95)

    def test_roundtrip_timestamp_resolution(self):
        """Test that timestamp resolution is preserved after roundtrip"""
        # Create a table with a pre-created timestamp column with resolution
        timestamp_col = TimestampVectorData(
            name='timestamp',
            description='timestamps',
            data=[1.0, 2.0],
            resolution=0.001
        )
        table = EventsTable(
            name='test_events',
            description='Test events table',
            columns=[timestamp_col],
        )

        nwbfile = self._create_nwbfile()
        nwbfile.add_events_table(table)
        with NWBHDF5IO(self.path, 'w') as io:
            io.write(nwbfile)

        with NWBHDF5IO(self.path, 'r') as io:
            read_nwbfile = io.read()
            read_table = read_nwbfile.events['test_events']

            self.assertEqual(read_table['timestamp'].resolution, 0.001)
