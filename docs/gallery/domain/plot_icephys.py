# -*- coding: utf-8 -*-
"""
.. _icephys_tutorial_new:

Intracellular Electrophysiology
===============================

This tutorial will guide you through storing intracellular electrophysiology data in NWB.
You'll learn how to create an NWB file containing stimulus and response time series,
electrode and device metadata, and how to organize your data in the hierarchical
metadata tables that NWB provides.

.. note:: For a video tutorial on intracellular electrophysiology in NWB see also the
       :incf_lesson:`Intracellular electrophysiology basics in NWB <intracellular-electrophysiology-basics-nwb>` and
       :incf_lesson:`Intracellular ephys metadata <intracellular-electrophysiology-structured-metadata-nwb>`
       tutorials as part of the :incf_collection:`NWB Course <neurodata-without-borders-neurophysiology-nwbn>`
       at the INCF Training Space.
"""
#####################################################################
# 1. Basic Intracellular Electrophysiology in NWB
# -----------------------------------------------
#
# In this section, we'll learn how to create a basic NWB file for intracellular 
# electrophysiology data, add device and electrode metadata, and create different 
# types of stimulus and response time series.

# Standard Python imports
# sphinx_gallery_thumbnail_path = 'figures/gallery_thumbnails_icephys.png'
from datetime import datetime, timezone
from uuid import uuid4
import numpy as np

# Import NWB classes
from pynwb import NWBFile
from pynwb.icephys import VoltageClampSeries, VoltageClampStimulusSeries

#####################################################################
# 1.1 Creating an NWB file
# ^^^^^^^^^^^^^^^^^^^^^^^^
#
# The first step is to create an NWB file with basic metadata about your experiment.

# Create the file with required metadata
nwbfile = NWBFile(
    session_description="my first synthetic recording",
    identifier=str(uuid4()),
    session_start_time=datetime.now(timezone.utc),
    experimenter=["Baggins, Bilbo"],
    lab="Bag End Laboratory",
    institution="University of Middle Earth at the Shire",
    experiment_description="I went on an adventure to reclaim vast treasures.",
    session_id="LONELYMTN001",
)


#####################################################################
# 1.2 Adding device and electrode metadata
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# Next, we'll add information about the recording device and electrode used.
# Device metadata is represented by :py:class:`~pynwb.device.Device` objects,
# while intracellular electrode metadata is represented by 
# :py:class:`~pynwb.icephys.IntracellularElectrode` objects.

# Create a device
device = nwbfile.create_device(name="Heka ITC-1600")

# Create an intracellular electrode
electrode = nwbfile.create_icephys_electrode(
    name="elec0", 
    description="a mock intracellular electrode", 
    device=device,
)

#####################################################################
# 1.3 Creating voltage clamp stimulus and response data
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# Intracellular stimulus and response data are represented with subclasses of
# :py:class:`~pynwb.icephys.PatchClampSeries`. For voltage clamp recordings, we use:
#
# - :py:class:`~pynwb.icephys.VoltageClampStimulusSeries` for the stimulus (voltage applied)
# - :py:class:`~pynwb.icephys.VoltageClampSeries` for the response (current recorded)
#
# Let's create a voltage clamp stimulus and response pair:

# Create a voltage clamp stimulus (voltage applied)
voltage_stimulus = VoltageClampStimulusSeries(
    name="voltage_stimulus",
    data=[1, 2, 3, 4, 5],
    starting_time=123.6,
    rate=10e3,
    electrode=electrode,
)

# Add the stimulus to the file
nwbfile.add_stimulus(voltage_stimulus)

# Create a voltage clamp response (current recorded)
voltage_response = VoltageClampSeries(
    name="voltage_response",
    data=[0.1, 0.2, 0.3, 0.4, 0.5],
    starting_time=123.6,
    rate=20e3,
    electrode=electrode,
)

# Add the response to the file
nwbfile.add_acquisition(voltage_response)


#####################################################################
# 1.4 Creating current clamp stimulus and response data
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# For current clamp recordings, we use:
#
# - :py:class:`~pynwb.icephys.CurrentClampStimulusSeries` for the stimulus (current applied)
# - :py:class:`~pynwb.icephys.CurrentClampSeries` for the response (voltage recorded)

# Import current clamp classes
from pynwb.icephys import CurrentClampStimulusSeries, CurrentClampSeries

# Create a current clamp stimulus (current applied)
current_stimulus = CurrentClampStimulusSeries(
    name="current_stimulus",
    data=[1, 2, 3, 4, 5],
    starting_time=123.6,
    rate=10e3,
    electrode=electrode,
    gain=0.02,
    sweep_number=np.uint(16),
)

# Add the stimulus to the file
nwbfile.add_stimulus(current_stimulus)

# Create a current clamp response (voltage recorded)
current_response = CurrentClampSeries(
    name="current_response",
    data=[0.1, 0.2, 0.3, 0.4, 0.5],
    starting_time=123.6,
    rate=20e3,
    electrode=electrode,
)

# Add the response to the file
nwbfile.add_acquisition(current_response)


#####################################################################
# 1.5 IZeroClamp recordings
# ^^^^^^^^^^^^^^^^^^^^^^^^^
#
# NWB also supports IZeroClamp recordings with :py:class:`~pynwb.icephys.IZeroClampSeries`.
# This is used for recordings when all current and amplifier settings are off 
# (i.e., current is clamped to 0). There is no stimulus associated with an IZero series 
# because the amplifier is disconnected and no stimulus can reach the cell.
#

# Import IZeroClampSeries
from pynwb.icephys import IZeroClampSeries

# Example of creating an IZeroClamp response
izero_response = IZeroClampSeries(
    name="izero_response",
    data=[0.1, 0.2, 0.3, 0.4, 0.5],
    electrode=electrode,
    starting_time=345.6,
    rate=20e3,
)

# Add the response to the file
nwbfile.add_acquisition(izero_response)


#####################################################################
# 2. Organizing Data with the Intracellular Recordings Table
# ----------------------------------------------------------
#
# While you can add stimulus and response data directly to the NWB file as shown above,
# NWB provides a more structured way to organize intracellular recordings using the
# :py:class:`~pynwb.icephys.IntracellularRecordingsTable`. This table relates electrode,
# stimulus, and response pairs and allows you to add custom metadata.

# Import pandas for displaying tables
import pandas

# Set pandas rendering option to avoid very wide tables in the html docs
pandas.set_option("display.max_colwidth", 30)
pandas.set_option("display.max_rows", 10)

#####################################################################
# 2.1 Adding recordings to the intracellular recordings table
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# The :py:class:`~pynwb.icephys.IntracellularRecordingsTable` relates electrode, stimulus
# and response pairs and describes metadata specific to individual recordings.
#
# .. figure:: ../../figures/plot_icephys_intracellular_recordings_table.png
#    :figwidth: 90%
#    :alt: IntracellularRecordingsTable
#
#    Illustration of the structure of the IntracellularRecordingsTable
#
# Let's add our voltage clamp recording to the table:

# Add an intracellular recording
rowindex = nwbfile.add_intracellular_recording(
    electrode=electrode, 
    stimulus=voltage_stimulus, 
    response=voltage_response, 
)

# Display the intracellular recordings table    
pandas.set_option("display.max_columns", 6)  # avoid oversize table in the html docs,m
nwbfile.intracellular_recordings.to_dataframe()


#####################################################################
# The add_intracellular_recording method requires the following parameters:
# - electrode: a reference to the electrode used for recording
# - stimulus: a reference to the stimulus time series (optional if response is provided)
# - response: a reference to the response time series (optional if stimulus is provided)
#
# For more information on this method, see the documentation:
# https://pynwb.readthedocs.io/en/stable/pynwb.file.html#pynwb.file.NWBFile.add_intracellular_recording
#
#
#
#
#
# 2.2 Handling time alignment with index ranges
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# Sometimes the stimulus and response recordings may not align perfectly in time.
# You can specify relevant time ranges for a stimulus and/or response as part of
# the intracellular recording using the `stimulus_start_index`, `stimulus_index_count`,
# `response_start_index`, and `response_index_count` parameters.

# Add a recording with specific time ranges for stimulus and response
rowindex2 = nwbfile.add_intracellular_recording(
    electrode=electrode,
    stimulus=voltage_stimulus,
    stimulus_start_index=1,  # Start at the second data point
    stimulus_index_count=3,   # Use 3 data points
    response=voltage_response,
    response_start_index=2,   # Start at the third data point
    response_index_count=3,    # Use 3 data points
    id=11,
)

# You can also add a recording with just a stimulus or response
rowindex3 = nwbfile.add_intracellular_recording(
    electrode=electrode, 
    response=current_response,  # Only response, no stimulus
    id=12,
)

# Display the updated intracellular recordings table
nwbfile.intracellular_recordings.to_dataframe()



#####################################################################
# The index range parameters allow you to specify which portion of the data to use:
# - stimulus_start_index: the starting index for the stimulus data
# - stimulus_index_count: the number of data points to use from the stimulus
# - response_start_index: the starting index for the response data
# - response_index_count: the number of data points to use from the response
#
# This is useful when the stimulus and response data are not perfectly aligned in time,
# or when you want to use only a specific portion of the data.
#
#
#
#
#
#
# 2.3 Adding custom metadata to the recordings table
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# You can add custom metadata to the intracellular recordings table by adding columns.

# Add a simple custom column to the main table
nwbfile.intracellular_recordings.add_column(
    name="recording_tag",
    data=["VoltageClamp", "VoltageClamp_TimeRange", "CurrentClamp"],
    description="Type of recording",
)

# Add a custom column to the electrodes category
nwbfile.intracellular_recordings.add_column(
    name="voltage_threshold",
    data=[0.1, 0.12, 0.13],
    description="Voltage threshold for spike detection",
    category="electrodes",
)

# Display the customized table
nwbfile.intracellular_recordings.to_dataframe()


#####################################################################
# The add_column method requires the following parameters:
# - name: the name of the column
# - data: the data for the column
# - description: a description of the column
# - category: the category to add the column to (optional)
#
# For more information on this method, see the documentation:
# https://pynwb.readthedocs.io/en/stable/pynwb.icephys.html#pynwb.icephys.IntracellularRecordingsTable.add_column
#
#
#
#
#
# 2.4 Creating custom categories for additional metadata
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# The :py:class:`~pynwb.icephys.IntracellularRecordingsTable` is an ``AlignedDynamicTable``
# that can contain additional category tables for organizing metadata.

# Import necessary classes for creating custom categories
from pynwb.core import DynamicTable, VectorData

# Create a new DynamicTable for our category
location_column = VectorData(
    name="location",
    data=["CA1", "CA3", "DG"],
    description="Recording location in the hippocampus",
)

lab_category = DynamicTable(
    name="recording_lab_data",
    description="category table for lab-specific recording metadata",
    colnames=["location"],
    columns=[location_column],
)

# Add the table as a new category to our intracellular_recordings
nwbfile.intracellular_recordings.add_category(category=lab_category)

# Display the table with the new category
nwbfile.intracellular_recordings.to_dataframe()


#####################################################################
# The add_category method requires the following parameters:
# - category: the category table to add
#
# For more information on this method, see the documentation:
# https://pynwb.readthedocs.io/en/stable/pynwb.icephys.html#pynwb.icephys.IntracellularRecordingsTable.add_category
#
#
#
#
# 2.5 Adding stimulus templates
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# Stimulus templates are idealized versions of the stimulus waveforms used in recordings.
# They can be useful for data analysis or to validate that the recorded stimulus matches
# the expected waveform.

# Import necessary classes for working with time series references
from pynwb.base import TimeSeriesReference, TimeSeriesReferenceVectorData

# Create a stimulus template
stimulus_template = VoltageClampStimulusSeries(
    name="voltage_step_template",
    data=[0, 1, 2, 3, 4],
    starting_time=0.0,
    rate=10e3,
    electrode=electrode,
    gain=0.02,
)
nwbfile.add_stimulus_template(stimulus_template)

# Add the stimulus template to our recordings table
nwbfile.intracellular_recordings.add_column(
    name="stimulus_template",
    data=[
        TimeSeriesReference(0, 5, stimulus_template),  # Full template
        TimeSeriesReference(1, 3, stimulus_template),  # Partial template
        TimeSeriesReference.empty(stimulus_template)   # Empty reference (no template)
    ],
    description="Reference to the stimulus template for each recording",
    category="stimuli",
    col_cls=TimeSeriesReferenceVectorData,
)

# Create a second voltage clamp recording for our fourth row
voltage_stimulus2 = VoltageClampStimulusSeries(
    name="voltage_stimulus2",
    data=[2, 3, 4, 5, 6],
    starting_time=223.6,
    rate=10e3,
    electrode=electrode,
)
nwbfile.add_stimulus(voltage_stimulus2)

voltage_response2 = VoltageClampSeries(
    name="voltage_response2",
    data=[0.2, 0.3, 0.4, 0.5, 0.6],
    starting_time=223.6,
    rate=20e3,
    electrode=electrode,
)
nwbfile.add_acquisition(voltage_response2)

# Add a new recording with all metadata at once
rowindex4 = nwbfile.add_intracellular_recording(
    electrode=electrode,
    stimulus=voltage_stimulus2,
    response=voltage_response2,
    stimulus_template=stimulus_template,
    recording_tag='VoltageClamp2',
    recording_lab_data={'location': 'CA2'},
    electrode_metadata={'voltage_threshold': 0.14},
    id=13,
)

# Display the updated table
nwbfile.intracellular_recordings.to_dataframe()



#####################################################################
# The TimeSeriesReference class is used to reference a specific portion of a time series:
# - TimeSeriesReference(start_index, count, timeseries): references a specific portion
# - TimeSeriesReference.empty(timeseries): creates an empty reference
#
# For more information on this class, see the documentation:
# https://pynwb.readthedocs.io/en/stable/pynwb.base.html#pynwb.base.TimeSeriesReference
#
#
#
#
# 3. Hierarchical Organization for Complex Experiments
# ----------------------------------------------------
#
# For more complex experiments, NWB provides a hierarchical organization of metadata
# tables that build on top of the IntracellularRecordingsTable. This hierarchy helps
# avoid duplication of metadata and makes it easier to organize and query your data.
#
# In this section, we'll create a more complex example with multiple electrodes,
# multiple recordings, and a hierarchical organization that matches the diagram
# shown in the documentation.

# Standard Python imports
from datetime import datetime, timezone
from uuid import uuid4
import numpy as np
import pandas

# Import NWB classes
from pynwb import NWBFile
from pynwb.icephys import (
    VoltageClampSeries, VoltageClampStimulusSeries,
    CurrentClampSeries, CurrentClampStimulusSeries
)

# Create a new NWB file for our complex example
nwbfile = NWBFile(
    session_description="hierarchical organization example",
    identifier=str(uuid4()),
    session_start_time=datetime.now(timezone.utc),
    experimenter=["Baggins, Bilbo"],
    lab="Bag End Laboratory",
    institution="University of Middle Earth at the Shire",
    experiment_description="Complex intracellular electrophysiology experiment",
    session_id="COMPLEX001",
)

# Create devices for our complex example
device1 = nwbfile.create_device(name="Heka ITC-1600")
device2 = nwbfile.create_device(name="Axon MultiClamp 700B")

# Create electrodes for our complex example
electrode1 = nwbfile.create_icephys_electrode(
    name="E1", 
    description="Electrode 1", 
    device=device1,
)

electrode2 = nwbfile.create_icephys_electrode(
    name="E2", 
    description="Electrode 2", 
    device=device1,
)

electrode3 = nwbfile.create_icephys_electrode(
    name="E3", 
    description="Electrode 3", 
    device=device2,
)

# Create stimulus and response series for our complex example
# Stimulus series S1-S6
stimulus1 = VoltageClampStimulusSeries(
    name="S1",
    data=np.ones(120),
    starting_time=0.0,
    rate=10e3,
    electrode=electrode1,
)

stimulus2 = VoltageClampStimulusSeries(
    name="S2",
    data=np.ones(140),
    starting_time=0.0,
    rate=10e3,
    electrode=electrode2,
)

stimulus3 = CurrentClampStimulusSeries(
    name="S3",
    data=np.ones(120),
    starting_time=0.0,
    rate=10e3,
    electrode=electrode1,
)

stimulus4 = CurrentClampStimulusSeries(
    name="S4",
    data=np.ones(150),
    starting_time=0.0,
    rate=10e3,
    electrode=electrode2,
)

stimulus5 = VoltageClampStimulusSeries(
    name="S5",
    data=np.ones(110),
    starting_time=0.0,
    rate=10e3,
    electrode=electrode3,
)

stimulus6 = CurrentClampStimulusSeries(
    name="S6",
    data=np.ones(160),
    starting_time=0.0,
    rate=10e3,
    electrode=electrode1,
)

# Response series R1-R6
response1 = VoltageClampSeries(
    name="R1",
    data=np.ones(120) * 0.1,
    starting_time=0.0,
    rate=10e3,
    electrode=electrode1,
)
nwbfile.add_acquisition(response1)

response2 = VoltageClampSeries(
    name="R2",
    data=np.ones(140) * 0.1,
    starting_time=0.0,
    rate=10e3,
    electrode=electrode2,
)
nwbfile.add_acquisition(response2)

response3 = CurrentClampSeries(
    name="R3",
    data=np.ones(120) * 0.1,
    starting_time=0.0,
    rate=10e3,
    electrode=electrode1,
)
nwbfile.add_acquisition(response3)

response4 = CurrentClampSeries(
    name="R4",
    data=np.ones(150) * 0.1,
    starting_time=0.0,
    rate=10e3,
    electrode=electrode2,
)
nwbfile.add_acquisition(response4)

response5 = VoltageClampSeries(
    name="R5",
    data=np.ones(110) * 0.1,
    starting_time=0.0,
    rate=10e3,
    electrode=electrode3,
)
nwbfile.add_acquisition(response5)

response6 = CurrentClampSeries(
    name="R6",
    data=np.ones(160) * 0.1,
    starting_time=0.0,
    rate=10e3,
    electrode=electrode1,
)
nwbfile.add_acquisition(response6)

# Add intracellular recordings
rec0 = nwbfile.add_intracellular_recording(
    electrode=electrode1,
    stimulus=stimulus1,
    response=response1,
    id=0,
)

rec1 = nwbfile.add_intracellular_recording(
    electrode=electrode2,
    stimulus=stimulus2,
    response=response2,
    id=1,
)

rec2 = nwbfile.add_intracellular_recording(
    electrode=electrode1,
    stimulus=stimulus3,
    response=response3,
    id=2,
)

rec3 = nwbfile.add_intracellular_recording(
    electrode=electrode2,
    stimulus=stimulus4,
    response=response4,
    id=3,
)

rec4 = nwbfile.add_intracellular_recording(
    electrode=electrode3,
    stimulus=stimulus5,
    response=response5,
    id=4,
)

rec5 = nwbfile.add_intracellular_recording(
    electrode=electrode1,
    stimulus=stimulus6,
    response=response6,
    id=5,
)

# Display the intracellular recordings table
pandas.set_option("display.max_colwidth", 30)
pandas.set_option("display.max_rows", 10)
pandas.set_option("display.max_columns", 6)
nwbfile.intracellular_recordings.to_dataframe()

#####################################################################
# 3.1 Simultaneous recordings
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# The :py:class:`~pynwb.icephys.SimultaneousRecordingsTable` groups intracellular
# recordings that were recorded simultaneously from different electrodes and/or cells.
# In practice, a simultaneous recording is often referred to as a "sweep".

# Get the simultaneous recordings table (creates it if it doesn't exist)
icephys_simultaneous_recordings = nwbfile.get_icephys_simultaneous_recordings()

# Add simultaneous recordings
sweep0 = nwbfile.add_icephys_simultaneous_recording(
    recordings=[rec0, rec1],
    id=0,
)

sweep1 = nwbfile.add_icephys_simultaneous_recording(
    recordings=[rec2, rec3, rec4],
    id=1,
)

sweep2 = nwbfile.add_icephys_simultaneous_recording(
    recordings=[rec5],
    id=2,
)

# Add another simultaneous recording that overlaps with others
sweep3 = nwbfile.add_icephys_simultaneous_recording(
    recordings=[rec0, rec2],
    id=3,
)

sweep4 = nwbfile.add_icephys_simultaneous_recording(
    recordings=[rec1, rec3],
    id=4,
)

sweep5 = nwbfile.add_icephys_simultaneous_recording(
    recordings=[rec4, rec5],
    id=5,
)

# Display the simultaneous recordings table
icephys_simultaneous_recordings.to_dataframe()



#####################################################################
# The add_icephys_simultaneous_recording method requires the following parameters:
# - recordings: a list of references to intracellular recordings
#
# For more information on this method, see the documentation:
# https://pynwb.readthedocs.io/en/stable/pynwb.file.html#pynwb.file.NWBFile.add_icephys_simultaneous_recording
#
#
# 3.2 Sequential recordings
# ^^^^^^^^^^^^^^^^^^^^^^^^^
#
# The :py:class:`~pynwb.icephys.SequentialRecordingsTable` groups simultaneously
# recorded intracellular recordings together. In practice, a sequential recording
# is often referred to as a "sweep sequence". A common use is to group together
# simultaneous recordings where a sequence of stimuli of the same type with varying
# parameters have been presented.

# Add sequential recordings
seq0 = nwbfile.add_icephys_sequential_recording(
    simultaneous_recordings=[sweep0, sweep1],
    stimulus_type="square",
    id=0,
)

seq1 = nwbfile.add_icephys_sequential_recording(
    simultaneous_recordings=[sweep2, sweep3],
    stimulus_type="ramp",
    id=1,
)

seq2 = nwbfile.add_icephys_sequential_recording(
    simultaneous_recordings=[sweep4, sweep5],
    stimulus_type="noise",
    id=2,
)

# Display the sequential recordings table
nwbfile.icephys_sequential_recordings.to_dataframe()


#####################################################################
# The add_icephys_sequential_recording method requires the following parameters:
# - simultaneous_recordings: a list of references to simultaneous recordings
# - stimulus_type: a description of the stimulus type
#
# For more information on this method, see the documentation:
# https://pynwb.readthedocs.io/en/stable/pynwb.file.html#pynwb.file.NWBFile.add_icephys_sequential_recording
#
#
# 3.3 Repetitions
# ^^^^^^^^^^^^^^^
#
# The :py:class:`~pynwb.icephys.RepetitionsTable` groups sequential recordings.
# In practice, a repetition is often referred to as a "run". A typical use is
# to group sets of different stimuli that are applied in sequence and may be repeated.

# Add repetitions
rep0 = nwbfile.add_icephys_repetition(
    sequential_recordings=[seq0, seq1],
    id=0,
)

rep1 = nwbfile.add_icephys_repetition(
    sequential_recordings=[seq2],
    id=1,
)

# Display the repetitions table
nwbfile.icephys_repetitions.to_dataframe()

#####################################################################
# The add_icephys_repetition method requires the following parameters:
# - sequential_recordings: a list of references to sequential recordings
#
# For more information on this method, see the documentation:
# https://pynwb.readthedocs.io/en/stable/pynwb.file.html#pynwb.file.NWBFile.add_icephys_repetition
#
#
# 3.4 Experimental conditions
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# The :py:class:`~pynwb.icephys.ExperimentalConditionsTable` groups repetitions of
# intracellular recording that belong to the same experimental conditions.

# Add experimental conditions
cond0 = nwbfile.add_icephys_experimental_condition(
    repetitions=[rep0],
    id=0,
)

cond1 = nwbfile.add_icephys_experimental_condition(
    repetitions=[rep1],
    id=1,
)

# Add a custom column to the experimental conditions table
nwbfile.icephys_experimental_conditions.add_column(
    name="condition_name",
    data=["Control", "Treatment"],
    description="Name of the experimental condition",
)

# Display the experimental conditions table
nwbfile.icephys_experimental_conditions.to_dataframe()

# The add_icephys_experimental_condition method requires the following parameters:
# - repetitions: a list of references to repetitions
#
# For more information on this method, see the documentation:
# https://pynwb.readthedocs.io/en/stable/pynwb.file.html#pynwb.file.NWBFile.add_icephys_experimental_condition

#####################################################################
# 3.5 Saving and accessing your data
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# Now let's save our NWB file.

# Write our file
from pynwb import NWBHDF5IO
testpath = "test_icephys_file.nwb"
with NWBHDF5IO(testpath, "w") as io:
    io.write(nwbfile)

#####################################################################
# 3.6 Understanding the hierarchy
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# The metadata tables we've created form a hierarchical structure that helps organize
# complex intracellular electrophysiology experiments.
#
# .. figure:: ../../figures/plot_icephys_table_hierarchy.png
#     :figwidth: 100%
#     :alt: Intracellular electrophysiology metadata table hierarchy
#
#     Illustration of the hierarchy of metadata tables used to describe the organization of
#     intracellular electrophysiology experiments.
#
# The tables are organized in a hierarchical structure:
#
# - :py:class:`~pynwb.icephys.IntracellularRecordingsTable` relates electrode, stimulus
#   and response pairs and describes metadata specific to individual recordings.
# - :py:class:`~pynwb.icephys.SimultaneousRecordingsTable` groups intracellular
#   recordings that were recorded simultaneously from different electrodes and/or cells.
# - :py:class:`~pynwb.icephys.SequentialRecordingsTable` groups simultaneous recordings
#   where a sequence of stimuli of the same type with varying parameters have been presented.
# - :py:class:`~pynwb.icephys.RepetitionsTable` groups sequential recordings, typically
#   sets of different stimuli that are applied in sequence and may be repeated.
# - :py:class:`~pynwb.icephys.ExperimentalConditionsTable` groups repetitions that
#   belong to the same experimental conditions.
#
# This hierarchical organization helps avoid duplication of metadata and makes it easier
# to focus on individual aspects of an experiment while still being able to access
# information from related tables.
