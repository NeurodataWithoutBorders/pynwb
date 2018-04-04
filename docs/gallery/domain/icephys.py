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
# argument is the source of the NWB file, and the second argument is a brief description of the dataset.

from datetime import datetime
from pynwb import NWBFile

nwbfile = NWBFile('the PyNWB tutorial', 'my first synthetic recording', 'EXAMPLE_ID', datetime.now(),
                  experimenter='Dr. Bilbo Baggins',
                  lab='Bag End Laboratory',
                  institution='University of Middle Earth at the Shire',
                  experiment_description='I went on an adventure with thirteen dwarves to reclaim vast treasures.',
                  session_id='LONELYMTN')

#######################
# Electrode metadata
# ^^^^^^^^^^^^^^^^^^
#
# Intracellular electrode metadata is represented by :py:class:`~pynwb.icephys.IntracellularElectrode` objects.
# To create an electrode group, you can use the :py:class:`~pynwb.file.NWBFile` instance method
# :py:meth:`~pynwb.file.NWBFile.create_ic_electrode`.

elec = nwbfile.create_ic_electrode(
    name="elec0", source='', slice='', resistance='', seal='', description='',
    location='', filtering='', initial_access_resistance='', device='')

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
    name="ccss", source="command", data=[1, 2, 3, 4, 5], unit='A',
    starting_time=123.6, rate=10e3, electrode=elec, gain=0.02)

nwbfile.add_stimulus(ccss)

####################
# .. _icephys_writing:
#
# Once you have finished adding all of your data to the :py:class:`~pynwb.NWBFile`,
# write the file with :py:class:`~pynwb.NWBHDF5IO`.

from pynwb import NWBHDF5IO

io = NWBHDF5IO('icephys_example.nwb', 'w')
io.write(nwbfile)
io.close()

####################
# For more details on :py:class:`~pynwb.NWBHDF5IO`, see the :ref:`basic tutorial <basic_writing>`.

####################
# .. _ecephys_reading:
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
# :py:class:`~pynwb.ecephys.ElectricalSeries` object we added above.
#
# First, get the  :py:class:`~pynwb.icephys.CurentClampStimulusSeries` we added as stimulus data.

ccss = nwbfile.get_stimulus('ccss')

####################
# We can also get back the electrode we added.

elec = nwbfile.get_ic_electrode('elec0')

####################
# Alternatively, we can also get this electrode from the :py:class:`~pynwb.icephys.CurentClampStimulusSeries`
# we retrieved above.

elec = ccss.electrode
