import numpy as np
import pandas as pd

from datetime import datetime, timedelta
from dateutil.tz import tzlocal, tzutc
from hdmf.common import DynamicTable

from hdmf.common import VectorData
from hdmf.utils import docval, get_docval, popargs
from pynwb import NWBFile, TimeSeries, NWBHDF5IO
from pynwb.base import Image, Images
from pynwb.file import Subject, ElectrodeTable, _add_missing_timezone
from pynwb.epoch import TimeIntervals
from pynwb.ecephys import ElectricalSeries
from pynwb.testing import TestCase, remove_test_file


class NWBFileTest(TestCase):
    def setUp(self):
        self.start = datetime(2017, 5, 1, 12, 0, 0, tzinfo=tzlocal())
        self.ref_time = datetime(1979, 1, 1, 0, tzinfo=tzutc())
        self.create = [datetime(2017, 5, 1, 12, tzinfo=tzlocal()),
                       datetime(2017, 5, 2, 13, 0, 0, 1, tzinfo=tzutc()),
                       datetime(2017, 5, 2, 14, tzinfo=tzutc())]
        self.path = 'nwbfile_test.h5'
        self.nwbfile = NWBFile(session_description='a test session description for a test NWBFile',
                               identifier='FILE123',
                               session_start_time=self.start,
                               file_create_date=self.create,
                               timestamps_reference_time=self.ref_time,
                               experimenter='A test experimenter',
                               lab='a test lab',
                               institution='a test institution',
                               experiment_description='a test experiment description',
                               session_id='test1',
                               notes='my notes',
                               pharmacology='drugs',
                               protocol='protocol',
                               related_publications='my pubs',
                               slices='my slices',
                               surgery='surgery',
                               virus='a virus',
                               source_script='noscript',
                               source_script_file_name='nofilename',
                               stimulus_notes='test stimulus notes',
                               data_collection='test data collection notes',
                               keywords=('these', 'are', 'keywords'))

    def test_constructor(self):
        self.assertEqual(self.nwbfile.session_description, 'a test session description for a test NWBFile')
        self.assertEqual(self.nwbfile.identifier, 'FILE123')
        self.assertEqual(self.nwbfile.session_start_time, self.start)
        self.assertEqual(self.nwbfile.file_create_date, self.create)
        self.assertEqual(self.nwbfile.lab, 'a test lab')
        self.assertEqual(self.nwbfile.experimenter, ('A test experimenter',))
        self.assertEqual(self.nwbfile.institution, 'a test institution')
        self.assertEqual(self.nwbfile.experiment_description, 'a test experiment description')
        self.assertEqual(self.nwbfile.session_id, 'test1')
        self.assertEqual(self.nwbfile.stimulus_notes, 'test stimulus notes')
        self.assertEqual(self.nwbfile.data_collection, 'test data collection notes')
        self.assertEqual(self.nwbfile.related_publications, ('my pubs',))
        self.assertEqual(self.nwbfile.source_script, 'noscript')
        self.assertEqual(self.nwbfile.source_script_file_name, 'nofilename')
        self.assertEqual(self.nwbfile.keywords, ('these', 'are', 'keywords'))
        self.assertEqual(self.nwbfile.timestamps_reference_time, self.ref_time)

    def test_create_electrode_group(self):
        name = 'example_electrode_group'
        desc = 'An example electrode'
        loc = 'an example location'
        d = self.nwbfile.create_device('a fake device')
        elecgrp = self.nwbfile.create_electrode_group(name, desc, loc, d)
        self.assertEqual(elecgrp.description, desc)
        self.assertEqual(elecgrp.location, loc)
        self.assertIs(elecgrp.device, d)

    def test_create_custom_intervals(self):
        df_words = pd.DataFrame({'start_time': [.1, 2.], 'stop_time': [.8, 2.3],
                                 'label': ['hello', 'there']})
        words = TimeIntervals.from_dataframe(df_words, name='words')
        self.nwbfile.add_time_intervals(words)
        self.assertEqual(self.nwbfile.intervals['words'], words)

    def test_create_electrode_group_invalid_index(self):
        """
        Test the case where the user creates an electrode table region with
        indexes that are out of range of the amount of electrodes added.
        """
        nwbfile = NWBFile('a', 'b', datetime.now(tzlocal()))
        device = nwbfile.create_device('a')
        elecgrp = nwbfile.create_electrode_group('a', 'b', device=device, location='a')
        for i in range(4):
            nwbfile.add_electrode(location='a', group=elecgrp, id=i)
        with self.assertRaises(IndexError):
            nwbfile.create_electrode_table_region(list(range(6)), 'test')

    def test_access_group_after_io(self):
        """
        Motivated by #739
        """
        nwbfile = NWBFile('a', 'b', datetime.now(tzlocal()))
        device = nwbfile.create_device('a')
        elecgrp = nwbfile.create_electrode_group('a', 'b', device=device, location='a')
        nwbfile.add_electrode(location='a', group=elecgrp, id=0)

        with NWBHDF5IO('electrodes_mwe.nwb', 'w') as io:
            io.write(nwbfile)

        with NWBHDF5IO('electrodes_mwe.nwb', 'a') as io:
            nwbfile_i = io.read()
            for aa, bb in zip(nwbfile_i.electrodes['group'][:], nwbfile.electrodes['group'][:]):
                self.assertEqual(aa.name, bb.name)

        for i in range(4):
            nwbfile.add_electrode(location='a', group=elecgrp, id=i + 1)

        with NWBHDF5IO('electrodes_mwe.nwb', 'w') as io:
            io.write(nwbfile)

        with NWBHDF5IO('electrodes_mwe.nwb', 'a') as io:
            nwbfile_i = io.read()
            for aa, bb in zip(nwbfile_i.electrodes['group'][:], nwbfile.electrodes['group'][:]):
                self.assertEqual(aa.name, bb.name)

        remove_test_file("electrodes_mwe.nwb")

    def test_access_processing(self):
        self.nwbfile.create_processing_module('test_mod', 'test_description')
        # test deprecate .modules
        with self.assertWarnsWith(DeprecationWarning, 'NWBFile.modules has been replaced by NWBFile.processing.'):
            modules = self.nwbfile.modules['test_mod']
        self.assertIs(self.nwbfile.processing['test_mod'], modules)

    def test_epoch_tags(self):
        tags1 = ['t1', 't2']
        tags2 = ['t3', 't4']
        tstamps = np.arange(1.0, 100.0, 0.1, dtype=np.float64)
        ts = TimeSeries("test_ts", list(range(len(tstamps))), 'unit', timestamps=tstamps)
        expected_tags = tags1 + tags2
        self.nwbfile.add_epoch(0.0, 1.0, tags1, ts)
        self.nwbfile.add_epoch(0.0, 1.0, tags2, ts)
        tags = self.nwbfile.epoch_tags
        self.assertEqual(set(expected_tags), set(tags))

    def test_add_acquisition(self):
        self.nwbfile.add_acquisition(TimeSeries('test_ts', [0, 1, 2, 3, 4, 5],
                                                'grams', timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5]))
        self.assertEqual(len(self.nwbfile.acquisition), 1)

    def test_add_stimulus(self):
        self.nwbfile.add_stimulus(TimeSeries('test_ts', [0, 1, 2, 3, 4, 5],
                                             'grams', timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5]))
        self.assertEqual(len(self.nwbfile.stimulus), 1)

    def test_add_stimulus_timeseries_arg(self):
        """Test nwbfile.add_stimulus using the deprecated 'timeseries' keyword argument"""
        msg = (
            "The 'timeseries' keyword argument is deprecated and will be removed in PyNWB 3.0. "
            "Use the 'stimulus' argument instead."
        )
        with self.assertWarnsWith(DeprecationWarning, msg):
            self.nwbfile.add_stimulus(
                timeseries=TimeSeries(
                    name='test_ts',
                    data=[0, 1, 2, 3, 4, 5],
                    unit='grams',
                    timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
                )
            )
        self.assertEqual(len(self.nwbfile.stimulus), 1)

    def test_add_stimulus_no_stimulus_arg(self):
        """Test nwbfile.add_stimulus using the deprecated 'timeseries' keyword argument"""
        msg = (
            "The 'stimulus' keyword argument is required. The 'timeseries' keyword argument can be "
            "provided for backwards compatibility but is deprecated in favor of 'stimulus' and will be "
            "removed in PyNWB 3.0."
        )
        with self.assertRaisesWith(ValueError, msg):
            self.nwbfile.add_stimulus(None)
        self.assertEqual(len(self.nwbfile.stimulus), 0)

    def test_add_stimulus_dynamic_table(self):
        dt = DynamicTable(
            name='test_dynamic_table',
            description='a test dynamic table',
        )
        self.nwbfile.add_stimulus(dt)
        self.assertEqual(len(self.nwbfile.stimulus), 1)
        self.assertIs(self.nwbfile.stimulus['test_dynamic_table'], dt)

    def test_add_stimulus_template(self):
        self.nwbfile.add_stimulus_template(TimeSeries('test_ts', [0, 1, 2, 3, 4, 5],
                                                      'grams', timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5]))
        self.assertEqual(len(self.nwbfile.stimulus_template), 1)

    def test_add_stimulus_template_images(self):
        image1 = Image(name='test_image1', data=np.ones((10, 10)))
        images = Images(name='images_name', images=[image1])
        self.nwbfile.add_stimulus_template(images)
        self.assertEqual(len(self.nwbfile.stimulus_template), 1)

    def test_add_analysis(self):
        self.nwbfile.add_analysis(TimeSeries('test_ts', [0, 1, 2, 3, 4, 5],
                                             'grams', timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5]))
        self.assertEqual(len(self.nwbfile.analysis), 1)

    def test_add_acquisition_check_dups(self):
        self.nwbfile.add_acquisition(TimeSeries('test_ts', [0, 1, 2, 3, 4, 5],
                                                'grams', timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5]))
        with self.assertRaises(ValueError):
            self.nwbfile.add_acquisition(TimeSeries('test_ts', [0, 1, 2, 3, 4, 5],
                                                    'grams', timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5]))

    def test_get_acquisition_empty(self):
        with self.assertRaisesWith(ValueError, "acquisition of NWBFile 'root' is empty."):
            self.nwbfile.get_acquisition()

    def test_get_acquisition_multiple_elements(self):
        self.nwbfile.add_acquisition(TimeSeries('test_ts1', [0, 1, 2, 3, 4, 5],
                                                'grams', timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5]))
        self.nwbfile.add_acquisition(TimeSeries('test_ts2', [0, 1, 2, 3, 4, 5],
                                                'grams', timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5]))
        msg = "More than one element in acquisition of NWBFile 'root' -- must specify a name."
        with self.assertRaisesWith(ValueError,  msg):
            self.nwbfile.get_acquisition()

    def test_add_acquisition_invalid_name(self):
        self.nwbfile.add_acquisition(TimeSeries('test_ts', [0, 1, 2, 3, 4, 5],
                                                'grams', timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5]))
        msg = "\"'TEST_TS' not found in acquisition of NWBFile 'root'.\""
        with self.assertRaisesWith(KeyError, msg):
            self.nwbfile.get_acquisition("TEST_TS")

    def test_set_electrode_table(self):
        table = ElectrodeTable()
        dev1 = self.nwbfile.create_device('dev1')
        group = self.nwbfile.create_electrode_group('tetrode1', 'tetrode description', 'tetrode location', dev1)

        table.add_row(location='CA1', group=group, group_name='tetrode1')
        table.add_row(location='CA1', group=group, group_name='tetrode1')
        table.add_row(location='CA1', group=group, group_name='tetrode1')
        table.add_row(location='CA1', group=group, group_name='tetrode1')

        self.nwbfile.set_electrode_table(table)

        self.assertIs(self.nwbfile.electrodes, table)
        self.assertIs(table.parent, self.nwbfile)

    def test_add_unit_column(self):
        self.nwbfile.add_unit_column('unit_type', 'the type of unit')
        self.assertEqual(self.nwbfile.units.colnames, ('unit_type',))

    def test_add_unit(self):
        self.nwbfile.add_unit(id=1)
        self.assertEqual(len(self.nwbfile.units), 1)
        self.nwbfile.add_unit(id=2)
        self.nwbfile.add_unit(id=3)
        self.assertEqual(len(self.nwbfile.units), 3)

    def test_add_trial_column(self):
        self.nwbfile.add_trial_column('trial_type', 'the type of trial')
        self.assertEqual(self.nwbfile.trials.colnames, ('start_time', 'stop_time', 'trial_type'))

    def test_add_trial_column_custom_class(self):
        class SubVectorData(VectorData):
            __fields__ = ('extra_kwarg', )

            @docval(
                *get_docval(VectorData.__init__, "name", "description", "data"),
                {'name': 'extra_kwarg', 'type': 'str', 'doc': 'An extra kwarg.'},
            )
            def __init__(self, **kwargs):
                extra_kwarg = popargs('extra_kwarg', kwargs)
                super().__init__(**kwargs)
                self.extra_kwarg = extra_kwarg

        self.nwbfile.add_trial_column(
            name="test",
            description="test",
            col_cls=SubVectorData,
            extra_kwarg="test_extra_kwarg"
        )
        self.assertEqual(self.nwbfile.trials["test"].extra_kwarg, "test_extra_kwarg")

    def test_add_trial(self):
        self.nwbfile.add_trial(start_time=10.0, stop_time=20.0)
        self.assertEqual(len(self.nwbfile.trials), 1)
        self.nwbfile.add_trial(start_time=30.0, stop_time=40.0)
        self.nwbfile.add_trial(start_time=50.0, stop_time=70.0)
        self.assertEqual(len(self.nwbfile.trials), 3)

    def test_add_invalid_times_column(self):
        self.nwbfile.add_invalid_times_column('comments', 'description of reason for omitting time')
        self.assertEqual(self.nwbfile.invalid_times.colnames, ('start_time', 'stop_time', 'comments'))

    def test_add_invalid_time_interval(self):

        self.nwbfile.add_invalid_time_interval(start_time=0.0, stop_time=12.0)
        self.assertEqual(len(self.nwbfile.invalid_times), 1)
        self.nwbfile.add_invalid_time_interval(start_time=15.0, stop_time=16.0)
        self.nwbfile.add_invalid_time_interval(start_time=17.0, stop_time=20.5)
        self.assertEqual(len(self.nwbfile.invalid_times), 3)

    def test_add_invalid_time_w_ts(self):
        ts = TimeSeries(name='name', data=[1.2], rate=1.0, unit='na')
        self.nwbfile.add_invalid_time_interval(start_time=18.0, stop_time=20.6,
                                               timeseries=ts, tags=('hi', 'there'))

    def test_add_electrode(self):
        dev1 = self.nwbfile.create_device(name='dev1')
        group = self.nwbfile.create_electrode_group(
            name='tetrode1',
            description='tetrode description',
            location='tetrode location',
            device=dev1
        )
        self.nwbfile.add_electrode(
            x=1.0, y=2.0, z=3.0,
            imp=-1.0,
            location='CA1',
            filtering='none',
            group=group,
            id=1
        )
        elec = self.nwbfile.electrodes[0]
        self.assertEqual(elec.index[0], 1)
        self.assertEqual(elec.iloc[0]['x'], 1.0)
        self.assertEqual(elec.iloc[0]['y'], 2.0)
        self.assertEqual(elec.iloc[0]['z'], 3.0)
        self.assertEqual(elec.iloc[0]['location'], 'CA1')
        self.assertEqual(elec.iloc[0]['filtering'], 'none')
        self.assertEqual(elec.iloc[0]['group'], group)

    def test_add_electrode_some_opt(self):
        dev1 = self.nwbfile.create_device(name='dev1')
        group = self.nwbfile.create_electrode_group(
            name='tetrode1',
            description='tetrode description',
            location='tetrode location',
            device=dev1
        )
        self.nwbfile.add_electrode(
            x=1.0, y=2.0, z=3.0,
            imp=-1.0,
            location='CA1',
            filtering='none',
            group=group,
            id=1,
            rel_x=4.0, rel_y=5.0, rel_z=6.0,
            reference='ref1'
        )
        self.nwbfile.add_electrode(
            x=1.0, y=2.0, z=3.0,
            imp=-1.0,
            location='CA1',
            filtering='none',
            group=group,
            id=2,
            rel_x=7.0, rel_y=8.0, rel_z=9.0,
            reference='ref2'
        )
        elec = self.nwbfile.electrodes[0]
        self.assertEqual(elec.iloc[0]['rel_x'], 4.0)
        self.assertEqual(elec.iloc[0]['rel_y'], 5.0)
        self.assertEqual(elec.iloc[0]['rel_z'], 6.0)
        self.assertEqual(elec.iloc[0]['reference'], 'ref1')
        elec = self.nwbfile.electrodes[1]
        self.assertEqual(elec.iloc[0]['rel_x'], 7.0)
        self.assertEqual(elec.iloc[0]['rel_y'], 8.0)
        self.assertEqual(elec.iloc[0]['rel_z'], 9.0)
        self.assertEqual(elec.iloc[0]['reference'], 'ref2')

    def test_add_electrode_missing_location(self):
        """
        Test the case where the user creates an electrode table region with
        indexes that are out of range of the amount of electrodes added.
        """
        nwbfile = NWBFile('a', 'b', datetime.now(tzlocal()))
        device = nwbfile.create_device('a')
        elecgrp = nwbfile.create_electrode_group('a', 'b', device=device, location='a')
        msg = "The 'location' argument is required when creating an electrode."
        with self.assertRaisesWith(ValueError, msg):
            nwbfile.add_electrode(group=elecgrp, id=0)

    def test_add_electrode_missing_group(self):
        """
        Test the case where the user creates an electrode table region with
        indexes that are out of range of the amount of electrodes added.
        """
        nwbfile = NWBFile('a', 'b', datetime.now(tzlocal()))
        msg = "The 'group' argument is required when creating an electrode."
        with self.assertRaisesWith(ValueError, msg):
            nwbfile.add_electrode(location='a', id=0)

    def test_all_children(self):
        ts1 = TimeSeries('test_ts1', [0, 1, 2, 3, 4, 5], 'grams', timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5])
        ts2 = TimeSeries('test_ts2', [0, 1, 2, 3, 4, 5], 'grams', timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5])
        self.nwbfile.add_acquisition(ts1)
        self.nwbfile.add_acquisition(ts2)
        name = 'example_electrode_group'
        desc = 'An example electrode'
        loc = 'an example location'
        device = self.nwbfile.create_device('a fake device')
        elecgrp = self.nwbfile.create_electrode_group(name, desc, loc, device)
        children = self.nwbfile.all_children()
        self.assertIn(ts1, children)
        self.assertIn(ts2, children)
        self.assertIn(device, children)
        self.assertIn(elecgrp, children)

    def test_fail_if_source_script_file_name_without_source_script(self):
        with self.assertRaises(ValueError):
            # <-- source_script_file_name without source_script is not allowed
            NWBFile('a test session description for a test NWBFile', 'FILE123', self.start,
                    source_script=None,
                    source_script_file_name='nofilename')

    def test_get_neurodata_type(self):
        ts1 = TimeSeries('test_ts1', [0, 1, 2, 3, 4, 5], 'grams', timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5])
        ts2 = TimeSeries('test_ts2', [0, 1, 2, 3, 4, 5], 'grams', timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5])
        self.nwbfile.add_acquisition(ts1)
        self.nwbfile.add_acquisition(ts2)
        p1 = ts1.get_ancestor(neurodata_type='NWBFile')
        self.assertIs(p1, self.nwbfile)
        p2 = ts2.get_ancestor(neurodata_type='NWBFile')
        self.assertIs(p2, self.nwbfile)

    def test_print_units(self):
        self.nwbfile.add_unit(spike_times=[1., 2., 3.])
        expected = """units pynwb.misc.Units at 0x%d
Fields:
  colnames: ['spike_times']
  columns: (
    spike_times_index <class 'hdmf.common.table.VectorIndex'>,
    spike_times <class 'hdmf.common.table.VectorData'>
  )
  description: Autogenerated by NWBFile
  id: id <class 'hdmf.common.table.ElementIdentifiers'>
  waveform_unit: volts
"""
        expected = expected % id(self.nwbfile.units)
        self.assertEqual(str(self.nwbfile.units), expected)

    def test_copy(self):
        self.nwbfile.add_unit(spike_times=[1., 2., 3.])
        device = self.nwbfile.create_device('a')
        elecgrp = self.nwbfile.create_electrode_group('a', 'b', device=device, location='a')
        self.nwbfile.add_electrode(x=1.0, location='a', group=elecgrp, id=0)
        self.nwbfile.add_electrode(x=2.0, location='b', group=elecgrp)
        elec_region = self.nwbfile.create_electrode_table_region([1], 'name')

        ts1 = TimeSeries('test_ts1', [0, 1, 2, 3, 4, 5], 'grams', timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5])
        ts2 = ElectricalSeries('test_ts2', [0, 1, 2, 3, 4, 5],
                               electrodes=elec_region, timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5])
        self.nwbfile.add_acquisition(ts1)
        self.nwbfile.add_acquisition(ts2)
        self.nwbfile.add_trial(start_time=50.0, stop_time=70.0)
        self.nwbfile.add_invalid_times_column('comments', 'description of reason for omitting time')
        self.nwbfile.create_processing_module('test_mod', 'test_description')
        self.nwbfile.create_time_intervals('custom_interval', 'a custom time interval')
        self.nwbfile.intervals['custom_interval'].add_interval(start_time=10., stop_time=20.)
        newfile = self.nwbfile.copy()

        # test dictionaries
        self.assertIs(self.nwbfile.devices['a'], newfile.devices['a'])
        self.assertIs(self.nwbfile.acquisition['test_ts1'], newfile.acquisition['test_ts1'])
        self.assertIs(self.nwbfile.acquisition['test_ts2'], newfile.acquisition['test_ts2'])
        self.assertIs(self.nwbfile.processing['test_mod'], newfile.processing['test_mod'])

        # test dynamic tables
        self.assertIsNot(self.nwbfile.electrodes, newfile.electrodes)
        self.assertIs(self.nwbfile.electrodes['x'], newfile.electrodes['x'])
        self.assertIsNot(self.nwbfile.units, newfile.units)
        self.assertIs(self.nwbfile.units['spike_times'], newfile.units['spike_times'])
        self.assertIsNot(self.nwbfile.trials, newfile.trials)
        self.assertIsNot(self.nwbfile.trials.parent, newfile.trials.parent)
        self.assertIs(self.nwbfile.trials.id, newfile.trials.id)
        self.assertIs(self.nwbfile.trials['start_time'], newfile.trials['start_time'])
        self.assertIs(self.nwbfile.trials['stop_time'], newfile.trials['stop_time'])
        self.assertIsNot(self.nwbfile.invalid_times, newfile.invalid_times)
        self.assertTupleEqual(self.nwbfile.invalid_times.colnames, newfile.invalid_times.colnames)
        self.assertIsNot(self.nwbfile.intervals['custom_interval'], newfile.intervals['custom_interval'])
        self.assertTupleEqual(self.nwbfile.intervals['custom_interval'].colnames,
                              newfile.intervals['custom_interval'].colnames)
        self.assertIs(self.nwbfile.intervals['custom_interval']['start_time'],
                      newfile.intervals['custom_interval']['start_time'])
        self.assertIs(self.nwbfile.intervals['custom_interval']['stop_time'],
                      newfile.intervals['custom_interval']['stop_time'])

    def test_multi_experimenters(self):
        self.nwbfile = NWBFile('a test session description for a test NWBFile',
                               'FILE123',
                               self.start,
                               experimenter=('experimenter1', 'experimenter2'))
        self.assertTupleEqual(self.nwbfile.experimenter, ('experimenter1', 'experimenter2'))

    def test_multi_publications(self):
        self.nwbfile = NWBFile('a test session description for a test NWBFile',
                               'FILE123',
                               self.start,
                               related_publications=('pub1', 'pub2'))
        self.assertTupleEqual(self.nwbfile.related_publications, ('pub1', 'pub2'))


class SubjectTest(TestCase):
    def setUp(self):
        self.subject = Subject(
            age='P90D',
            age__reference="birth",
            description='An unfortunate rat',
            genotype='WT',
            sex='M',
            species='Rattus norvegicus',
            subject_id='RAT123',
            weight='2 kg',
            date_of_birth=datetime(2017, 5, 1, 12, tzinfo=tzlocal()),
            strain='my_strain',
        )
        self.start = datetime(2017, 5, 1, 12, tzinfo=tzlocal())
        self.path = 'nwbfile_test.h5'
        self.nwbfile = NWBFile(
            'a test session description for a test NWBFile',
            'FILE123',
            self.start,
            experimenter='A test experimenter',
            lab='a test lab',
            institution='a test institution',
            experiment_description='a test experiment description',
            session_id='test1',
            subject=self.subject,
        )

    def test_constructor(self):
        self.assertEqual(self.subject.age, 'P90D')
        self.assertEqual(self.subject.age__reference, "birth")
        self.assertEqual(self.subject.description, 'An unfortunate rat')
        self.assertEqual(self.subject.genotype, 'WT')
        self.assertEqual(self.subject.sex, 'M')
        self.assertEqual(self.subject.species, 'Rattus norvegicus')
        self.assertEqual(self.subject.subject_id, 'RAT123')
        self.assertEqual(self.subject.weight, '2 kg')
        self.assertEqual(self.subject.date_of_birth, datetime(2017, 5, 1, 12, tzinfo=tzlocal()))
        self.assertEqual(self.subject.strain, 'my_strain')

    def test_nwbfile_constructor(self):
        self.assertIs(self.nwbfile.subject, self.subject)

    def test_weight_float(self):
        subject = Subject(
            subject_id='RAT123',
            weight=2.3,
        )
        self.assertEqual(subject.weight, '2.3 kg')

    def test_age_reference_arg_check(self):
        with self.assertRaisesWith(ValueError, "age__reference, if supplied, must be 'birth' or 'gestational'."):
            Subject(subject_id='RAT123', age='P90D', age__reference='brth')

    def test_age_regression_1(self):
        subject = Subject(
            age='P90D',
            description='An unfortunate rat',
            subject_id='RAT123',
        )

        self.assertEqual(subject.age, 'P90D')
        self.assertEqual(subject.age__reference, "birth")
        self.assertEqual(subject.description, 'An unfortunate rat')
        self.assertEqual(subject.subject_id, 'RAT123')

    def test_age_regression_2(self):
        subject = Subject(
            description='An unfortunate rat',
            subject_id='RAT123',
        )

        self.assertEqual(subject.description, 'An unfortunate rat')
        self.assertEqual(subject.subject_id, 'RAT123')

    def test_subject_age_duration(self):
        subject = Subject(
            subject_id='RAT123',
            age=timedelta(seconds=99999)
        )

        self.assertEqual(subject.age, "P1DT3H46M39S")


class TestCacheSpec(TestCase):
    """Test whether the file can be written and read when caching the spec."""

    def setUp(self):
        self.path = 'unittest_cached_spec.nwb'

    def tearDown(self):
        remove_test_file(self.path)

    def test_simple(self):
        nwbfile = NWBFile('sess_desc', 'identifier',
                          datetime.now(tzlocal()),
                          file_create_date=datetime.now(tzlocal()),
                          institution='University of California, San Francisco',
                          lab='Chang Lab')
        with NWBHDF5IO(self.path, 'w') as io:
            io.write(nwbfile)
        with NWBHDF5IO(self.path, 'r') as reader:
            nwbfile = reader.read()
            assert nwbfile.session_description == "sess_desc"


class TestNoCacheSpec(TestCase):
    """Test whether the file can be written and read when not caching the spec."""

    def setUp(self):
        self.path = 'unittest_cached_spec.nwb'

    def tearDown(self):
        remove_test_file(self.path)

    def test_simple(self):
        nwbfile = NWBFile('sess_desc', 'identifier',
                          datetime.now(tzlocal()),
                          file_create_date=datetime.now(tzlocal()),
                          institution='University of California, San Francisco',
                          lab='Chang Lab')
        with NWBHDF5IO(self.path, 'w') as io:
            io.write(nwbfile, cache_spec=False)

        with NWBHDF5IO(self.path, 'r') as reader:
            nwbfile = reader.read()
            assert nwbfile.session_description == "sess_desc"


class TestTimestampsRefDefault(TestCase):
    def setUp(self):
        self.start_time = datetime(2017, 5, 1, 12, 0, 0, tzinfo=tzlocal())
        self.nwbfile = NWBFile('test session description',
                               'TEST123',
                               self.start_time)

    def test_reftime_default(self):
        # 'timestamps_reference_time' should default to 'session_start_time'
        self.assertEqual(self.nwbfile.timestamps_reference_time, self.start_time)


class TestTimestampsRefAware(TestCase):
    def setUp(self):
        self.start_time = datetime(2017, 5, 1, 12, 0, 0, tzinfo=tzlocal())
        self.ref_time_notz = datetime(1979, 1, 1, 0, 0, 0)

    def test_reftime_tzaware(self):
        with self.assertRaises(ValueError):
            # 'timestamps_reference_time' must be a timezone-aware datetime
            NWBFile('test session description',
                    'TEST124',
                    self.start_time,
                    timestamps_reference_time=self.ref_time_notz)


class TestTimezone(TestCase):
    def test_raise_warning__add_missing_timezone(self):
        with self.assertWarnsWith(UserWarning, "Date is missing timezone information. Updating to local timezone."):
            _add_missing_timezone(datetime(2017, 5, 1, 12))
