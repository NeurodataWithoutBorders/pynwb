"""
Module for testing of the intracellular electrophysiology experiment metadata
tables originally created as part of the ndx-icephys-meta extension. These
are tested in this separate module to avoid crowding of the main test_icephys
test module and to allow us to test the main experiment metadata structures
separately.
"""
import numpy as np
from datetime import datetime
from dateutil.tz import tzlocal
from pandas.testing import assert_frame_equal
from numpy.testing import assert_array_equal
import warnings
import h5py


from pynwb.testing import TestCase, remove_test_file, create_icephys_stimulus_and_response
from pynwb.file import NWBFile
from pynwb.icephys import (
    VoltageClampStimulusSeries,
    VoltageClampSeries,
    CurrentClampStimulusSeries,
    IZeroClampSeries,
    SimultaneousRecordingsTable,
    SequentialRecordingsTable,
    RepetitionsTable,
    ExperimentalConditionsTable,
    IntracellularElectrode,
    CurrentClampSeries,
    IntracellularRecordingsTable
)
from pynwb.device import Device
from pynwb.base import TimeSeriesReferenceVectorData
from pynwb import NWBHDF5IO
from hdmf.utils import docval, popargs


class ICEphysMetaTestBase(TestCase):
    """
    Base helper class for setting up tests for the ndx-icephys-meta extension.
    """

    def setUp(self):
        # Create an example nwbfile with a device, intracellular electrode, stimulus, and response
        self.nwbfile = NWBFile(
            session_description='my first synthetic recording',
            identifier='EXAMPLE_ID',
            session_start_time=datetime.now(tzlocal()),
            experimenter='Dr. Bilbo Baggins',
            lab='Bag End Laboratory',
            institution='University of Middle Earth at the Shire',
            experiment_description='I went on an adventure with thirteen dwarves to reclaim vast treasures.',
            session_id='LONELYMTN'
        )
        self.device = self.nwbfile.create_device(name='Heka ITC-1600')
        self.electrode = self.nwbfile.create_icephys_electrode(
            name="elec0",
            description='a mock intracellular electrode',
            device=self.device
        )
        self.stimulus = VoltageClampStimulusSeries(
            name="ccss",
            data=[1, 2, 3, 4, 5],
            starting_time=123.6,
            rate=10e3,
            electrode=self.electrode,
            gain=0.02,
            sweep_number=np.uint64(15)
        )
        self.nwbfile.add_stimulus(self.stimulus)
        self.response = VoltageClampSeries(
            name='vcs',
            data=[0.1, 0.2, 0.3, 0.4, 0.5],
            conversion=1e-12,
            resolution=np.nan,
            starting_time=123.6,
            rate=20e3,
            electrode=self.electrode,
            gain=0.02,
            capacitance_slow=100e-12,
            resistance_comp_correction=70.0,
            sweep_number=np.uint64(15)
        )
        self.nwbfile.add_acquisition(self.response)
        self.path = 'test_icephys_meta_intracellularrecording.h5'

    def tearDown(self):
        remove_test_file(self.path)

    @docval({'name': 'ir',
             'type': IntracellularRecordingsTable,
             'doc': 'Intracellular recording to be added to the file before write',
             'default': None},
            {'name': 'sw',
             'type': SimultaneousRecordingsTable,
             'doc': 'SimultaneousRecordingsTable table to be added to the file before write',
             'default': None},
            {'name': 'sws',
             'type': SequentialRecordingsTable,
             'doc': 'SequentialRecordingsTable table to be added to the file before write',
             'default': None},
            {'name': 'repetitions',
             'type': RepetitionsTable,
             'doc': 'RepetitionsTable table to be added to the file before write',
             'default': None},
            {'name': 'cond',
             'type': ExperimentalConditionsTable,
             'doc': 'ExperimentalConditionsTable table to be added to the file before write',
             'default': None})
    def write_test_helper(self, **kwargs):
        """
        Internal helper function to roundtrip an ICEphys file with the given set of ICEphys tables
        """
        ir, sw, sws, repetitions, cond = popargs('ir', 'sw', 'sws', 'repetitions', 'cond', kwargs)

        if ir is not None:
            self.nwbfile.intracellular_recordings = ir
        if sw is not None:
            self.nwbfile.icephys_simultaneous_recordings = sw
        if sws is not None:
            self.nwbfile.icephys_sequential_recordings = sws
        if repetitions is not None:
            self.nwbfile.icephys_repetitions = repetitions
        if cond is not None:
            self.nwbfile.icephys_experimental_conditions = cond

        # Write our test file
        with NWBHDF5IO(self.path, 'w') as io:
            io.write(self.nwbfile)

        # Test that we can read the file
        with NWBHDF5IO(self.path, 'r') as io:
            infile = io.read()
            if ir is not None:
                in_ir = infile.intracellular_recordings
                self.assertIsNotNone(in_ir)
                to_dataframe_kwargs = dict(electrode_refs_as_objectids=True,
                                           stimulus_refs_as_objectids=True,
                                           response_refs_as_objectids=True)
                assert_frame_equal(ir.to_dataframe(**to_dataframe_kwargs), in_ir.to_dataframe(**to_dataframe_kwargs))
            if sw is not None:
                in_sw = infile.icephys_simultaneous_recordings
                self.assertIsNotNone(in_sw)
                self.assertListEqual(in_sw['recordings'].target.data[:].tolist(), sw['recordings'].target.data[:])
                self.assertEqual(in_sw['recordings'].target.table.object_id, sw['recordings'].target.table.object_id)
            if sws is not None:
                in_sws = infile.icephys_sequential_recordings
                self.assertIsNotNone(in_sws)
                self.assertListEqual(in_sws['simultaneous_recordings'].target.data[:].tolist(),
                                     sws['simultaneous_recordings'].target.data[:])
                self.assertEqual(in_sws['simultaneous_recordings'].target.table.object_id,
                                 sws['simultaneous_recordings'].target.table.object_id)
            if repetitions is not None:
                in_repetitions = infile.icephys_repetitions
                self.assertIsNotNone(in_repetitions)
                self.assertListEqual(in_repetitions['sequential_recordings'].target.data[:].tolist(),
                                     repetitions['sequential_recordings'].target.data[:])
                self.assertEqual(in_repetitions['sequential_recordings'].target.table.object_id,
                                 repetitions['sequential_recordings'].target.table.object_id)
            if cond is not None:
                in_cond = infile.icephys_experimental_conditions
                self.assertIsNotNone(in_cond)
                self.assertListEqual(in_cond['repetitions'].target.data[:].tolist(),
                                     cond['repetitions'].target.data[:])
                self.assertEqual(in_cond['repetitions'].target.table.object_id,
                                 cond['repetitions'].target.table.object_id)


class IntracellularElectrodesTableTests(TestCase):
    """
    The IntracellularElectrodesTable is covered by the
    IntracellularRecordingsTableTests as this table is part of that table.
    """
    pass


class IntracellularStimuliTableTests(TestCase):
    """
    The IntracellularStimuliTable is covered by the
    IntracellularRecordingsTableTests as this table is part of that table.
    """
    pass


class IntracellularResponsesTableTests(TestCase):
    """
    The IntracellularResponsesTable is covered by the
    IntracellularRecordingsTableTests as this table is part of that table.
    """
    pass


class IntracellularRecordingsTableTests(ICEphysMetaTestBase):
    """
    Class for testing the IntracellularRecordingsTable Container
    """

    def test_init(self):
        ret = IntracellularRecordingsTable()
        self.assertEqual(ret.name, 'intracellular_recordings')

    def test_add_row(self):
        # Add a row to our IR table
        ir = IntracellularRecordingsTable()

        row_index = ir.add_recording(
            electrode=self.electrode,
            stimulus=self.stimulus,
            response=self.response,
            id=np.int64(10)
        )
        # Test that we get the correct row index back
        self.assertEqual(row_index, 0)
        # Read our first (and only) row and assert that it is correct
        res = ir[0]
        # Confirm that slicing one row give the same result as converting the whole table, which has only one row
        assert_frame_equal(ir.to_dataframe(), res)
        # Check the row id
        self.assertEqual(res.index[0], 10)
        # Check electrodes
        self.assertIs(res[('electrodes', 'electrode')].iloc[0], self.electrode)
        # Check the stimulus
        self.assertTupleEqual(res[('stimuli', 'stimulus')].iloc[0], (0, 5, self.stimulus))
        # Check the response
        self.assertTupleEqual(res[('responses', 'response')].iloc[0], (0, 5, self.response))
        # Test writing out ir table
        self.write_test_helper(ir)

    def test_add_row_incompatible_types(self):
        # Add a row that mixes CurrentClamp and VoltageClamp data
        sweep_number = 15
        local_stimulus = CurrentClampStimulusSeries(
            name="ccss_"+str(sweep_number),
            data=[1, 2, 3, 4, 5],
            starting_time=123.6,
            rate=10e3,
            electrode=self.electrode,
            gain=0.1,
            sweep_number=np.uint64(sweep_number)
        )
        ir = IntracellularRecordingsTable()
        with self.assertRaises(ValueError):
            _ = ir.add_recording(
                electrode=self.electrode,
                stimulus=local_stimulus,
                response=self.response,
                id=np.int64(10)
            )

    def test_error_if_IZeroClampSeries_with_stimulus(self):
        local_response = IZeroClampSeries(
            name="ccss",
            data=[1, 2, 3, 4, 5],
            starting_time=123.6,
            rate=10e3,
            electrode=self.electrode,
            gain=0.02,
            sweep_number=np.uint64(100000)
        )
        ir = IntracellularRecordingsTable()
        with self.assertRaises(ValueError):
            _ = ir.add_recording(
                electrode=self.electrode,
                stimulus=self.stimulus,
                response=local_response,
                id=np.int64(10)
            )

    def test_noerror_if_IZeroClampSeries(self):
        local_response = IZeroClampSeries(
            name="ccss",
            data=[1, 2, 3, 4, 5],
            starting_time=123.6,
            rate=10e3,
            electrode=self.electrode,
            gain=0.02,
            sweep_number=np.uint64(100000)
        )
        ir = IntracellularRecordingsTable()
        try:
            _ = ir.add_recording(
                electrode=self.electrode,
                response=local_response,
                id=np.int64(10)
            )
        except ValueError as e:
            self.fail("Adding IZeroClampSeries falsely resulted in error" + str(e))

    def test_inconsistent_PatchClampSeries(self):
        local_electrode = self.nwbfile.create_icephys_electrode(
            name="elec1",
            description='a mock intracellular electrode',
            device=self.device
        )
        local_stimulus = VoltageClampStimulusSeries(
            name="ccss",
            data=[1, 2, 3, 4, 5],
            starting_time=123.6,
            rate=10e3,
            electrode=local_electrode,
            gain=0.02,
            sweep_number=np.uint64(100000)
        )
        ir = IntracellularRecordingsTable()
        with self.assertRaises(ValueError):
            _ = ir.add_recording(
                electrode=self.electrode,
                stimulus=local_stimulus,
                response=self.response,
                id=np.int64(10)
            )

    def test_add_row_no_response(self):
        ir = IntracellularRecordingsTable()
        row_index = ir.add_recording(
            electrode=self.electrode,
            stimulus=self.stimulus,
            response=None,
            id=np.int64(10)
        )
        res = ir[0]
        # Check the ID
        self.assertEqual(row_index, 0)
        self.assertEqual(res.index[0], 10)
        # Check the row id
        self.assertEqual(res.index[0], 10)
        # Check electrodes
        self.assertIs(res[('electrodes', 'electrode')].iloc[0], self.electrode)
        # Check the stimulus
        self.assertTupleEqual(res[('stimuli', 'stimulus')].iloc[0], (0, 5, self.stimulus))
        # Check the response
        self.assertTrue(isinstance(res[('responses', 'response')].iloc[0],
                                   TimeSeriesReferenceVectorData.TIME_SERIES_REFERENCE_TUPLE))
        # Test writing out ir table
        self.write_test_helper(ir)

    def test_add_row_no_stimulus(self):
        ir = IntracellularRecordingsTable()
        row_index = ir.add_recording(
            electrode=self.electrode,
            stimulus=None,
            response=self.response,
            id=np.int64(10)
        )
        res = ir[0]
        # Check the ID
        self.assertEqual(row_index, 0)
        self.assertEqual(res.index[0], 10)
        # Check the row id
        self.assertEqual(res.index[0], 10)
        # Check electrodes
        self.assertIs(res[('electrodes', 'electrode')].iloc[0], self.electrode)
        # Check the stimulus
        self.assertTrue(isinstance(res[('stimuli', 'stimulus')].iloc[0],
                                   TimeSeriesReferenceVectorData.TIME_SERIES_REFERENCE_TUPLE))
        # Check the response
        self.assertTupleEqual(res[('responses', 'response')].iloc[0], (0, 5, self.response))
        # Test writing out ir table
        self.write_test_helper(ir)

    def test_add_row_check_start_index_and_index_count_are_fixed(self):
        # Make sure -1 values are converted
        ir = IntracellularRecordingsTable()
        ir.add_recording(
            electrode=self.electrode,
            stimulus=self.stimulus,
            stimulus_start_index=-1,  # assert this is fixed to 0
            stimulus_index_count=-1,  # assert this is fixed to len(stimulus)
            response=None,
            response_start_index=0,   # assert this is fixed to -1
            response_index_count=10,  # assert this is fixed to -1
            id=np.int64(10)
        )
        res = ir[0]
        self.assertTupleEqual(res[('stimuli', 'stimulus')].iloc[0],
                              (0, len(self.stimulus.data), self.stimulus))
        self.assertTrue(isinstance(res[('responses', 'response')].iloc[0],
                                   TimeSeriesReferenceVectorData.TIME_SERIES_REFERENCE_TUPLE))
        # Make sure single -1 values are converted
        ir = IntracellularRecordingsTable()
        ir.add_recording(
            electrode=self.electrode,
            stimulus=self.stimulus,
            stimulus_start_index=2,
            id=np.int64(10)
        )
        res = ir[0]
        self.assertTupleEqual(res[('stimuli', 'stimulus')].iloc[0],
                              (2, len(self.stimulus.data)-2, self.stimulus))
        # Make sure single -1 values are converted
        ir = IntracellularRecordingsTable()
        ir.add_recording(
            electrode=self.electrode,
            stimulus=self.stimulus,
            stimulus_index_count=2,
            id=np.int64(10)
        )
        res = ir[0]
        self.assertTupleEqual(res[('stimuli', 'stimulus')].iloc[0],
                              (0, 2, self.stimulus))

    def test_add_row_index_out_of_range(self):
        # Stimulus/Response start_index to large
        with self.assertRaises(IndexError):
            ir = IntracellularRecordingsTable()
            ir.add_recording(
                electrode=self.electrode,
                stimulus=self.stimulus,
                stimulus_start_index=10,
                response=self.response,
                id=np.int64(10)
            )
        with self.assertRaises(IndexError):
            ir = IntracellularRecordingsTable()
            ir.add_recording(
                electrode=self.electrode,
                stimulus=self.stimulus,
                response_start_index=10,
                response=self.response,
                id=np.int64(10)
            )
        with self.assertRaises(IndexError):
            ir = IntracellularRecordingsTable()
            ir.add_recording(
                electrode=self.electrode,
                stimulus_template=self.stimulus,
                stimulus_template_start_index=10,
                response=self.response,
                id=np.int64(10)
            )
        # Stimulus/Response index count too large
        with self.assertRaises(IndexError):
            ir = IntracellularRecordingsTable()
            ir.add_recording(
                electrode=self.electrode,
                stimulus=self.stimulus,
                stimulus_index_count=10,
                response=self.response,
                id=np.int64(10)
            )
        with self.assertRaises(IndexError):
            ir = IntracellularRecordingsTable()
            ir.add_recording(
                electrode=self.electrode,
                stimulus=self.stimulus,
                response_index_count=10,
                response=self.response,
                id=np.int64(10)
            )
        with self.assertRaises(IndexError):
            ir = IntracellularRecordingsTable()
            ir.add_recording(
                electrode=self.electrode,
                stimulus_template=self.stimulus,
                stimulus_template_index_count=10,
                response=self.response,
                id=np.int64(10)
            )
        # Stimulus/Response start+count combination too large
        with self.assertRaises(IndexError):
            ir = IntracellularRecordingsTable()
            ir.add_recording(
                electrode=self.electrode,
                stimulus=self.stimulus,
                stimulus_start_index=3,
                stimulus_index_count=4,
                response=self.response,
                id=np.int64(10)
            )
        with self.assertRaises(IndexError):
            ir = IntracellularRecordingsTable()
            ir.add_recording(
                electrode=self.electrode,
                stimulus=self.stimulus,
                response_start_index=3,
                response_index_count=4,
                response=self.response,
                id=np.int64(10)
            )
        with self.assertRaises(IndexError):
            ir = IntracellularRecordingsTable()
            ir.add_recording(
                electrode=self.electrode,
                stimulus_template=self.stimulus,
                stimulus_template_start_index=3,
                stimulus_template_index_count=4,
                response=self.response,
                id=np.int64(10)
            )

    def test_add_row_no_stimulus_and_response(self):
        with self.assertRaises(ValueError):
            ir = IntracellularRecordingsTable()
            ir.add_recording(
                electrode=self.electrode,
                stimulus=None,
                response=None
            )

    def test_add_row_with_stimulus_template(self):
        ir = IntracellularRecordingsTable()
        ir.add_recording(
            electrode=self.electrode,
            stimulus=self.stimulus,
            stimulus_template=self.stimulus,
            response=self.response,
            id=np.int64(10)
        )

    def test_add_stimulus_template_column(self):
        ir = IntracellularRecordingsTable()
        ir.add_column(name='stimulus_template',
                      description='test column',
                      category='stimuli',
                      col_cls=TimeSeriesReferenceVectorData)

    def test_add_row_with_no_stimulus_template_when_stimulus_template_column_exists(self):
        ir = IntracellularRecordingsTable()
        ir.add_recording(electrode=self.electrode,
                         stimulus=self.stimulus,
                         response=self.response,
                         stimulus_template=self.stimulus,
                         id=np.int64(10))

        # add row with only stimulus when stimulus template column already exists
        ir.add_recording(electrode=self.electrode,
                         stimulus=self.stimulus,
                         id=np.int64(20))
        # add row with only response when stimulus template column already exists
        ir.add_recording(electrode=self.electrode,
                         response=self.stimulus,
                         id=np.int64(30))

    def test_add_column(self):
        ir = IntracellularRecordingsTable()
        ir.add_recording(
            electrode=self.electrode,
            stimulus=self.stimulus,
            response=self.response,
            id=np.int64(10)
        )
        ir.add_column(name='test', description='test column', data=np.arange(1))
        self.assertTupleEqual(ir.colnames, ('test',))

    def test_enforce_unique_id(self):
        """
        Test to ensure that unique ids are enforced on RepetitionsTable table
        """
        ir = IntracellularRecordingsTable()
        ir.add_recording(
            electrode=self.electrode,
            stimulus=self.stimulus,
            response=self.response,
            id=np.int64(10)
        )
        with self.assertRaises(ValueError):
            ir.add_recording(
                electrode=self.electrode,
                stimulus=self.stimulus,
                response=self.response,
                id=np.int64(10)
            )

    def test_basic_write(self):
        """
        Populate, write, and read the SimultaneousRecordingsTable container and other required containers
        """
        ir = IntracellularRecordingsTable()
        row_index = ir.add_recording(
            electrode=self.electrode,
            stimulus=self.stimulus,
            response=self.response,
            id=np.int64(10)
        )
        self.assertEqual(row_index, 0)
        ir.add_column(name='test', description='test column', data=np.arange(1))
        self.write_test_helper(ir=ir)

    def test_to_dataframe(self):
        # Add the intracelluar recordings
        # Create a table setup for testing a number of conditions
        electrode0 = self.electrode
        electrode1 = self.nwbfile.create_icephys_electrode(
            name="elec1",
            description='another mock intracellular electrode',
            device=self.device
        )
        for sweep_number in range(20):
            elec = (electrode0 if (sweep_number % 2 == 0) else electrode1)
            stim, resp = create_icephys_stimulus_and_response(sweep_number=np.uint64(sweep_number),
                                                              electrode=elec,
                                                              randomize_data=False)
            if sweep_number in [0, 10]:  # include missing stimuli
                stim = None
            self.nwbfile.add_intracellular_recording(electrode=elec,
                                                     stimulus=stim,
                                                     response=resp,
                                                     id=sweep_number)
        tags_data = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'C3',
                     'D1', 'D2', 'D3', 'A1', 'A2', 'B1', 'B2',
                     'C1', 'C2', 'C3', 'D1', 'D2', 'D3']
        self.nwbfile.intracellular_recordings.add_column(name='recording_tags',
                                                         data=tags_data,
                                                         description='String with a set of recording tags')
        # Test normal conversion to a dataframe
        df = self.nwbfile.intracellular_recordings.to_dataframe()
        expected_cols = [('intracellular_recordings', 'recording_tags'), ('electrodes', 'id'),
                         ('electrodes', 'electrode'), ('stimuli', 'id'), ('stimuli', 'stimulus'),
                         ('responses', 'id'), ('responses', 'response')]
        self.assertListEqual(df.columns.to_list(), expected_cols)
        self.assertListEqual(df[('intracellular_recordings', 'recording_tags')].to_list(), tags_data)
        # Test conversion with ignore category ids set
        df = self.nwbfile.intracellular_recordings.to_dataframe(ignore_category_ids=True)
        expected_cols_no_ids = [('intracellular_recordings', 'recording_tags'),
                                ('electrodes', 'electrode'), ('stimuli', 'stimulus'),
                                ('responses', 'response')]
        self.assertListEqual(df.columns.to_list(), expected_cols_no_ids)
        # Test conversion with stimulus_refs_as_objectids
        df = self.nwbfile.intracellular_recordings.to_dataframe(stimulus_refs_as_objectids=True)
        self.assertListEqual(df.columns.to_list(), expected_cols)
        expects_stim_col = [e if e[2] is None else (e[0], e[1], e[2].object_id)
                            for e in self.nwbfile.intracellular_recordings[('stimuli', 'stimulus')][:]]
        self.assertListEqual(df[('stimuli', 'stimulus')].tolist(), expects_stim_col)
        # Test conversion with response_refs_as_objectids
        df = self.nwbfile.intracellular_recordings.to_dataframe(response_refs_as_objectids=True)
        self.assertListEqual(df.columns.to_list(), expected_cols)
        expects_resp_col = [e if e[2] is None else (e[0], e[1], e[2].object_id)
                            for e in self.nwbfile.intracellular_recordings[('responses', 'response')][:]]
        self.assertListEqual(df[('responses', 'response')].tolist(), expects_resp_col)
        # Test conversion with all options enabled
        df = self.nwbfile.intracellular_recordings.to_dataframe(ignore_category_ids=True,
                                                                stimulus_refs_as_objectids=True,
                                                                response_refs_as_objectids=True)
        self.assertListEqual(df.columns.to_list(), expected_cols_no_ids)
        self.assertListEqual(df[('stimuli', 'stimulus')].tolist(), expects_stim_col)
        self.assertListEqual(df[('responses', 'response')].tolist(), expects_resp_col)

    def test_round_trip_container_no_data(self):
        """Test read and write the container by itself"""
        curr = IntracellularRecordingsTable()
        with NWBHDF5IO(self.path, 'w') as io:
            io.write(curr)
        with NWBHDF5IO(self.path, 'r') as io:
            incon = io.read(skip_version_check=True)
            self.assertListEqual(incon.categories, curr.categories)
            for n in curr.categories:
                # empty columns from file have dtype int64 or float64 but empty in-memory columns have dtype object
                assert_frame_equal(incon[n], curr[n], check_dtype=False, check_index_type=False)

    def test_write_with_stimulus_template(self):
        """
        Populate, write, and read the SimultaneousRecordingsTable container and other required containers
        """
        local_nwbfile = NWBFile(
            session_description='my first synthetic recording',
            identifier='EXAMPLE_ID',
            session_start_time=datetime.now(tzlocal()),
            experimenter='Dr. Bilbo Baggins',
            lab='Bag End Laboratory',
            institution='University of Middle Earth at the Shire',
            experiment_description='I went on an adventure with thirteen dwarves to reclaim vast treasures.',
            session_id='LONELYMTN'
        )
        # Add a device
        local_device = local_nwbfile.create_device(name='Heka ITC-1600')
        local_electrode = local_nwbfile.create_icephys_electrode(
            name="elec0",
            description='a mock intracellular electrode',
            device=local_device
        )
        local_stimulus = VoltageClampStimulusSeries(
            name="ccss",
            data=[1, 2, 3, 4, 5],
            starting_time=123.6,
            rate=10e3,
            electrode=local_electrode,
            gain=0.02,
            sweep_number=np.uint64(15)
        )
        local_response = VoltageClampSeries(
            name='vcs',
            data=[0.1, 0.2, 0.3, 0.4, 0.5],
            conversion=1e-12,
            resolution=np.nan,
            starting_time=123.6,
            rate=20e3,
            electrode=local_electrode,
            gain=0.02,
            capacitance_slow=100e-12,
            resistance_comp_correction=70.0,
            sweep_number=np.uint64(15)
        )
        local_nwbfile.add_stimulus_template(local_stimulus)
        row_index = local_nwbfile.add_intracellular_recording(
            electrode=local_electrode,
            stimulus=local_stimulus,
            response=local_response,
            id=np.int64(10)
        )
        self.assertEqual(row_index, 0)
        # Write our test file
        with NWBHDF5IO(self.path, 'w') as io:
            io.write(local_nwbfile)

    def test_no_electrode(self):
        device = Device(name='device_name')
        elec = IntracellularElectrode(
            name='test_iS',
            device=device,
            description='description',
            slice='slice',
            seal='seal',
            location='location',
            resistance='resistance',
            filtering='filtering',
            initial_access_resistance='initial_access_resistance',
            cell_id='this_cell',
        )

        cCSS = CurrentClampStimulusSeries(
            name="test_cCSS",
            data=np.ones((30,)),
            electrode=elec,
            gain=1.0,
            rate=100_000.,
        )

        cCS = CurrentClampSeries(
            name="test_cCS",
            data=np.ones((30,)),
            electrode=elec,
            gain=1.0,
            rate=100_000.,
        )

        # test retrieve electrode from stimulus (when both stimulus and response are given)
        itr = IntracellularRecordingsTable()
        itr.add_recording(stimulus=cCSS, response=cCS)
        self.assertEqual(itr["electrodes"].values[0], elec)
        del itr

        # test retrieve electrode from stimulus (when only stimulus is given)
        itr = IntracellularRecordingsTable()
        itr.add_recording(stimulus=cCSS, response=None)
        self.assertEqual(itr["electrodes"].values[0], elec)
        del itr

        # test retrieve electrode from response (when only response is given)
        itr = IntracellularRecordingsTable()
        itr.add_recording(stimulus=None, response=cCS)
        self.assertEqual(itr["electrodes"].values[0], elec)


class SimultaneousRecordingsTableTests(ICEphysMetaTestBase):
    """
    Test class for testing the SimultaneousRecordingsTable Container class
    """

    def test_init(self):
        """
        Test __init__ to make sure we can instantiate the SimultaneousRecordingsTable container
        """
        ir = IntracellularRecordingsTable()
        ret = SimultaneousRecordingsTable(intracellular_recordings_table=ir)
        self.assertIs(ret.recordings.table, ir)
        self.assertEqual(ret.name, 'simultaneous_recordings')

    def test_missing_intracellular_recordings_on_init(self):
        """
        Test that ValueError is raised when intracellular_recordings is missing. This is
        allowed only on read where the intracellular_recordings table is already set
        from the file.
        """
        with self.assertRaises(ValueError):
            _ = SimultaneousRecordingsTable()

    def test_add_simultaneous_recording(self):
        """
        Populate, write, and read the SimultaneousRecordingsTable container and other required containers
        """
        ir = IntracellularRecordingsTable()
        row_index = ir.add_recording(
            electrode=self.electrode,
            stimulus=self.stimulus,
            response=self.response,
            id=np.int64(10)
        )
        self.assertEqual(row_index, 0)
        self.assertEqual(len(ir), 1)
        sw = SimultaneousRecordingsTable(intracellular_recordings_table=ir)
        row_index = sw.add_simultaneous_recording(recordings=[row_index], id=100)
        self.assertEqual(row_index, 0)
        self.assertListEqual(sw.id[:], [100])
        self.assertListEqual(sw['recordings'].data, [1])
        self.assertListEqual(sw['recordings'].target.data[:], [0])

    def test_basic_write(self):
        """
        Populate, write, and read the SimultaneousRecordingsTable container and other required containers
        """
        ir = IntracellularRecordingsTable()
        row_index = ir.add_recording(
            electrode=self.electrode,
            stimulus=self.stimulus,
            response=self.response,
            id=np.int64(10)
        )
        self.assertEqual(row_index, 0)
        self.assertEqual(len(ir), 1)
        sw = SimultaneousRecordingsTable(intracellular_recordings_table=ir)
        row_index = sw.add_simultaneous_recording(recordings=[row_index])
        self.assertEqual(row_index, 0)
        self.write_test_helper(ir=ir, sw=sw)

    def test_enforce_unique_id(self):
        """
        Test to ensure that unique ids are enforced on RepetitionsTable table
        """
        ir = IntracellularRecordingsTable()
        ir.add_recording(
            electrode=self.electrode,
            stimulus=self.stimulus,
            response=self.response,
            id=np.int64(10)
        )
        sw = SimultaneousRecordingsTable(intracellular_recordings_table=ir)
        sw.add_simultaneous_recording(recordings=[0], id=np.int64(10))
        with self.assertRaises(ValueError):
            sw.add_simultaneous_recording(recordings=[0], id=np.int64(10))


class SequentialRecordingsTableTests(ICEphysMetaTestBase):
    """
    Test class for testing the SequentialRecordingsTable Container class
    """

    def test_init(self):
        """
        Test  __init__ to make sure we can instantiate the SequentialRecordingsTable container
        """
        ir = IntracellularRecordingsTable()
        sw = SimultaneousRecordingsTable(intracellular_recordings_table=ir)
        ret = SequentialRecordingsTable(simultaneous_recordings_table=sw)
        self.assertIs(ret.simultaneous_recordings.table, sw)
        self.assertEqual(ret.name, 'sequential_recordings')

    def test_missing_simultaneous_recordings_on_init(self):
        """
        Test that ValueError is raised when simultaneous_recordings is missing. This is
        allowed only on read where the simultaneous_recordings table is already set
        from the file.
        """
        with self.assertRaises(ValueError):
            _ = SequentialRecordingsTable()

    def test_basic_write(self):
        """
        Populate, write, and read the SequentialRecordingsTable container and other required containers
        """
        ir = IntracellularRecordingsTable()
        row_index = ir.add_recording(
            electrode=self.electrode,
            stimulus=self.stimulus,
            response=self.response,
            id=np.int64(10)
        )
        self.assertEqual(row_index, 0)
        sw = SimultaneousRecordingsTable(intracellular_recordings_table=ir)
        row_index = sw.add_simultaneous_recording(recordings=[0])
        self.assertEqual(row_index, 0)
        sws = SequentialRecordingsTable(sw)
        row_index = sws.add_sequential_recording(simultaneous_recordings=[0, ], stimulus_type='MyStimStype')
        self.assertEqual(row_index, 0)
        self.write_test_helper(ir=ir, sw=sw, sws=sws)

    def test_enforce_unique_id(self):
        """
        Test to ensure that unique ids are enforced on RepetitionsTable table
        """
        ir = IntracellularRecordingsTable()
        ir.add_recording(
            electrode=self.electrode,
            stimulus=self.stimulus,
            response=self.response,
            id=np.int64(10)
        )
        sw = SimultaneousRecordingsTable(intracellular_recordings_table=ir)
        sw.add_simultaneous_recording(recordings=[0])
        sws = SequentialRecordingsTable(sw)
        sws.add_sequential_recording(simultaneous_recordings=[0, ], id=np.int64(10), stimulus_type='MyStimStype')
        with self.assertRaises(ValueError):
            sws.add_sequential_recording(simultaneous_recordings=[0, ], id=np.int64(10), stimulus_type='MyStimStype')


class RepetitionsTableTests(ICEphysMetaTestBase):
    """
    Test class for testing the RepetitionsTable Container class
    """

    def test_init(self):
        """
        Test  __init__ to make sure we can instantiate the RepetitionsTable container
        """
        ir = IntracellularRecordingsTable()
        sw = SimultaneousRecordingsTable(intracellular_recordings_table=ir)
        sws = SequentialRecordingsTable(simultaneous_recordings_table=sw)
        ret = RepetitionsTable(sequential_recordings_table=sws)
        self.assertIs(ret.sequential_recordings.table, sws)
        self.assertEqual(ret.name, 'repetitions')

    def test_missing_sequential_recordings_on_init(self):
        """
        Test that ValueError is raised when sequential_recordings is missing. This is
        allowed only on read where the sequential_recordings table is already set
        from the file.
        """
        with self.assertRaises(ValueError):
            _ = RepetitionsTable()

    def test_basic_write(self):
        """
        Populate, write, and read the RepetitionsTable container and other required containers
        """
        ir = IntracellularRecordingsTable()
        row_index = ir.add_recording(
            electrode=self.electrode,
            stimulus=self.stimulus,
            response=self.response,
            id=np.int64(10)
        )
        self.assertEqual(row_index, 0)
        sw = SimultaneousRecordingsTable(intracellular_recordings_table=ir)
        row_index = sw.add_simultaneous_recording(recordings=[0])
        self.assertEqual(row_index, 0)
        sws = SequentialRecordingsTable(sw)
        row_index = sws.add_sequential_recording(simultaneous_recordings=[0, ], stimulus_type='MyStimStype')
        self.assertEqual(row_index, 0)
        repetitions = RepetitionsTable(sequential_recordings_table=sws)
        repetitions.add_repetition(sequential_recordings=[0, ])
        self.write_test_helper(ir=ir, sw=sw, sws=sws, repetitions=repetitions)

    def test_enforce_unique_id(self):
        """
        Test to ensure that unique ids are enforced on RepetitionsTable table
        """
        ir = IntracellularRecordingsTable()
        ir.add_recording(
            electrode=self.electrode,
            stimulus=self.stimulus,
            response=self.response,
            id=np.int64(10)
        )
        sw = SimultaneousRecordingsTable(intracellular_recordings_table=ir)
        sw.add_simultaneous_recording(recordings=[0])
        sws = SequentialRecordingsTable(sw)
        sws.add_sequential_recording(simultaneous_recordings=[0, ], stimulus_type='MyStimStype')
        repetitions = RepetitionsTable(sequential_recordings_table=sws)
        repetitions.add_repetition(sequential_recordings=[0, ], id=np.int64(10))
        with self.assertRaises(ValueError):
            repetitions.add_repetition(sequential_recordings=[0, ], id=np.int64(10))


class ExperimentalConditionsTableTests(ICEphysMetaTestBase):
    """
    Test class for testing the ExperimentalConditionsTable Container class
    """

    def test_init(self):
        """
        Test  __init__ to make sure we can instantiate the ExperimentalConditionsTable container
        """
        ir = IntracellularRecordingsTable()
        sw = SimultaneousRecordingsTable(intracellular_recordings_table=ir)
        sws = SequentialRecordingsTable(simultaneous_recordings_table=sw)
        repetitions = RepetitionsTable(sequential_recordings_table=sws)
        ret = ExperimentalConditionsTable(repetitions_table=repetitions)
        self.assertIs(ret.repetitions.table, repetitions)
        self.assertEqual(ret.name, 'experimental_conditions')

    def test_missing_repetitions_on_init(self):
        """
        Test that ValueError is raised when repetitions is missing. This is
        allowed only on read where the repetitions table is already set
        from the file.
        """
        with self.assertRaises(ValueError):
            _ = ExperimentalConditionsTable()

    def test_basic_write(self):
        """
        Populate, write, and read the ExperimentalConditionsTable container and other required containers
        """
        ir = IntracellularRecordingsTable()
        row_index = ir.add_recording(electrode=self.electrode,
                                     stimulus=self.stimulus,
                                     response=self.response,
                                     id=np.int64(10))
        self.assertEqual(row_index, 0)
        sw = SimultaneousRecordingsTable(intracellular_recordings_table=ir)
        row_index = sw.add_simultaneous_recording(recordings=[0])
        self.assertEqual(row_index, 0)
        sws = SequentialRecordingsTable(sw)
        row_index = sws.add_sequential_recording(simultaneous_recordings=[0, ], stimulus_type='MyStimStype')
        self.assertEqual(row_index, 0)
        repetitions = RepetitionsTable(sequential_recordings_table=sws)
        row_index = repetitions.add_repetition(sequential_recordings=[0, ])
        self.assertEqual(row_index, 0)
        cond = ExperimentalConditionsTable(repetitions_table=repetitions)
        row_index = cond.add_experimental_condition(repetitions=[0, ])
        self.assertEqual(row_index, 0)
        self.write_test_helper(ir=ir, sw=sw, sws=sws, repetitions=repetitions, cond=cond)

    def test_enforce_unique_id(self):
        """
        Test to ensure that unique ids are enforced on RepetitionsTable table
        """
        ir = IntracellularRecordingsTable()
        ir.add_recording(electrode=self.electrode,
                         stimulus=self.stimulus,
                         response=self.response,
                         id=np.int64(10))
        sw = SimultaneousRecordingsTable(intracellular_recordings_table=ir)
        sw.add_simultaneous_recording(recordings=[0])
        sws = SequentialRecordingsTable(sw)
        sws.add_sequential_recording(simultaneous_recordings=[0, ], stimulus_type='MyStimStype')
        repetitions = RepetitionsTable(sequential_recordings_table=sws)
        repetitions.add_repetition(sequential_recordings=[0, ])
        cond = ExperimentalConditionsTable(repetitions_table=repetitions)
        cond.add_experimental_condition(repetitions=[0, ], id=np.int64(10))
        with self.assertRaises(ValueError):
            cond.add_experimental_condition(repetitions=[0, ], id=np.int64(10))


class NWBFileTests(TestCase):
    """
    Test class for testing the NWBFileTests Container class
    """
    def setUp(self):
        warnings.simplefilter("always")  # Trigger all warnings
        self.path = 'test_icephys_meta_intracellularrecording.h5'

    def tearDown(self):
        remove_test_file(self.path)

    def __get_icephysfile(self):
        """
        Create a dummy NWBFile instance
        """
        icefile = NWBFile(
            session_description='my first synthetic recording',
            identifier='EXAMPLE_ID',
            session_start_time=datetime.now(tzlocal())
        )
        return icefile

    def __add_device(self, icefile):
        return icefile.create_device(name='Heka ITC-1600')

    def __add_electrode(self, icefile, device):
        return icefile.create_icephys_electrode(name="elec0",
                                                description='a mock intracellular electrode',
                                                device=device)

    def __get_stimulus(self, electrode):
        """
        Create a dummy VoltageClampStimulusSeries
        """
        return VoltageClampStimulusSeries(
            name="ccss",
            data=[1, 2, 3, 4, 5],
            starting_time=123.6,
            rate=10e3,
            electrode=electrode,
            gain=0.02,
            sweep_number=np.uint64(15)
        )

    def __get_response(self, electrode):
        """
        Create a dummy VoltageClampSeries
        """
        return VoltageClampSeries(
            name='vcs',
            data=[0.1, 0.2, 0.3, 0.4, 0.5],
            conversion=1e-12,
            resolution=np.nan,
            starting_time=123.6,
            rate=20e3,
            electrode=electrode,
            gain=0.02,
            capacitance_slow=100e-12,
            resistance_comp_correction=70.0,
            sweep_number=np.uint64(15)
        )

    def test_deprecate_simultaneous_recordings_on_add_stimulus(self):
        """
        Test that warnings are raised if the user tries to use a simultaneous_recordings table
        """
        nwbfile = self.__get_icephysfile()
        device = self.__add_device(nwbfile)
        electrode = self.__add_electrode(nwbfile, device)
        stimulus = self.__get_stimulus(electrode=electrode)
        response = self.__get_response(electrode=electrode)
        # Make sure we warn if sweeptable is added on add_stimulus
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")  # Trigger all warnings
            nwbfile.add_stimulus(stimulus, use_sweep_table=True)
            self.assertEqual(len(w), 1)
            assert issubclass(w[-1].category, DeprecationWarning)
            # make sure we don't trigger the same deprecation warning twice
            nwbfile.add_acquisition(response, use_sweep_table=True)
            self.assertEqual(len(w), 1)

    def test_deprecate_sweeptable_on_add_stimulus_template(self):
        """
        Make sure we warn when using the sweep-table
        """
        nwbfile = self.__get_icephysfile()
        local_electrode = nwbfile.create_icephys_electrode(
            name="elec0",
            description='a mock intracellular electrode',
            device=nwbfile.create_device(name='Heka ITC-1600')
        )
        local_stimulus = VoltageClampStimulusSeries(
            name="ccss",
            data=[1, 2, 3, 4, 5],
            starting_time=123.6,
            rate=10e3,
            electrode=local_electrode,
            gain=0.02,
            sweep_number=np.uint64(15)
        )
        local_stimulus2 = VoltageClampStimulusSeries(
            name="ccss2",
            data=[1, 2, 3, 4, 5],
            starting_time=123.6,
            rate=10e3,
            electrode=local_electrode,
            gain=0.02,
            sweep_number=np.uint64(15)
        )
        with warnings.catch_warnings(record=True) as w:
            nwbfile.add_stimulus_template(local_stimulus, use_sweep_table=True)
            self.assertEqual(len(w), 1)
            assert issubclass(w[-1].category, DeprecationWarning)
            self.assertEqual(str(w[-1].message),
                             "Use of SweepTable is deprecated. Use the IntracellularRecordingsTable "
                             "instead. See also the  NWBFile.add_intracellular_recordings function.")
            # make sure we don't trigger the same deprecation warning twice
            nwbfile.add_stimulus_template(local_stimulus2, use_sweep_table=True)
            self.assertEqual(len(w), 1)

    def test_deprecate_sweepstable_on_add_acquistion(self):
        """
        Test that warnings are raised if the user tries to use a sweeps table
        """
        nwbfile = self.__get_icephysfile()
        device = self.__add_device(nwbfile)
        electrode = self.__add_electrode(nwbfile, device)
        stimulus = self.__get_stimulus(electrode=electrode)
        response = self.__get_response(electrode=electrode)
        # Make sure we warn if sweeptable is added on add_stimulus
        with warnings.catch_warnings(record=True) as w:
            nwbfile.add_acquisition(response, use_sweep_table=True)
            self.assertEqual(len(w), 1)
            assert issubclass(w[-1].category, DeprecationWarning)
            self.assertEqual(str(w[-1].message),
                             "Use of SweepTable is deprecated. Use the IntracellularRecordingsTable "
                             "instead. See also the  NWBFile.add_intracellular_recordings function.")
            # make sure we don't trigger the same deprecation warning twice
            nwbfile.add_stimulus(stimulus, use_sweep_table=True)
            self.assertEqual(len(w), 1)

    def test_deprecate_sweepstable_on_init(self):
        """
        Test that warnings are raised if the user tries to use a sweeps table
        """
        from pynwb.icephys import SweepTable
        with warnings.catch_warnings(record=True) as w:
            nwbfile = NWBFile(
                session_description='my first synthetic recording',
                identifier='EXAMPLE_ID',
                session_start_time=datetime.now(tzlocal()),
                sweep_table=SweepTable()
            )
            device = self.__add_device(nwbfile)
            electrode = self.__add_electrode(nwbfile, device)
            stimulus = self.__get_stimulus(electrode=electrode)
            self.assertEqual(len(w), 1)
            assert issubclass(w[-1].category, DeprecationWarning)
            # make sure we don't trigger the same deprecation warning twice
            nwbfile.add_stimulus(stimulus, use_sweep_table=True)
            self.assertEqual(len(w), 1)

    def test_deprectation_icephys_filtering_on_init(self):
        with warnings.catch_warnings(record=True) as w:
            nwbfile = NWBFile(
                session_description='my first synthetic recording',
                identifier='EXAMPLE_ID',
                session_start_time=datetime.now(tzlocal()),
                icephys_filtering='test filtering'
            )
            assert issubclass(w[-1].category, DeprecationWarning)
            self.assertEqual(nwbfile.icephys_filtering, 'test filtering')

    def test_icephys_filtering_roundtrip(self):
        # create the base file
        nwbfile = NWBFile(
            session_description='my first synthetic recording',
            identifier='EXAMPLE_ID',
            session_start_time=datetime.now(tzlocal())
        )
        # set the icephys_filtering attribute and make sure we get a deprecation warning
        with warnings.catch_warnings(record=True) as w:
            nwbfile.icephys_filtering = 'test filtering'
            assert issubclass(w[-1].category, DeprecationWarning)
        # write the test fil
        with NWBHDF5IO(self.path, 'w') as io:
            io.write(nwbfile)
        # read the test file and confirm icephys_filtering has been written
        with NWBHDF5IO(self.path, 'r') as io:
            with warnings.catch_warnings(record=True) as w:
                infile = io.read()
                self.assertEqual(len(w), 1)  # make sure a warning is being raised
                assert issubclass(w[0].category, DeprecationWarning)  # make sure it is a deprecation warning
                self.assertEqual(infile.icephys_filtering, 'test filtering')  # make sure the value is set

    def test_get_icephys_meta_parent_table(self):
        """
        Create the table hierarchy step-by-step and check that as we add tables the get_icephys_meta_parent_table
        returns the expected top table
        """
        local_nwbfile = NWBFile(
            session_description='my first synthetic recording',
            identifier='EXAMPLE_ID',
            session_start_time=datetime.now(tzlocal())
        )
        # Add a device
        local_device = local_nwbfile.create_device(name='Heka ITC-1600')
        local_electrode = local_nwbfile.create_icephys_electrode(
            name="elec0",
            description='a mock intracellular electrode',
            device=local_device
        )
        local_stimulus = VoltageClampStimulusSeries(
            name="ccss",
            data=[1, 2, 3, 4, 5],
            starting_time=123.6,
            rate=10e3,
            electrode=local_electrode,
            gain=0.02,
            sweep_number=np.uint64(15)
        )
        local_response = VoltageClampSeries(
            name='vcs',
            data=[0.1, 0.2, 0.3, 0.4, 0.5],
            conversion=1e-12,
            resolution=np.nan,
            starting_time=123.6,
            rate=20e3,
            electrode=local_electrode,
            gain=0.02,
            capacitance_slow=100e-12,
            resistance_comp_correction=70.0,
            sweep_number=np.uint64(15)
        )
        local_nwbfile.add_stimulus_template(local_stimulus)
        # Check that none of the table exist yet
        self.assertIsNone(local_nwbfile.get_icephys_meta_parent_table())
        # Add a recording and confirm that intracellular_recordings is the top table
        _ = local_nwbfile.add_intracellular_recording(
            electrode=local_electrode,
            stimulus=local_stimulus,
            response=local_response,
            id=np.int64(10)
        )
        self.assertIsInstance(local_nwbfile.get_icephys_meta_parent_table(),
                              IntracellularRecordingsTable)
        # Add a sweep and check that the simultaneous_recordings table is the top table
        _ = local_nwbfile.add_icephys_simultaneous_recording(recordings=[0])
        self.assertIsInstance(local_nwbfile.get_icephys_meta_parent_table(),
                              SimultaneousRecordingsTable)
        # Add a sweep_sequence and check that it is now our top table
        _ = local_nwbfile.add_icephys_sequential_recording(simultaneous_recordings=[0], stimulus_type="MyStimulusType")
        self.assertIsInstance(local_nwbfile.get_icephys_meta_parent_table(),
                              SequentialRecordingsTable)
        # Add a repetition and check that it is now our top table
        _ = local_nwbfile.add_icephys_repetition(sequential_recordings=[0])
        self.assertIsInstance(local_nwbfile.get_icephys_meta_parent_table(),
                              RepetitionsTable)
        # Add a condition and check that it is now our top table
        _ = local_nwbfile.add_icephys_experimental_condition(repetitions=[0])
        self.assertIsInstance(local_nwbfile.get_icephys_meta_parent_table(),
                              ExperimentalConditionsTable)

    def test_add_icephys_meta_full_roundtrip(self):
        """
        This test adds all data and then constructs step-by-step the full table structure
        Returns:

        """
        ####################################
        # Create our file and timeseries
        ###################################
        nwbfile = self.__get_icephysfile()
        device = self.__add_device(nwbfile)
        electrode = self.__add_electrode(nwbfile, device)
        # Add the data using standard methods from NWBFile
        stimulus = self.__get_stimulus(electrode=electrode)
        nwbfile.add_stimulus(stimulus)
        # Check that the deprecated sweep table has indeed not been created
        self.assertIsNone(nwbfile.sweep_table)
        response = self.__get_response(electrode=electrode)
        nwbfile.add_acquisition(response)
        # Check that the deprecated sweep table has indeed not been created
        self.assertIsNone(nwbfile.sweep_table)

        #############################################
        #  Test adding IntracellularRecordingsTable
        #############################################
        # Check that our IntracellularRecordingsTable table does not yet exist
        self.assertIsNone(nwbfile.intracellular_recordings)
        # Add an intracellular recording
        intracellular_recording_ids = [np.int64(10), np.int64(11)]
        nwbfile.add_intracellular_recording(
            electrode=electrode,
            stimulus=stimulus,
            response=response,
            id=intracellular_recording_ids[0]
        )
        nwbfile.add_intracellular_recording(
            electrode=electrode,
            stimulus=stimulus,
            response=response,
            id=intracellular_recording_ids[1]
        )
        # Check that the table has been created
        self.assertIsNotNone(nwbfile.intracellular_recordings)
        # Check that the values in our row are correct
        self.assertEqual(len(nwbfile.intracellular_recordings), 2)
        res = nwbfile.intracellular_recordings[0]
        # Check the ID
        self.assertEqual(res.index[0], intracellular_recording_ids[0])
        # Check electrodes
        self.assertIs(res[('electrodes', 'electrode')].iloc[0], electrode)
        # Check the stimulus
        self.assertTupleEqual(res[('stimuli', 'stimulus')].iloc[0], (0, 5, stimulus))
        # Check the response
        self.assertTupleEqual(res[('responses', 'response')].iloc[0], (0, 5, response))

        #############################################
        #  Test adding SimultaneousRecordingsTable
        #############################################
        # Confirm that our SimultaneousRecordingsTable table does not yet exist
        self.assertIsNone(nwbfile.icephys_simultaneous_recordings)
        # Add a sweep
        simultaneous_recordings_id = np.int64(12)
        recordings_indices = [0, 1]
        nwbfile.add_icephys_simultaneous_recording(recordings=recordings_indices, id=simultaneous_recordings_id)
        # Check that the SimultaneousRecordingsTable table has been added
        self.assertIsNotNone(nwbfile.icephys_simultaneous_recordings)
        # Check that the values for our icephys_simultaneous_recordings table are correct
        self.assertListEqual(nwbfile.icephys_simultaneous_recordings.id[:], [simultaneous_recordings_id])
        self.assertListEqual(nwbfile.icephys_simultaneous_recordings['recordings'].data, [2])
        self.assertListEqual(nwbfile.icephys_simultaneous_recordings['recordings'].target.data[:], [0, 1])
        res = nwbfile.icephys_simultaneous_recordings[0]
        # check the id value
        self.assertEqual(res.index[0],  simultaneous_recordings_id)
        # Check that our simultaneous recording contains 2 IntracellularRecording
        assert_array_equal(res.loc[simultaneous_recordings_id]['recordings'],
                           recordings_indices)

        #############################################
        #  Test adding a SweepSequence
        #############################################
        # Confirm that our SequentialRecordingsTable table does not yet exist
        self.assertIsNone(nwbfile.icephys_sequential_recordings)
        # Add a sweep
        sequential_recording_id = np.int64(15)
        simultaneous_recordings_indices = [0]
        nwbfile.add_icephys_sequential_recording(simultaneous_recordings=simultaneous_recordings_indices,
                                                 id=sequential_recording_id,
                                                 stimulus_type="MyStimulusType")
        # Check that the SimultaneousRecordingsTable table has been added
        self.assertIsNotNone(nwbfile.icephys_sequential_recordings)
        # Check that the values for our SimultaneousRecordingsTable table are correct
        res = nwbfile.icephys_sequential_recordings[0]
        # check the id value
        self.assertEqual(res.index[0], sequential_recording_id)
        # Check that our sequential recording contains 1 simultaneous recording
        assert_array_equal(res.loc[sequential_recording_id]['simultaneous_recordings'],
                           simultaneous_recordings_indices)

        #############################################
        #  Test adding a Run
        #############################################
        # Confirm that our RepetitionsTable table does not yet exist
        self.assertIsNone(nwbfile.icephys_repetitions)
        # Add a repetition
        sequential_recordings_indices = [0]
        repetition_id = np.int64(17)
        nwbfile.add_icephys_repetition(sequential_recordings=sequential_recordings_indices, id=repetition_id)
        # Check that the SimultaneousRecordingsTable table has been added
        self.assertIsNotNone(nwbfile.icephys_repetitions)
        # Check that the values for our RepetitionsTable table are correct
        res = nwbfile.icephys_repetitions[0]
        # check the id value
        self.assertEqual(res.index[0], repetition_id)
        # Check that our repetition contains 1 SweepSequence
        assert_array_equal(res.loc[repetition_id]['sequential_recordings'],
                           sequential_recordings_indices)

        #############################################
        #  Test adding a Condition
        #############################################
        # Confirm that our RepetitionsTable table does not yet exist
        self.assertIsNone(nwbfile.icephys_experimental_conditions)
        # Add a condition
        repetitions_indices = [0]
        experiment_id = np.int64(19)
        nwbfile.add_icephys_experimental_condition(repetitions=repetitions_indices, id=experiment_id)
        # Check that the ExperimentalConditionsTable table has been added
        self.assertIsNotNone(nwbfile.icephys_experimental_conditions)
        # Check that the values for our ExperimentalConditionsTable table are correct
        res = nwbfile.icephys_experimental_conditions[0]
        # check the id value
        self.assertEqual(res.index[0], experiment_id)
        # Check that our repetition contains 1 repetition
        assert_array_equal(res.loc[experiment_id]['repetitions'],
                           repetitions_indices)

        #############################################
        #  Test writing the file to disk
        #############################################
        # Write our file to disk
        # Write our test file
        with NWBHDF5IO(self.path, 'w') as nwbio:
            # # Uncomment the following lines to enable profiling for write
            # import cProfile, pstats, io
            # from pstats import SortKey
            # pr = cProfile.Profile()
            # pr.enable()
            nwbio.write(nwbfile)
            # pr.disable()
            # s = io.StringIO()
            # sortby = SortKey.CUMULATIVE
            # ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
            # ps.print_stats()
            # print(s.getvalue())

        #################################################################
        # Confirm that the low-level data has been written as expected
        # using h5py to confirm all id values. We do this before we try
        # to read the file back to confirm that data is correct on disk.
        #################################################################
        with h5py.File(self.path, 'r') as io:
            assert_array_equal(io['/general']['intracellular_ephys']['intracellular_recordings']['id'][:],
                               intracellular_recording_ids)
            default_ids = [0, 1]
            assert_array_equal(io['/general']['intracellular_ephys']['intracellular_recordings']['electrodes']['id'][:],
                               default_ids)
            assert_array_equal(io['/general']['intracellular_ephys']['intracellular_recordings']['stimuli']['id'][:],
                               default_ids)
            assert_array_equal(io['/general']['intracellular_ephys']['intracellular_recordings']['responses']['id'][:],
                               default_ids)
            assert_array_equal(io['/general']['intracellular_ephys']['simultaneous_recordings']['id'][:],
                               [simultaneous_recordings_id, ])
            assert_array_equal(io['/general']['intracellular_ephys']['sequential_recordings']['id'][:],
                               [sequential_recording_id, ])
            assert_array_equal(io['/general']['intracellular_ephys']['repetitions']['id'][:],
                               [repetition_id, ])
            assert_array_equal(io['/general']['intracellular_ephys']['experimental_conditions']['id'][:],
                               [experiment_id, ])

        #############################################
        #  Test reading the file back from disk
        #############################################
        with NWBHDF5IO(self.path, 'r') as nwbio:
            # # Uncomment the following lines to enable profiling for read
            # import cProfile, pstats, io
            # from pstats import SortKey
            # pr = cProfile.Profile()
            # pr.enable()
            infile = nwbio.read()
            # pr.disable()
            # s = io.StringIO()
            # sortby = SortKey.CUMULATIVE
            # ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
            # ps.print_stats()
            # print(s.getvalue())

            ############################################################################
            #  Test that the  IntracellularRecordingsTable table has been written correctly
            ############################################################################
            self.assertIsNotNone(infile.intracellular_recordings)
            self.assertEqual(len(infile.intracellular_recordings), 2)
            res = infile.intracellular_recordings[0]
            # Check the ID
            self.assertEqual(res.index[0], 10)
            # Check the stimulus
            self.assertEqual(res[('stimuli', 'stimulus')].iloc[0][0], 0)
            self.assertEqual(res[('stimuli', 'stimulus')].iloc[0][1], 5)
            self.assertEqual(res[('stimuli', 'stimulus')].iloc[0][2].object_id,  stimulus.object_id)
            # Check the response
            self.assertEqual(res[('responses', 'response')].iloc[0][0], 0)
            self.assertEqual(res[('responses', 'response')].iloc[0][1], 5)
            self.assertEqual(res[('responses', 'response')].iloc[0][2].object_id,
                             nwbfile.get_acquisition('vcs').object_id)
            # Check the Intracellular electrode
            self.assertEqual(res[('electrodes', 'electrode')].iloc[0].object_id,  electrode.object_id)

            ############################################################################
            #  Test that the  SimultaneousRecordingsTable table has been written correctly
            ############################################################################
            self.assertIsNotNone(infile.icephys_simultaneous_recordings)
            self.assertEqual(len(infile.icephys_simultaneous_recordings), 1)
            res = infile.icephys_simultaneous_recordings[0]
            # Check the ID and len of the intracellular_recordings column
            self.assertEqual(res.index[0], simultaneous_recordings_id)
            assert_array_equal(res.loc[simultaneous_recordings_id]['recordings'], recordings_indices)

            ############################################################################
            #  Test that the  SequentialRecordingsTable table has been written correctly
            ############################################################################
            self.assertIsNotNone(infile.icephys_sequential_recordings)
            self.assertEqual(len(infile.icephys_sequential_recordings), 1)
            res = infile.icephys_sequential_recordings[0]
            # Check the ID and len of the simultaneous_recordings column
            self.assertEqual(res.index[0], sequential_recording_id)
            assert_array_equal(res.loc[sequential_recording_id]['simultaneous_recordings'],
                               simultaneous_recordings_indices)

            ############################################################################
            #  Test that the  RepetitionsTable table has been written correctly
            ############################################################################
            self.assertIsNotNone(infile.icephys_repetitions)
            self.assertEqual(len(infile.icephys_repetitions), 1)
            res = infile.icephys_repetitions[0]
            # Check the ID and len of the simultaneous_recordings column
            self.assertEqual(res.index[0], repetition_id)
            assert_array_equal(res.loc[repetition_id]['sequential_recordings'], sequential_recordings_indices)

            ############################################################################
            #  Test that the ExperimentalConditionsTable table has been written correctly
            ############################################################################
            self.assertIsNotNone(infile.icephys_experimental_conditions)
            self.assertEqual(len(infile.icephys_experimental_conditions), 1)
            res = infile.icephys_experimental_conditions[0]
            # Check the ID and len of the simultaneous_recordings column
            self.assertEqual(res.index[0], experiment_id)
            assert_array_equal(res.loc[experiment_id]['repetitions'], repetitions_indices)
