# -*- coding: utf-8 -*-
"""
.. _ecephys_tutorial:

Extracellular Electrophysiology Data
====================================

This tutorial describes storage of extracellular electrophysiology data in NWB in four
main steps:

1. Create the electrodes table
2. Add acquired raw voltage data
3. Add LFP data
4. Add spike data

It is recommended to cover :ref:`basics` before this tutorial.

.. note:: It is recommended to check if your source data is supported by
  `NeuroConv Extracellular Electrophysiology Gallery <https://neuroconv.readthedocs.io/en/main/conversion_examples_gallery/#extracellular-electrophysiology>`_.
  If it is supported, it is recommended to use NeuroConv to convert your data.

The following examples will reference variables that may not be defined within the block they are used in. For
clarity, we define them here:
"""

# sphinx_gallery_thumbnail_path = 'figures/gallery_thumbnails_ecephys.png'
from datetime import datetime
from uuid import uuid4

import numpy as np
from dateutil.tz import tzlocal

from pynwb import NWBHDF5IO, NWBFile

from pynwb.ecephys import LFP, ElectricalSeries, SpikeEventSeries
from pynwb.misc import DecompositionSeries

#######################
# Creating and Writing NWB files
# ------------------------------
#
# When creating a NWB file, the first step is to create the :py:class:`~pynwb.file.NWBFile`.

nwbfile = NWBFile(
    session_description="my first synthetic recording",
    identifier=str(uuid4()),
    session_start_time=datetime.now(tzlocal()),
    experimenter=[
        "Baggins, Bilbo",
    ],
    lab="Bag End Laboratory",
    institution="University of Middle Earth at the Shire",
    experiment_description="I went on an adventure to reclaim vast treasures.",
    keywords=["ecephys", "exploration", "wanderlust"],
    related_publications="doi:10.1016/j.neuron.2016.12.011",
)

#######################
# Electrodes Table
# ----------------
#
# To store extracellular electrophysiology data, you first must create an electrodes table
# describing the electrodes that generated this data. Extracellular electrodes are stored in an
# ``"electrodes"`` table, which is a :py:class:`~hdmf.common.table.DynamicTable`.
#
# .. only:: html
#
#   .. image:: ../../_static/Electrodes.svg
#     :width: 500
#     :alt: electrodes table UML diagram
#     :align: center
#
# .. only:: latex
#
#   .. image:: ../../_static/Electrodes.png
#     :width: 500
#     :alt: electrodes table UML diagram
#     :align: center
#
# The electrodes table references a required :py:class:`~pynwb.ecephys.ElectrodeGroup`, which is used to represent a
# group of electrodes. Before creating an :py:class:`~pynwb.ecephys.ElectrodeGroup`, you must define a
# :py:class:`~pynwb.device.Device` object using the method :py:meth:`.NWBFile.create_device`. The fields
# ``description``, ``serial_number``, and ``model`` are optional, but recommended. The
# :py:class:`~pynwb.device.DeviceModel` object stores information about the device model, which can be useful
# when searching a set of NWB files or a data archive for all files that use a specific device model
# (e.g., Neuropixels probe).
device_model = nwbfile.create_device_model(
    name="Neurovoxels 0.99",
    manufacturer="Array Technologies",
    model_number="PRB_1_4_0480_123",
    description="A 12-channel array with 4 shanks and 3 channels per shank",
)
device = nwbfile.create_device(
    name="array",
    description="A 12-channel array with 4 shanks and 3 channels per shank",
    serial_number="1234567890",
    model=device_model,
)

#######################
# Once you have created the :py:class:`~pynwb.device.Device`, you can create an
# :py:class:`~pynwb.ecephys.ElectrodeGroup`. Then you can add electrodes one-at-a-time with
# :py:meth:`.NWBFile.add_electrode`. :py:meth:`.NWBFile.add_electrode` has two required arguments,
# ``group``, which takes an :py:class:`~pynwb.ecephys.ElectrodeGroup`, and ``location``, which takes a string. It also
# has a number of optional metadata fields for electrode features (e.g, ``x``, ``y``, ``z``, ``imp``,
# and ``filtering``). Since this table is a :py:class:`~hdmf.common.table.DynamicTable`, we can add
# additional user-specified metadata as custom columns of the table. We will be adding a ``"label"`` column to the
# table. Use the following code to add electrodes for an array with 4 shanks and 3 channels per shank.

nwbfile.add_electrode_column(name="label", description="label of electrode")

nshanks = 4
nchannels_per_shank = 3
electrode_counter = 0

for ishank in range(nshanks):
    # create an electrode group for this shank
    electrode_group = nwbfile.create_electrode_group(
        name="shank{}".format(ishank),
        description="electrode group for shank {}".format(ishank),
        device=device,
        location="brain area",
    )
    # add electrodes to the electrode table
    for ielec in range(nchannels_per_shank):
        nwbfile.add_electrode(
            group=electrode_group,
            label="shank{}elec{}".format(ishank, ielec),
            location="brain area",
        )
        electrode_counter += 1

#######################
# Similarly to other tables in PyNWB, we can view the ``electrodes`` table in tabular form
# by converting it to a pandas :py:class:`~pandas.DataFrame`.

nwbfile.electrodes.to_dataframe()

#######################
# .. note:: When we added an electrode with the :py:meth:`~pynwb.file.NWBFile.add_electrode`
#    method, we passed in the :py:class:`~pynwb.ecephys.ElectrodeGroup` object for the ``"group"`` argument.
#    This creates a reference from the ``"electrodes"`` table to the individual
#    :py:class:`~pynwb.ecephys.ElectrodeGroup` objects, one per row (electrode).

#######################
# .. _ec_recordings:
#
# Extracellular recordings
# ------------------------
#
# Raw voltage traces and local-field potential (LFP) data are stored in :py:class:`~pynwb.ecephys.ElectricalSeries`
# objects. :py:class:`~pynwb.ecephys.ElectricalSeries` is a subclass of :py:class:`~pynwb.base.TimeSeries`
# specialized for voltage data. To create the :py:class:`~pynwb.ecephys.ElectricalSeries` objects, we need to
# reference a set of rows in the ``"electrodes"`` table to indicate which electrodes were recorded. We will do this
# by creating a :py:class:`~hdmf.common.table.DynamicTableRegion`, which is a type of link that allows you to reference
# rows of a :py:class:`~hdmf.common.table.DynamicTable`. :py:meth:`.NWBFile.create_electrode_table_region` is a
# convenience function that creates a :py:class:`~hdmf.common.table.DynamicTableRegion` which references the
# ``"electrodes"`` table.

all_table_region = nwbfile.create_electrode_table_region(
    region=list(range(electrode_counter)),  # reference row indices 0 to N-1
    description="all electrodes",
)

####################
# Raw voltage data
# ^^^^^^^^^^^^^^^^^
#
# Now create an :py:class:`~pynwb.ecephys.ElectricalSeries` object to store raw data collected
# during the experiment, passing in this ``all_table_region`` :py:class:`~hdmf.common.table.DynamicTableRegion`
# reference to all rows of the electrodes table.
#
# .. only:: html
#
#   .. image:: ../../_static/ElectricalSeries.svg
#     :width: 800
#     :alt: electrical series UML diagram
#     :align: center
#
# .. only:: latex
#
#   .. image:: ../../_static/ElectricalSeries.png
#     :width: 800
#     :alt: electrical series UML diagram
#     :align: center
#

raw_data = np.random.randn(50, 12)
raw_electrical_series = ElectricalSeries(
    name="ElectricalSeries",
    description="Raw acquisition traces",
    data=raw_data,
    electrodes=all_table_region,
    starting_time=0.0,  # timestamp of the first sample in seconds relative to the session start time
    rate=20000.0,  # in Hz
)

####################
# Since this :py:class:`~pynwb.ecephys.ElectricalSeries` represents raw data from the data acquisition system,
# add it to the acquisition group of the :py:class:`~pynwb.file.NWBFile`.

nwbfile.add_acquisition(raw_electrical_series)

####################
# LFP
# ^^^
#
# Now create an :py:class:`~pynwb.ecephys.ElectricalSeries` object to store LFP data collected during the experiment,
# again passing in the :py:class:`~hdmf.common.table.DynamicTableRegion` reference to all rows of the ``"electrodes"``
# table.

lfp_data = np.random.randn(50, 12)
lfp_electrical_series = ElectricalSeries(
    name="ElectricalSeries",
    description="LFP data",
    data=lfp_data,
    filtering='Low-pass filter at 300 Hz',
    electrodes=all_table_region,
    starting_time=0.0,
    rate=200.0,
)

####################
# To help data analysis and visualization tools know that this :py:class:`~pynwb.ecephys.ElectricalSeries` object
# represents LFP data, store the :py:class:`~pynwb.ecephys.ElectricalSeries` object inside of an
# :py:class:`~pynwb.ecephys.LFP` object. This is analogous to how we can store the
# :py:class:`~pynwb.behavior.SpatialSeries` object inside of a :py:class:`~pynwb.behavior.Position` object.
#
# .. only:: html
#
#   .. image:: ../../_static/LFP.svg
#     :width: 800
#     :alt: LFP UML diagram
#     :align: center
#
# .. only:: latex
#
#   .. image:: ../../_static/LFP.png
#     :width: 800
#     :alt: LFP UML diagram
#     :align: center
#

lfp = LFP(electrical_series=lfp_electrical_series)

####################
# LFP refers to data that has been low-pass filtered, typically below 300 Hz. This data may also be downsampled.
# Because it is filtered and potentially resampled, it is categorized as processed data.
#
# Create a processing module named ``"ecephys"`` and add the :py:class:`~pynwb.ecephys.LFP` object to it.
# This is analogous to how we can store the :py:class:`~pynwb.behavior.Position` object in a processing module
# created with the method :py:meth:`.NWBFile.create_processing_module`.

ecephys_module = nwbfile.create_processing_module(
    name="ecephys", description="processed extracellular electrophysiology data"
)
ecephys_module.add(lfp)

#######################
# If your data is filtered for frequency ranges other than LFP — such as Gamma or Theta — you should store it in an
# :py:class:`~pynwb.ecephys.ElectricalSeries` and encapsulate it within a
# :py:class:`~pynwb.ecephys.FilteredEphys` object.

from pynwb.ecephys import FilteredEphys

filtered_data = np.random.randn(50, 12)
filtered_electrical_series = ElectricalSeries(
    name="FilteredElectricalSeries",
    description="Filtered data",
    data=filtered_data,
    filtering='Band-pass filtered between 4 and 8 Hz',
    electrodes=all_table_region,
    starting_time=0.0,
    rate=200.0,
)

filtered_ephys = FilteredEphys(electrical_series=filtered_electrical_series)
ecephys_module.add(filtered_ephys)

################################
# In some cases, you may want to further process the LFP data and decompose the signal into different frequency bands
# to use for other downstream analyses. You can store the processed data from these spectral analyses using a
# :py:class:`~pynwb.misc.DecompositionSeries` object. This object allows you to include metadata about the frequency
# bands and metric used (e.g., power, phase, amplitude), as well as link the decomposed data to the original
# :py:class:`~pynwb.base.TimeSeries` signal the data was derived from.

#######################
# .. note:: When adding data to :py:class:`~pynwb.misc.DecompositionSeries`, the ``data`` argument is assumed to be
#           3D where the first dimension is time, the second dimension is channels, and the third dimension is bands.


bands = dict(theta=(4.0, 12.0),
             beta=(12.0, 30.0),
             gamma=(30.0, 80.0))  # in Hz
phase_data = np.random.randn(50, 12, len(bands))  # 50 samples, 12 channels, 3 frequency bands

decomp_series = DecompositionSeries(
    name="theta",
    description="phase of bandpass filtered LFP data",
    data=phase_data,
    metric='phase',
    rate=200.0,
    source_channels=all_table_region,
    source_timeseries=lfp_electrical_series,
)

for band_name, band_limits in bands.items():
    decomp_series.add_band(
        band_name=band_name,
        band_limits=band_limits,
    )

ecephys_module.add(decomp_series)

#######################
# The frequency band information can also be viewed as a pandas DataFrame.

decomp_series.bands.to_dataframe()

####################
# .. _units_electrode:
#
# Sorted spike times
# ^^^^^^^^^^^^^^^^^^
#
# Spike times are stored in the :py:class:`~pynwb.misc.Units` table, which is a subclass of
# :py:class:`~hdmf.common.table.DynamicTable`. Adding columns to the :py:class:`~pynwb.misc.Units` table is analogous
# to how we can add columns to the ``"electrodes"`` and ``"trials"`` tables. Use the convenience method
# :py:meth:`.NWBFile.add_unit_column` to add a new column on the :py:class:`~pynwb.misc.Units` table for the
# sorting quality of the units.

nwbfile.add_unit_column(name="quality", description="sorting quality")

####################
# Generate some random spike data and populate the :py:class:`~pynwb.misc.Units` table using the
# method :py:meth:`.NWBFile.add_unit`.

firing_rate = 20
n_units = 10
res = 1000
duration = 20
for n_units_per_shank in range(n_units):
    spike_times = np.where(np.random.rand((res * duration)) < (firing_rate / res))[0] / res
    nwbfile.add_unit(spike_times=spike_times, quality="good")

#######################
# The :py:class:`~pynwb.misc.Units` table can also be converted to a pandas :py:class:`~pandas.DataFrame`.
#
# The :py:class:`~pynwb.misc.Units` table can contain simply the spike times of sorted units, or you can also include
# individual and mean waveform information in some of the optional, predefined :py:class:`~pynwb.misc.Units` table
# columns: ``waveform_mean``, ``waveform_sd``, or ``waveforms``.

nwbfile.units.to_dataframe()

####################
# Unsorted spike times
# ^^^^^^^^^^^^^^^^^^^^
#
# While the :py:class:`~pynwb.misc.Units` table is used to store spike times and waveform data for
# spike-sorted, single-unit activity, you may also want to store spike times and waveform snippets of
# unsorted spiking activity (e.g., multi-unit activity detected via threshold crossings during data acquisition).
# This information can be stored using :py:class:`~pynwb.ecephys.SpikeEventSeries` objects.

spike_snippets = np.random.rand(40, 3, 30)  # 40 events, 3 channels, 30 samples per event
shank0 = nwbfile.create_electrode_table_region(
    region=[0, 1, 2],
    description="shank0",
)

spike_events = SpikeEventSeries(
    name='SpikeEvents_Shank0',
    description="events detected with 100uV threshold",
    data=spike_snippets,
    timestamps=np.arange(40).astype(float),
    electrodes=shank0,
)
nwbfile.add_acquisition(spike_events)

############################################
# If you need to store the complete, continuous raw voltage traces, along with unsorted spike times, you should store
# the traces with :py:class:`~pynwb.ecephys.ElectricalSeries` objects as :ref:`acquisition <basic_timeseries>` data,
# and use the :py:class:`~pynwb.ecephys.EventDetection` class to identify the spike events in your raw traces.

from pynwb.ecephys import EventDetection

event_detection = EventDetection(
    name="threshold_events",
    detection_method="thresholding, 1.5 * std",
    source_electricalseries=raw_electrical_series,
    source_idx=[[1000, 0], [2000, 4], [3000, 8]],  # indicates the time and channel indices
    times=[.033, .066, .099],
)

ecephys_module.add(event_detection)

######################################
# If you do not want to store the raw voltage traces and only the waveform 'snippets' surrounding spike events,
# you should store the snippets with :py:class:`~pynwb.ecephys.SpikeEventSeries` objects.
#
# NWB also provides a way to store features of spikes, such as principal components, using the
# :py:class:`~pynwb.ecephys.FeatureExtraction` class.

from pynwb.ecephys import FeatureExtraction

feature_extraction = FeatureExtraction(
    name="PCA_features",
    electrodes=all_table_region,
    description=["PC1", "PC2", "PC3", "PC4"],
    times=[.033, .066, .099],
    features=np.random.rand(3, 12, 4),  # time, channel, feature
)

ecephys_module.add(feature_extraction)

####################
# .. _ecephys_writing:
#
# Writing electrophysiology data
# ------------------------------
#
# Once you have finished adding all of your data to the :py:class:`~pynwb.file.NWBFile`,
# write the file with :py:class:`~pynwb.NWBHDF5IO`.

with NWBHDF5IO("ecephys_tutorial.nwb", "w") as io:
    io.write(nwbfile)

####################
# For more details on :py:class:`~pynwb.NWBHDF5IO`, see the :ref:`basic_writing` tutorial.

####################
# .. _ecephys_reading:
#
# Reading electrophysiology data
# ------------------------------
#
# Access the raw data by indexing :py:class:`~pynwb.file.NWBFile.acquisition`
# with the name of the :py:class:`~pynwb.ecephys.ElectricalSeries`, which we named ``"ElectricalSeries"``.
# We can also access the LFP data by indexing :py:class:`~pynwb.file.NWBFile.processing`
# with the name of the processing module ``"ecephys"``.
# Then, we can access the :py:class:`~pynwb.ecephys.LFP` object inside the ``"ecephys"`` processing module
# by indexing it with the name of the :py:class:`~pynwb.ecephys.LFP` object.
# The default name of :py:class:`~pynwb.ecephys.LFP` objects is ``"LFP"``.
# Finally, we can access the :py:class:`~pynwb.ecephys.ElectricalSeries` object inside the
# :py:class:`~pynwb.ecephys.LFP` object by indexing it with the name of the
# :py:class:`~pynwb.ecephys.ElectricalSeries` object, which we named ``"ElectricalSeries"``.

with NWBHDF5IO("ecephys_tutorial.nwb", "r") as io:
    read_nwbfile = io.read()
    print(read_nwbfile.acquisition["ElectricalSeries"])
    print(read_nwbfile.processing["ecephys"])
    print(read_nwbfile.processing["ecephys"]["LFP"])
    print(read_nwbfile.processing["ecephys"]["LFP"]["ElectricalSeries"])

####################
# Accessing your data
# ^^^^^^^^^^^^^^^^^^^
#
# Data arrays are read passively from the file. Calling the data attribute on a :py:class:`~pynwb.base.TimeSeries`
# such as a :py:class:`~pynwb.ecephys.ElectricalSeries` does not read the data values, but presents an
# :py:class:`h5py.Dataset` object that can be indexed to read data. You can use the ``[:]`` operator to read the entire
# data array into memory.
#
# Load and print all the data values of the :py:class:`~pynwb.ecephys.ElectricalSeries`
# object representing the LFP data.

with NWBHDF5IO("ecephys_tutorial.nwb", "r") as io:
    read_nwbfile = io.read()
    print(read_nwbfile.processing["ecephys"]["LFP"]["ElectricalSeries"].data[:])

####################
# Accessing data regions
# ^^^^^^^^^^^^^^^^^^^^^^
#
# It is often preferable to read only a portion of the data. To do this, index
# or slice into the ``data`` attribute just like if you index or slice a
# :py:class:`numpy.ndarray`.
#
# The following code prints elements ``0:10`` in the first dimension (time)
# and ``0:3`` in the second dimension (electrodes) from the LFP data we have written.
# It also demonstrates how to access the spike times of the 0th unit.


with NWBHDF5IO("ecephys_tutorial.nwb", "r") as io:
    read_nwbfile = io.read()

    print("section of LFP:")
    print(read_nwbfile.processing["ecephys"]["LFP"]["ElectricalSeries"].data[:10, :3])
    print("")
    print("spike times from 0th unit:")
    print(read_nwbfile.units["spike_times"][0])
