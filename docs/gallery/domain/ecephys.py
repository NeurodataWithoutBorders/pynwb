# -*- coding: utf-8 -*-
'''
.. _ecephys_tutorial:

Extracellular electrophysiology data
============================================

The following examples will reference variables that may not be defined within the block they are used in. For
clarity, we define them here:
'''


import numpy as np

#######################
# Creating and Writing NWB files
# ------------------------------
#
# When creating a NWB file, the first step is to create the :py:class:`~pynwb.file.NWBFile`. The first
# argument is the name of the NWB file, and the second argument is a brief description of the dataset.

from datetime import datetime
from dateutil.tz import tzlocal
from pynwb import NWBFile

nwbfile = NWBFile('my first synthetic recording', 'EXAMPLE_ID', datetime.now(tzlocal()),
                  experimenter='Dr. Bilbo Baggins',
                  lab='Bag End Laboratory',
                  institution='University of Middle Earth at the Shire',
                  experiment_description='I went on an adventure with thirteen dwarves to reclaim vast treasures.',
                  session_id='LONELYMTN')


#######################
# Electrode metadata
# ^^^^^^^^^^^^^^^^^^
#
# Electrode groups (i.e. experimentally relevant groupings of channels) are represented by
# :py:class:`~pynwb.ecephys.ElectrodeGroup` objects. To create an electrode group, you can use the
# :py:class:`~pynwb.file.NWBFile` instance method :py:meth:`~pynwb.file.NWBFile.create_electrode_group`.
#
# Before creating an :py:class:`~pynwb.ecephys.ElectrodeGroup`, you need to provide some information about the
# device that was used to record from the electrode. This is done by creating a :py:class:`~pynwb.ecephys.Device`
# object using the instance method :py:meth:`~pynwb.file.NWBFile.create_device`.

device = nwbfile.create_device(name='trodes_rig123')

#######################
# Once you have created the :py:class:`~pynwb.device.Device`, you can create an
# :py:class:`~pynwb.ecephys.ElectrodeGroup`.

electrode_name = 'tetrode1'
description = "an example tetrode"
location = "somewhere in the hippocampus"

electrode_group = nwbfile.create_electrode_group(electrode_name,
                                                 description=description,
                                                 location=location,
                                                 device=device)

#######################
# After setting up electrode group metadata, you should add metadata about the individual electrodes comprising
# each electrode group. This is done with :py:func:`~pynwb.file.NWBFile.add_electrode`.
#
# The first argument to :py:class:`~pynwb.file.NWBFile.add_electrode` is a unique identifier that the user should
# assign. For details on the rest of the arguments, please see the
# :py:func:`API documentation <pynwb.file.NWBFile.add_electrode>`.


for idx in [1, 2, 3, 4]:
    nwbfile.add_electrode(idx,
                          x=1.0, y=2.0, z=3.0,
                          imp=float(-idx),
                          location='CA1', filtering='none',
                          group=electrode_group)


#######################
# .. note: :py:class:`~pynwb.file.NWBFile.add_electrode` returns the index of the electrode you just added.
#    This can come in handy when creating with an :py:class:`~pynwb.ecephys.ElectrodeTableRegion`
#    :py:class:`~pynwb.file.NWBFile.create_electrode_table_region` (See :ref:`ec_recordings`).

#######################
# .. _ec_recordings:
#
# Extracellular recordings
# ^^^^^^^^^^^^^^^^^^^^^^^^
#
# The main classes for storing extracellular recordings are :py:class:`~pynwb.ecephys.ElectricalSeries`
# and :py:class:`~pynwb.ecephys.SpikeEventSeries`. :py:class:`~pynwb.ecephys.ElectricalSeries` should be used
# for storing raw voltage traces, local-field potential and filtered voltage traces and
# :py:class:`~pynwb.ecephys.SpikeEventSeries` is meant for storing spike waveforms (typically in preparation for
# clustering). The results of spike clustering (e.g. per-unit metadata and spike times) should be stored in the
# top-level :py:class:`~pynwb.misc.Units` table.
#
# In addition to the *data* and *timestamps* fields inherited
# from :py:class:`~pynwb.base.TimeSeries` class, these two classs will require metadata about the elctrodes
# from which *data* was generated. This is done by providing an :py:class:`~pynwb.ecephys.ElectrodeTableRegion`,
# which you can create using the :py:class:`~pynwb.file.NWBFile.create_electrode_table_region`
#
# The first argument to :py:class:`~pynwb.file.NWBFile.create_electrode_table_region` a list of the
# indices of the electrodes you want in the region..

electrode_table_region = nwbfile.create_electrode_table_region([0, 2], 'the first and third electrodes')


####################
# Now that we have a :py:class:`~pynwb.ecephys.ElectrodeTableRegion`, we can create an
# :py:class:`~pynwb.ecephys.ElectricalSeries` and add it to our :py:class:`~pynwb.file.NWBFile`.


from pynwb.ecephys import ElectricalSeries

rate = 10.0
np.random.seed(1234)
data_len = 1000
ephys_data = np.random.rand(data_len * 2).reshape((data_len, 2))
ephys_timestamps = np.arange(data_len) / rate

ephys_ts = ElectricalSeries('test_ephys_data',
                            ephys_data,
                            electrode_table_region,
                            timestamps=ephys_timestamps,
                            # Alternatively, could specify starting_time and rate as follows
                            # starting_time=ephys_timestamps[0],
                            # rate=rate,
                            resolution=0.001,
                            comments="This data was randomly generated with numpy, using 1234 as the seed",
                            description="Random numbers generated with numpy.random.rand")
nwbfile.add_acquisition(ephys_ts)

####################
# .. _units_electrode:
#
# Associate electrodes with units
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# The :ref:`PyNWB Basics tutorial <basics>` demonstrates how to add data about units and specifying custom metadata
# about units. As mentioned :ref:`here <units_fields_ref>`, there are some optional fields for units, one of these
# is *electrodes*. This field takes a list of indices into the electrode table for the electrodes that the unit
# corresponds to. For example, if two units were inferred from the first electrode (*id* = 1, index = 0), you would
# specify that like so:

nwbfile.add_unit(id=1, electrodes=[0])
nwbfile.add_unit(id=2, electrodes=[0])

#######################
# Designating electrophysiology data
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# As mentioned above, :py:class:`~pynwb.ecephys.ElectricalSeries` and :py:class:`~pynwb.ecephys.SpikeEventSeries`
# are meant for storing specific types of extracellular recordings. In addition to these two
# :py:class:`~pynwb.base.TimeSeries` classes, NWB provides some :ref:`data interfaces <basic_data_interfaces>`
# for designating the type of data you are storing. We will briefly discuss them here, and refer the reader to
# :py:mod:`API documentation <pynwb.ecephys>` and :ref:`PyNWB Basics tutorial <basics>` for more details on
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
# Once you have finished adding all of your data to the :py:class:`~pynwb.file.NWBFile`,
# write the file with :py:class:`~pynwb.NWBHDF5IO`.

from pynwb import NWBHDF5IO

with NWBHDF5IO('ecephys_example.nwb', 'w') as io:
    io.write(nwbfile)

####################
# For more details on :py:class:`~pynwb.NWBHDF5IO`, see the :ref:`basic tutorial <basic_writing>`.

####################
# .. _ecephys_reading:
#
# Reading electrophysiology data
# ------------------------------
#
# Now that you have written some electrophysiology data, you can read it back in.

io = NWBHDF5IO('ecephys_example.nwb', 'r')
nwbfile = io.read()

####################
# For details on retrieving data from an :py:class:`~pynwb.file.NWBFile`, we refer the reader to the
# :ref:`basic tutorial <basic_reading>`. For this tutorial, we will just get back our the
# :py:class:`~pynwb.ecephys.ElectricalSeries` object we added above.
#
# First, get the :py:class:`~pynwb.ecephys.ElectricalSeries`.

ephys_ts = nwbfile.acquisition['test_ephys_data']

####################
# The second dimension of the :py:func:`~pynwb.base.TimeSeries.data` attribute should be the
# electrodes the data was recorded with. We can get the electrodes for each column in *data*
# from the :py:func:`~pynwb.ecephys.ElectricalSeries.electrodes` attribute. For example,
# information about the electrode in the second index can be retrieved like so:

elec2 = ephys_ts.electrodes[1]
