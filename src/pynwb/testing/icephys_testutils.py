"""
Module with helper functions to facilitate testing
"""
import numpy as np
from datetime import datetime
from dateutil.tz import tzlocal
from pynwb.file import NWBFile
from pynwb.icephys import (VoltageClampStimulusSeries, VoltageClampSeries)
from pynwb import NWBHDF5IO


def create_icephys_stimulus_and_response(sweep_number, electrode, randomize_data):
    """
    Internal helper function to construct a dummy stimulus and response pair representing an
    intracellular recording:

    :param sweep_number: Integer sweep number of the recording
    :type sweep_number: int
    :param electrode: Intracellular electrode used
    :type electrode: pynwb.icephys.IntracellularElectrode
    :param randomize_data: Randomize data values in the stimulus and response
    :type randomize_data: bool

    :returns: Tuple of VoltageClampStimulusSeries with the stimulus and VoltageClampSeries with the response.
    """
    stimulus = VoltageClampStimulusSeries(
                name="ccss_"+str(sweep_number),
                data=[1, 2, 3, 4, 5] if not randomize_data else np.random.rand(10),
                starting_time=123.6 if not randomize_data else (np.random.rand() * 100),
                rate=10e3 if not randomize_data else int(np.random.rand()*10) * 1000 + 1000.,
                electrode=electrode,
                gain=0.1 if not randomize_data else np.random.rand(),
                sweep_number=sweep_number)
    # Create and ic-response
    response = VoltageClampSeries(
                name='vcs_'+str(sweep_number),
                data=[0.1, 0.2, 0.3, 0.4, 0.5] if not randomize_data else np.random.rand(10),
                conversion=1e-12,
                resolution=np.nan,
                starting_time=123.6 if not randomize_data else (np.random.rand() * 100),
                rate=20e3 if not randomize_data else int(np.random.rand() * 20) * 1000. + 1000.,
                electrode=electrode,
                gain=0.02 if not randomize_data else np.random.rand(),
                capacitance_slow=100e-12,
                resistance_comp_correction=70.0 if not randomize_data else 70.0 + np.random.rand(),
                sweep_number=sweep_number)
    return stimulus, response


def create_icephys_testfile(filename=None, add_custom_columns=True, randomize_data=True, with_missing_stimulus=True):
    """
    Create a small but relatively complex icephys test file that
    we can use for testing of queries.

    :param filename: The name of the output file to be generated. If set to None then the file is not written
                     but only created in memory
    :type filename: str, None
    :param add_custom_colums: Add custom metadata columns to each table
    :type add_custom_colums: bool
    :param randomize_data: Randomize data values in the stimulus and response
    :type randomize_data: bool

    :returns: NWBFile object with icephys data created for writing. NOTE: If filename is provided then
              the file is written to disk, but the function does not read the file back. If
              you want to use the file from disk then you will need to read it with NWBHDF5IO.
    :rtype: NWBFile
    """
    nwbfile = NWBFile(
            session_description='my first synthetic recording',
            identifier='EXAMPLE_ID',
            session_start_time=datetime.now(tzlocal()),
            experimenter='Dr. Bilbo Baggins',
            lab='Bag End Laboratory',
            institution='University of Middle Earth at the Shire',
            experiment_description='I went on an adventure with thirteen dwarves to reclaim vast treasures.',
            session_id='LONELYMTN')
    # Add a device
    device = nwbfile.create_device(name='Heka ITC-1600')
    # Add an intracellular electrode
    electrode0 = nwbfile.create_icephys_electrode(
        name="elec0",
        description='a mock intracellular electrode',
        device=device)
    # Add an intracellular electrode
    electrode1 = nwbfile.create_icephys_electrode(
        name="elec1",
        description='another mock intracellular electrode',
        device=device)
    # Add the intracelluar recordings
    for sweep_number in range(20):
        elec = (electrode0 if (sweep_number % 2 == 0) else electrode1)
        stim, resp = create_icephys_stimulus_and_response(sweep_number=np.uint64(sweep_number),
                                                          electrode=elec,
                                                          randomize_data=randomize_data)
        if with_missing_stimulus and sweep_number in [0, 10]:
            stim = None
        nwbfile.add_intracellular_recording(electrode=elec,
                                            stimulus=stim,
                                            response=resp,
                                            id=sweep_number)
    nwbfile.intracellular_recordings.add_column(name='recording_tags',
                                                data=['A1', 'A2',
                                                      'B1', 'B2',
                                                      'C1', 'C2', 'C3',
                                                      'D1', 'D2', 'D3',
                                                      'A1', 'A2',
                                                      'B1', 'B2',
                                                      'C1', 'C2', 'C3',
                                                      'D1', 'D2', 'D3'],
                                                description='String with a set of recording tags')
    # Add simultaneous_recordings
    nwbfile.add_icephys_simultaneous_recording(recordings=[0, 1], id=np.int64(100))
    nwbfile.add_icephys_simultaneous_recording(recordings=[2, 3], id=np.int64(101))
    nwbfile.add_icephys_simultaneous_recording(recordings=[4, 5, 6], id=np.int64(102))
    nwbfile.add_icephys_simultaneous_recording(recordings=[7, 8, 9], id=np.int64(103))
    nwbfile.add_icephys_simultaneous_recording(recordings=[10, 11], id=np.int64(104))
    nwbfile.add_icephys_simultaneous_recording(recordings=[12, 13], id=np.int64(105))
    nwbfile.add_icephys_simultaneous_recording(recordings=[14, 15, 16], id=np.int64(106))
    nwbfile.add_icephys_simultaneous_recording(recordings=[17, 18, 19], id=np.int64(107))
    if add_custom_columns:
        nwbfile.icephys_simultaneous_recordings.add_column(
            name='tag',
            data=np.arange(8),
            description='some integer tag for a sweep')

    # Add sequential recordings
    nwbfile.add_icephys_sequential_recording(simultaneous_recordings=[0, 1],
                                             id=np.int64(1000),
                                             stimulus_type="StimType_1")
    nwbfile.add_icephys_sequential_recording(simultaneous_recordings=[2, ],
                                             id=np.int64(1001),
                                             stimulus_type="StimType_2")
    nwbfile.add_icephys_sequential_recording(simultaneous_recordings=[3, ],
                                             id=np.int64(1002),
                                             stimulus_type="StimType_3")
    nwbfile.add_icephys_sequential_recording(simultaneous_recordings=[4, 5],
                                             id=np.int64(1003),
                                             stimulus_type="StimType_1")
    nwbfile.add_icephys_sequential_recording(simultaneous_recordings=[6, ],
                                             id=np.int64(1004),
                                             stimulus_type="StimType_2")
    nwbfile.add_icephys_sequential_recording(simultaneous_recordings=[7, ],
                                             id=np.int64(1005),
                                             stimulus_type="StimType_3")
    if add_custom_columns:
        nwbfile.icephys_sequential_recordings.add_column(
            name='type',
            data=['T1', 'T2', 'T3', 'T1', 'T2', 'T3'],
            description='type of the sequential recording')

    # Add repetitions
    nwbfile.add_icephys_repetition(sequential_recordings=[0, ], id=np.int64(10000))
    nwbfile.add_icephys_repetition(sequential_recordings=[1, 2], id=np.int64(10001))
    nwbfile.add_icephys_repetition(sequential_recordings=[3, ], id=np.int64(10002))
    nwbfile.add_icephys_repetition(sequential_recordings=[4, 5], id=np.int64(10003))
    if add_custom_columns:
        nwbfile.icephys_repetitions.add_column(
            name='type',
            data=['R1', 'R2', 'R1', 'R2'],
            description='some repetition type indicator')

    # Add experimental_conditions
    nwbfile.add_icephys_experimental_condition(repetitions=[0, 1], id=np.int64(100000))
    nwbfile.add_icephys_experimental_condition(repetitions=[2, 3], id=np.int64(100001))
    if add_custom_columns:
        nwbfile.icephys_experimental_conditions.add_column(
            name='temperature',
            data=[32., 24.],
            description='Temperatur in C')

    # Write our test file
    if filename is not None:
        with NWBHDF5IO(filename, 'w') as io:
            io.write(nwbfile)

    # Return our in-memory NWBFile
    return nwbfile
