# -*- coding: utf-8 -*-
'''
.. _icephys_tutorial:

Intracellular electrophysiology data
============================================

The following examples will reference variables that may not be defined within the block they are used in. For
clarity, we define them here:
'''

#######################
# Creating and Writing NWB files
# ------------------------------
#
# When creating a NWB file, the first step is to create the :py:class:`~pynwb.file.NWBFile`. The first
# argument is is a brief description of the dataset.

from datetime import datetime
from dateutil.tz import tzlocal
from pynwb import NWBFile
import numpy as np

nwbfile = NWBFile('my first synthetic recording', 'EXAMPLE_ID', datetime.now(tzlocal()),
                  experimenter='Dr. Bilbo Baggins',
                  lab='Bag End Laboratory',
                  institution='University of Middle Earth at the Shire',
                  experiment_description='I went on an adventure with thirteen dwarves to reclaim vast treasures.',
                  session_id='LONELYMTN')

#######################
# Device metadata
# ^^^^^^^^^^^^^^^
#
# Device metadata is represented by :py:class:`~pynwb.device.Device` objects.
# To create a device, you can use the :py:class:`~pynwb.device.Device` instance method
# :py:meth:`~pynwb.file.NWBFile.create_device`.

device = nwbfile.create_device(name='Heka ITC-1600')

#######################
# Electrode metadata
# ^^^^^^^^^^^^^^^^^^
#
# Intracellular electrode metadata is represented by :py:class:`~pynwb.icephys.IntracellularElectrode` objects.
# To create an electrode group, you can use the :py:class:`~pynwb.file.NWBFile` instance method
# :py:meth:`~pynwb.file.NWBFile.create_ic_electrode`.

elec = nwbfile.create_ic_electrode(name="elec0",
                                   description='a mock intracellular electrode',
                                   device=device)

#######################
# Stimulus data
# ^^^^^^^^^^^^^
#
# Intracellular stimulus and response data are represented with subclasses of
# :py:class:`~pynwb.icephys.PatchClampSeries`. There are two classes for representing stimulus
# data--:py:class:`~pynwb.icephys.VoltageClampStimulusSeries` and
# :py:class:`~pynwb.icephys.CurrentClampStimulusSeries`--, and three classes for representing response
# data--:py:class:`~pynwb.icephys.VoltageClampSeries`,
# :py:class:`~pynwb.icephys.VoltageClampSeries`, :py:class:`~pynwb.icephys.CurrentClampSeries`, and
# :py:class:`~pynwb.icephys.IZeroClampSeries`.
#
# Here, we will use :py:class:`~pynwb.icephys.CurrentClampStimulusSeries` to store current clamp stimulus
# data and then add it to our NWBFile as stimulus data using the :py:class:`~pynwb.file.NWBFile` method
# :py:meth:`~pynwb.file.NWBFile.add_stimulus`.

from pynwb.icephys import CurrentClampStimulusSeries

ccss = CurrentClampStimulusSeries(
    name="ccss", data=[1, 2, 3, 4, 5], unit='A',
    starting_time=123.6, rate=10e3, electrode=elec, gain=0.02)

nwbfile.add_stimulus(ccss)

#######################
# Here, we will use :py:class:`~pynwb.icephys.VoltageClampSeries` to store voltage clamp
# data and then add it to our NWBFile as acquired data using the :py:class:`~pynwb.file.NWBFile` method
# :py:meth:`~pynwb.file.NWBFile.add_acquisition`.

from pynwb.icephys import VoltageClampSeries

vcs = VoltageClampSeries(
    name='vcs', data=[0.1, 0.2, 0.3, 0.4, 0.5],
    unit='A', conversion=1e-12, resolution=np.nan, starting_time=123.6, rate=20e3,
    electrode=elec, gain=0.02, capacitance_slow=100e-12, resistance_comp_correction=70.0,
    capacitance_fast=np.nan, resistance_comp_bandwidth=np.nan, resistance_comp_prediction=np.nan,
    whole_cell_capacitance_comp=np.nan, whole_cell_series_resistance_comp=np.nan)

nwbfile.add_acquisition(vcs)

####################
# .. _icephys_writing:
#
# Once you have finished adding all of your data to the :py:class:`~pynwb.file.NWBFile`,
# write the file with :py:class:`~pynwb.NWBHDF5IO`.

from pynwb import NWBHDF5IO

io = NWBHDF5IO('icephys_example.nwb', 'w')
io.write(nwbfile)
io.close()

####################
# For more details on :py:class:`~pynwb.NWBHDF5IO`, see the :ref:`basic tutorial <basic_writing>`.

####################
# .. _icephys_reading:
#
# Reading electrophysiology data
# ------------------------------
#
# Now that you have written some intracellular electrophysiology data, you can read it back in.

io = NWBHDF5IO('icephys_example.nwb', 'r')
nwbfile = io.read()

####################
# For details on retrieving data from an :py:class:`~pynwb.file.NWBFile`, we refer the reader to the
# :ref:`basic tutorial <basic_reading>`. For this tutorial, we will just get back our the
# :py:class:`~pynwb.icephys.CurrentClampStimulusSeries` object we added above.
#
# First, get the :py:class:`~pynwb.icephys.CurrentClampStimulusSeries` we added as stimulus data.

ccss = nwbfile.get_stimulus('ccss')

####################
# Grabbing acquisition data an be done via :py:meth:`~pynwb.file.NWBFile.get_acquisition`

vcs = nwbfile.get_acquisition('vcs')

####################
# We can also get back the electrode we added.

elec = nwbfile.get_ic_electrode('elec0')

####################
# Alternatively, we can also get this electrode from the :py:class:`~pynwb.icephys.CurrentClampStimulusSeries`
# we retrieved above. This is exposed via the :py:meth:`~pynwb.icephys.PatchClampSeries.electrode` attribute.

elec = ccss.electrode

####################
# And the device name via :py:meth:`~pynbwb.file.NWBFile.get_device`

device = nwbfile.get_device('Heka ITC-1600')
