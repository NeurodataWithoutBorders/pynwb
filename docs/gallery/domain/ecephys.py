# -*- coding: utf-8 -*-
'''
.. _ecephys_tutorial:

Extracellular Electrophysiology Data
====================================

The following tutorial describes storage of extracellular electrophysiology data in NWB.
The workflow demonstrated here involves four main steps:

1. Create the electrodes table
2. Add acquired raw voltage data
3. Add LFP data
4. Add spike data


This tutorial assumes that transforming data between these states is done by users--PyNWB does not provide
analysis functionality. It is recommended to cover :ref:`basics` before this tutorial.

The following examples will reference variables that may not be defined within the block they are used in. For
clarity, we define them here:
'''

# sphinx_gallery_thumbnail_path = 'figures/gallery_thumbnails_ecephys.png'
from datetime import datetime
from dateutil.tz import tzlocal

import numpy as np
from pynwb import NWBFile, NWBHDF5IO
from pynwb.ecephys import ElectricalSeries, LFP

#######################
# Creating and Writing NWB files
# ------------------------------
#
# When creating a NWB file, the first step is to create the :py:class:`~pynwb.file.NWBFile`.


nwbfile = NWBFile(
    'my first synthetic recording',
    'EXAMPLE_ID',
    datetime.now(tzlocal()),
    experimenter='Dr. Bilbo Baggins',
    lab='Bag End Laboratory',
    institution='University of Middle Earth at the Shire',
    experiment_description='I went on an adventure with thirteen dwarves '
                           'to reclaim vast treasures.',
    session_id='LONELYMTN'
)

#######################
# Electrodes Table
# ------------------------------
#
# In order to store extracellular electrophysiology data, you first must create an electrodes table
# describing the electrodes that generated this data. Extracellular electrodes are stored in an
# ``"electrodes"`` table, which is also a :py:class:`~hdmf.common.table.DynamicTable`.
# The ``"electrodes"`` table has several required fields: ``x``, ``y``, ``z``, ``impedance``,
# ``location``, ``filtering``, and ``electrode group``.
# Electrode groups (i.e. experimentally relevant groupings of channels) are represented by
# :py:class:`~pynwb.ecephys.ElectrodeGroup` objects.
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
# Before creating an :py:class:`~pynwb.ecephys.ElectrodeGroup`, you need to provide some information about the
# device that was used to record from the electrode. This is done by creating a :py:class:`~pynwb.device.Device`
# object using the instance method :py:meth:`~pynwb.file.NWBFile.create_device`.


device = nwbfile.create_device(
    name='array',
    description='the best array',
    manufacturer='Probe Company 9000'
)

#######################
# Once you have created the :py:class:`~pynwb.device.Device`, you can create an
# :py:class:`~pynwb.ecephys.ElectrodeGroup`. Since this is a :py:class:`~hdmf.common.table.DynamicTable`,
# we can add additional metadata fields. We will be adding a ``"label"`` column to the table.
# Use the following code to add electrodes for an array with 4 shanks and 3 channels per shank.


nwbfile.add_electrode_column(name='label', description='label of electrode')

nshanks = 4
nchannels_per_shank = 3
electrode_counter = 0

for ishank in range(nshanks):
    # create an electrode group for this shank
    electrode_group = nwbfile.create_electrode_group(
        name='shank{}'.format(ishank),
        description='electrode group for shank {}'.format(ishank),
        device=device,
        location='brain area'
    )
    # add electrodes to the electrode table
    for ielec in range(nchannels_per_shank):
        nwbfile.add_electrode(
            x=5.3, y=1.5, z=8.5, imp=np.nan,
            location='unknown',
            filtering='unknown',
            group=electrode_group,
            label='shank{}elec{}'.format(ishank, ielec)
        )
        electrode_counter += 1

#######################
# Similarly to the ``trials`` table, we can view the ``electrodes`` table in tabular form
# by converting it to a pandas :py:class:`~pandas.DataFrame`.


nwbfile.electrodes.to_dataframe()

#######################
# .. note:: When we added an electrode with the :py:class:`~pynwb.file.NWBFile.add_electrode`
#    method, we passed in the :py:class:`~pynwb.ecephys.ElectrodeGroup` object for the ``"group"`` argument.
#    This creates a reference from the ``"electrodes"`` table to the individual :py:class:`~pynwb.ecephys.ElectrodeGroup`
#    objects, one per row (electrode).

#######################
# .. _ec_recordings:
#
# Extracellular recordings
# ------------------------------
#
# Raw voltage traces and local-field potential (LFP) data are stored in :py:class:`~pynwb.ecephys.ElectricalSeries`
# objects. :py:class:`~pynwb.ecephys.ElectricalSeries` is a subclass of :py:class:`~pynwb.base.TimeSeries` specialized for voltage data.
# To create the :py:class:`~pynwb.ecephys.ElectricalSeries` objects, we need to reference a set of rows
# in the ``"electrodes"`` table to indicate which electrodes were recorded.
# We will do this by creating a :py:class:`~pynwb.core.DynamicTableRegion`, which is a type of link that allows you to reference
# specific rows of a :py:class:`~hdmf.common.table.DynamicTable`, such as the electrodes table, by row indices.
#
# We will create :py:class:`~pynwb.core.DynamicTableRegion` object that references all rows of the ``"electrodes"`` table.


all_table_region = nwbfile.create_electrode_table_region(
    region=list(range(electrode_counter)),  # reference row indices 0 to N-1
    description='all electrodes'
)

####################
# Raw voltage data
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# Now create an :py:class:`~pynwb.ecephys.ElectricalSeries` object to store raw data collected
# during the experiment, passing in this ``"all_table_region"`` :py:class:`~pynwb.core.DynamicTableRegion`
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


raw_data = np.random.randn(50, 4)
raw_electrical_series = ElectricalSeries(
    name='ElectricalSeries',
    data=raw_data,
    electrodes=all_table_region,
    starting_time=0.,
    rate=20000.
)

####################
# NWB organizes data into different groups depending on the type of data. Groups can be thought of
# as folders within the file. Here are some of the groups within an :py:class:`~pynwb.file.NWBFile` and the types of data
# they are intended to store:
#
# * **acquisition**: raw, acquired data that should never change
# * **processing**: processed data, typically the results of preprocessing algorithms and could change
# * **analysis**: results of data analysis
# * **stimuli**: stimuli used in the experiment (e.g., images, videos, light pulses)
#
# Since this :py:class:`~pynwb.ecephys.ElectricalSeries` represents raw data from the data acquisition system,
# we will add it to the acquisition group of the :py:class:`~pynwb.file.NWBFile`.


nwbfile.add_acquisition(raw_electrical_series)

####################
# LFP
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# Now create an :py:class:`~pynwb.ecephys.ElectricalSeries` object to store LFP data collected during the experiment,
# again passing in the :py:class:`~pynwb.core.DynamicTableRegion` reference to all rows of the ``"electrodes"`` table.


lfp_data = np.random.randn(50, 4)
lfp_electrical_series = ElectricalSeries(
    name='ElectricalSeries',
    data=lfp_data,
    electrodes=all_table_region,
    starting_time=0.,
    rate=200.
)

####################
# To help data analysis and visualization tools know that this :py:class:`~pynwb.ecephys.ElectricalSeries` object
# represents LFP data, store the ElectricalSeries object inside of an :py:class:`~pynwb.ecephys.LFP` object.
# This is analogous to how we can store the :py:class:`~pynwb.behavior.SpatialSeries` object inside of a
# :py:class:`~pynwb.behavior.Position` object.
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
# Unlike the raw data, which we put into the acquisition group of the :py:class:`~pynwb.file.NWBFile`,
# LFP data is typically considered processed data because the raw data was filtered and downsampled to generate the LFP.
#
# Create a processing module named ``"ecephys"`` and add the :py:class:`~pynwb.ecephys.LFP` object to it.
# This is analogous to how we can store the :py:class:`~pynwb.behavior.Position` object in a processing module
# with the :py:class:`~pynwb.file.NWBFile.create_processing_module` method.


ecephys_module = nwbfile.create_processing_module(
    name='ecephys',
    description='processed extracellular electrophysiology data'
)
ecephys_module.add(lfp)

####################
# .. _units_electrode:
#
# Spike Times
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# Spike times are stored in the :py:class:`~pynwb.misc.Units` table, which is another subclass of :py:class:`~hdmf.common.table.DynamicTable`.
# Adding columns to the :py:class:`~pynwb.misc.Units` table is analogous to how we can add columns to the ``"electrodes"`` and ``"trials"`` tables.
#
# We will generate some random spike data and populate the :py:class:`~pynwb.misc.Units` table using the :py:class:`~pynwb.file.NWBFile.add_unit`
# method. Then we can display the :py:class:`~pynwb.misc.Units` table as a pandas :py:class:`~pandas.DataFrame`.

nwbfile.add_unit_column(name='quality', description='sorting quality')

poisson_lambda = 20
firing_rate = 20
n_units = 10
for n_units_per_shank in range(n_units):
    n_spikes = np.random.poisson(lam=poisson_lambda)
    spike_times = np.round(np.cumsum(np.random.exponential(1 / firing_rate, n_spikes)), 5)
    nwbfile.add_unit(spike_times=spike_times,
                     quality='good',
                     waveform_mean=[1., 2., 3., 4., 5.])

nwbfile.units.to_dataframe()

#######################
# Designating electrophysiology data
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# As mentioned above, :py:class:`~pynwb.ecephys.ElectricalSeries` objects
# are meant for storing specific types of extracellular recordings. In addition to this
# :py:class:`~pynwb.base.TimeSeries` class, NWB provides some :ref:`basic_data_interfaces`
# for designating the type of data you are storing. We will briefly discuss them here, and refer the reader to
# :py:mod:`API documentation <pynwb.ecephys>` and :ref:`basics` for more details on
# using these objects.
#
# For storing spike data, there are two options. Which one you choose depends on what data you have available.
# If you need to store the complete, continuous raw voltage traces, you should store your the traces with
# :py:class:`~pynwb.ecephys.ElectricalSeries` objects as :ref:`acquisition <basic_timeseries>` data, and use
# the :py:class:`~pynwb.ecephys.EventDetection` class for identifying the spike events in your raw traces.
# If you do not want to store the raw voltage traces and only the waveform 'snippets' surrounding spike events,
# you should use the :py:class:`~pynwb.ecephys.EventWaveform` class, which can store one or more
# :py:class:`~pynwb.ecephys.SpikeEventSeries` objects.
#
# The results of spike sorting (or clustering) should be stored in the top-level :py:class:`~pynwb.misc.Units` table.
# Note that it is not required to store spike waveforms in order to store spike events or waveforms--if you only
# want to store the spike times of clustered units you can use only the Units table.
#
# For local field potential data, there are two options. Again, which one you choose depends on what data you
# have available. With both options, you should store your traces with :py:class:`~pynwb.ecephys.ElectricalSeries`
# objects. If you are storing unfiltered local field potential data, you should store
# the :py:class:`~pynwb.ecephys.ElectricalSeries` objects in :py:class:`~pynwb.ecephys.LFP` data interface object(s).
# If you have filtered LFP data, you should store the :py:class:`~pynwb.ecephys.ElectricalSeries` objects  in
# :py:class:`~pynwb.ecephys.FilteredEphys` data interface object(s).


####################
# .. _ecephys_writing:
#
# Writing electrophysiology data
# ------------------------------
#
# Once you have finished adding all of your data to the :py:class:`~pynwb.file.NWBFile`,
# write the file with :py:class:`~pynwb.NWBHDF5IO`.


with NWBHDF5IO('ecephys_tutorial.nwb', 'w') as io:
    io.write(nwbfile)

####################
# For more details on :py:class:`~pynwb.NWBHDF5IO`, see the :ref:`basic_writing` tutorial.

####################
# .. _ecephys_reading:
#
# Reading electrophysiology data
# ------------------------------
#
# We can access the raw data by indexing :py:class:`~pynwb.file.NWBFile.acquisition`
# with the name of the :py:class:`~pynwb.ecephys.ElectricalSeries`, which we named ``"ElectricalSeries"``.
# We can also access the LFP data by indexing :py:class:`~pynwb.file.NWBFile.processing`
# with the name of the processing module ``"ecephys"``.
# Then, we can access the :py:class:`~pynwb.ecephys.LFP` object inside of the ``"ecephys"`` processing module
# by indexing it with the name of the :py:class:`~pynwb.ecephys.LFP` object.
# The default name of :py:class:`~pynwb.ecephys.LFP` objects is ``"LFP"``.
# Finally, we can access the :py:class:`~pynwb.ecephys.ElectricalSeries` object inside of the
# :py:class:`~pynwb.ecephys.LFP` object by indexing it with the name of the
# :py:class:`~pynwb.ecephys.ElectricalSeries` object, which we named ``"ElectricalSeries"``.

with NWBHDF5IO('ecephys_tutorial.nwb', 'r') as io:
    read_nwbfile = io.read()
    print(read_nwbfile.acquisition['ElectricalSeries'])
    print(read_nwbfile.processing['ecephys'])
    print(read_nwbfile.processing['ecephys']['LFP'])
    print(read_nwbfile.processing['ecephys']['LFP']['ElectricalSeries'])

####################
# Accessing your data
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# Data arrays are read passively from the file.
# Calling the data attribute on a :py:class:`~pynwb.base.pynwb.TimeSeries`
# such as a :py:class:`~pynwb.ecephys.ElectricalSeries` does not read the data
# values, but presents an :py:class:`~h5py` object that can be indexed to read data.
# You can use the ``[:]`` operator to read the entire data array into memory.
#
# Load and print all the data values of the :py:class:`~pynwb.ecephys.ElectricalSeries`
# object representing the LFP data.

with NWBHDF5IO('ecephys_tutorial.nwb', 'r') as io:
    read_nwbfile = io.read()
    print(read_nwbfile.processing['ecephys']['LFP']['ElectricalSeries'].data[:])

####################
# Accessing data regions
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# It is often preferable to read only a portion of the data. To do this, index
# or slice into the ``data`` attribute just like if you were indexing or slicing a
# :py:class:`~numpy` array.
#
# The following code prints elements ``0:10`` in the first dimension (time)
# and ``0:3`` in the second dimension (electrodes) from the LFP data we have written.


with NWBHDF5IO('ecephys_tutorial.nwb', 'r') as io:
    read_nwbfile = io.read()

    print('section of LFP:')
    print(read_nwbfile.processing['ecephys']['LFP']['ElectricalSeries'].data[:10, :3])
    print('')
    print('spike times from 0th unit:')
    print(read_nwbfile.units['spike_times'][0])
