import os
from datetime import datetime
from dateutil.tz import tzlocal, tzutc

import pandas as pd
import numpy as np

from pynwb.form.build import GroupBuilder, DatasetBuilder
from pynwb.form.backends.hdf5 import HDF5IO

from pynwb import NWBFile, TimeSeries
from pynwb.file import Subject
from pynwb.ecephys import Clustering
from pynwb.epoch import TimeIntervals
from pynwb.misc import Units

from . import base


class TestNWBFileIO(base.TestMapNWBContainer):

    def setUp(self):
        self.start_time = datetime(1970, 1, 1, 12, tzinfo=tzutc())
        self.ref_time = datetime(1979, 1, 1, 0, tzinfo=tzutc())
        self.create_date = datetime(2017, 4, 15, 12, tzinfo=tzlocal())
        super(TestNWBFileIO, self).setUp()
        self.path = "test_pynwb_io_hdf5.h5"

    def setUpBuilder(self):
        ts_builder = GroupBuilder('test_timeseries',
                                  attributes={'namespace': base.CORE_NAMESPACE,
                                              'neurodata_type': 'TimeSeries',
                                              'comments': 'no comments',
                                              'description': 'no description',
                                              'help': 'General time series object'},
                                  datasets={'data': DatasetBuilder('data', list(range(100, 200, 10)),
                                                                   attributes={'unit': 'SIunit',
                                                                               'conversion': 1.0,
                                                                               'resolution': 0.1}),
                                            'timestamps': DatasetBuilder('timestamps', list(range(10)),
                                                                         attributes={'unit': 'Seconds',
                                                                                     'interval': 1})})

        module_builder = GroupBuilder('test_module',
                                      attributes={'namespace': base.CORE_NAMESPACE,
                                                  'neurodata_type': 'ProcessingModule',
                                                  'help': 'A collection of analysis outputs from processing of data',
                                                  'description': 'a test module'},
                                      groups={
                                          'Clustering':
                                          GroupBuilder('Clustering',
                                                       attributes={
                                                           'help': 'Clustered spike data, whether from automatic clustering tools (eg, klustakwik) or as a result of manual sorting',  # noqa: E501
                                                           'neurodata_type': 'Clustering',
                                                           'namespace': base.CORE_NAMESPACE},
                                                       datasets={
                                                           'num': DatasetBuilder('num', [0, 1, 2, 0, 1, 2]),
                                                           'times': DatasetBuilder('times', list(range(10, 61, 10))),
                                                           'peak_over_rms':
                                                           DatasetBuilder('peak_over_rms', [100, 101, 102]),
                                                           'description':
                                                           DatasetBuilder('description',
                                                                          "A fake Clustering interface")})})

        general_builder = GroupBuilder('general',
                                       datasets={
                                            'experimenter': DatasetBuilder('experimenter', 'test experimenter'),
                                            'stimulus': DatasetBuilder('stimulus', 'test stimulus notes'),
                                            'experiment_description': DatasetBuilder('experiment_description',
                                                                                     'test experiment description'),
                                            'data_collection': DatasetBuilder('data_collection',
                                                                              'test data collection notes'),
                                            'institution': DatasetBuilder('institution', 'nomad'),
                                            'lab': DatasetBuilder('lab', 'nolab'),
                                            'notes': DatasetBuilder('notes', 'nonotes'),
                                            'pharmacology': DatasetBuilder('pharmacology', 'nopharmacology'),
                                            'protocol': DatasetBuilder('protocol', 'noprotocol'),
                                            'related_publications': DatasetBuilder('related_publications', 'nopubs'),
                                            'session_id': DatasetBuilder('session_id', '007'),
                                            'slices': DatasetBuilder('slices', 'noslices'),
                                            'source_script': DatasetBuilder('source_script', 'nosources',
                                                                            attributes={'file_name': 'nofilename'}),
                                            'surgery': DatasetBuilder('surgery', 'nosurgery'),
                                            'virus': DatasetBuilder('virus', 'novirus')}
                                       )

        return GroupBuilder('root',
                            groups={'acquisition': GroupBuilder(
                                'acquisition',
                                groups={'test_timeseries': ts_builder}),
                                    'analysis': GroupBuilder('analysis'),
                                    'general': general_builder,
                                    'processing': GroupBuilder('processing', groups={'test_module': module_builder}),
                                    'stimulus': GroupBuilder(
                                        'stimulus',
                                        groups={'presentation':
                                                GroupBuilder('presentation'),
                                                'templates': GroupBuilder('templates')})},
                            datasets={
                                'file_create_date':
                                DatasetBuilder('file_create_date', [self.create_date.isoformat()]),
                                'identifier': DatasetBuilder('identifier', 'TEST123'),
                                'session_description': DatasetBuilder('session_description', 'a test NWB File'),
                                'session_start_time': DatasetBuilder('session_start_time', self.start_time.isoformat()),
                                'timestamps_reference_time': DatasetBuilder('timestamps_reference_time',
                                                                            self.ref_time.isoformat())
                                },
                            attributes={'namespace': base.CORE_NAMESPACE,
                                        'nwb_version': '2.0b',
                                        'neurodata_type': 'NWBFile',
                                        'help': 'an NWB:N file for storing cellular-based neurophysiology data'})

    def setUpContainer(self):
        container = NWBFile('a test NWB File', 'TEST123',
                            self.start_time,
                            timestamps_reference_time=self.ref_time,
                            file_create_date=self.create_date,
                            experimenter='test experimenter',
                            stimulus_notes='test stimulus notes',
                            experiment_description='test experiment description',
                            data_collection='test data collection notes',
                            institution='nomad',
                            lab='nolab',
                            notes='nonotes',
                            pharmacology='nopharmacology',
                            protocol='noprotocol',
                            related_publications='nopubs',
                            session_id='007',
                            slices='noslices',
                            source_script='nosources',
                            surgery='nosurgery',
                            virus='novirus',
                            source_script_file_name='nofilename')
        self.ts = TimeSeries('test_timeseries', list(range(100, 200, 10)),
                             'SIunit', timestamps=list(range(10)), resolution=0.1)
        container.add_acquisition(self.ts)
        self.mod = container.create_processing_module('test_module',
                                                      'a test module')
        self.clustering = Clustering("A fake Clustering interface", [0, 1, 2, 0, 1, 2], [100, 101, 102],
                                     list(range(10, 61, 10)))
        self.mod.add_container(self.clustering)
        return container

    def test_children(self):
        self.assertIn(self.ts, self.container.children)
        self.assertIn(self.mod, self.container.children)
        self.assertIn(self.clustering, self.mod.children)

    def tearDown(self):
        if os.path.exists(self.path):
            os.remove(self.path)

    def test_write(self):
        hdf5io = HDF5IO(self.path, self.manager)
        hdf5io.write(self.container)
        hdf5io.close()
        # TODO add some asserts

    def test_read(self):
        hdf5io = HDF5IO(self.path, self.manager)
        hdf5io.write(self.container)
        hdf5io.close()
        hdf5io = HDF5IO(self.path, self.manager)
        container = hdf5io.read()
        self.assertIsInstance(container, NWBFile)
        raw_ts = container.acquisition
        self.assertEqual(len(raw_ts), 1)
        for v in raw_ts.values():
            self.assertIsInstance(v, TimeSeries)
        hdf5io.close()


class TestSubjectIO(base.TestDataInterfaceIO):

    def setUpContainer(self):
        return Subject(age='12 mo',
                       description='An unfortunate rat',
                       genotype='WT',
                       sex='M',
                       species='Rattus norvegicus',
                       subject_id='RAT123',
                       weight='2 lbs')

    def setUpBuilder(self):
        return GroupBuilder('subject',
                            attributes={'namespace': base.CORE_NAMESPACE,
                                        'neurodata_type': 'Subject',
                                        'help': 'Information about the subject'},
                            datasets={'age': DatasetBuilder('age', '12 mo'),
                                      'description': DatasetBuilder('description', 'An unfortunate rat'),
                                      'genotype': DatasetBuilder('genotype', 'WT'),
                                      'sex': DatasetBuilder('sex', 'M'),
                                      'species': DatasetBuilder('species', 'Rattus norvegicus'),
                                      'subject_id': DatasetBuilder('subject_id', 'RAT123'),
                                      'weight': DatasetBuilder('weight', '2 lbs')})

    def addContainer(self, nwbfile):
        ''' Should take an NWBFile object and add the container to it '''
        nwbfile.subject = self.container

    def getContainer(self, nwbfile):
        ''' Should take an NWBFile object and return the Container'''
        return nwbfile.subject


class TestEpochsRoundtrip(base.TestMapRoundTrip):

    def setUpContainer(self):
        # this will get ignored
        return TimeIntervals('epochs')

    def addContainer(self, nwbfile):
        nwbfile.add_epoch_column(
            name='temperature',
            description='average temperture (c) during epoch'
        )

        nwbfile.add_epoch(
            start_time=5.3,
            stop_time=6.1,
            timeseries=[],
            tags='ambient',
            temperature=26.4,
        )

        # reset the thing
        self.container = nwbfile.epochs

    def getContainer(self, nwbfile):
        return nwbfile.epochs


class TestEpochsRoundtripDf(base.TestMapRoundTrip):

    def setUpContainer(self):
        # this will get ignored
        return TimeIntervals('epochs')

    def addContainer(self, nwbfile):

        tsa, tsb = [
            TimeSeries(name='a', timestamps=np.linspace(0, 1, 11)),
            TimeSeries(name='b', timestamps=np.linspace(0.1, 5, 13)),
        ]

        nwbfile.add_acquisition(tsa)
        nwbfile.add_acquisition(tsb)

        nwbfile.epochs = TimeIntervals.from_dataframe(
            pd.DataFrame({
                'foo': [1, 2, 3, 4],
                'bar': ['fish', 'fowl', 'dog', 'cat'],
                'start_time': [0.2, 0.25, 0.30, 0.35],
                'stop_time': [0.25, 0.30, 0.40, 0.45],
                'timeseries': [[(2, 1, tsa)],
                               [(3, 1, tsa)],
                               [(3, 1, tsa)],
                               [(4, 1, tsa)]],
                'tags': [[], [], ['fizz', 'buzz'], ['qaz']]
            }),
            'epochs',
            columns=[
                {'name': 'foo', 'description': 'a column of integers'},
                {'name': 'bar', 'description': 'a column of strings'},
            ]
        )

        # reset the thing
        self.container = nwbfile.epochs

    def getContainer(self, nwbfile):
        return nwbfile.epochs


class TestUnitElectrodes(base.TestMapRoundTrip):

    def setUpContainer(self):
        # this will get ignored
        return Units('placeholder_units')

    def addContainer(self, nwbfile):
        device = nwbfile.create_device(name='trodes_rig123')
        electrode_name = 'tetrode1'
        description = "an example tetrode"
        location = "somewhere in the hippocampus"
        electrode_group = nwbfile.create_electrode_group(electrode_name,
                                                         description=description,
                                                         location=location,
                                                         device=device)
        for idx in [1, 2, 3, 4]:
            nwbfile.add_electrode(idx,
                                  x=1.0, y=2.0, z=3.0,
                                  imp=float(-idx),
                                  location='CA1', filtering='none',
                                  group=electrode_group)

        nwbfile.add_unit(id=1, electrodes=[1])
        nwbfile.add_unit(id=2, electrodes=[1])
        self.container = nwbfile.units

    def getContainer(self, nwbfile):
        return nwbfile.units
