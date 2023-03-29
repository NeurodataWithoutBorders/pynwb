# -*- coding: utf-8 -*-
"""
.. _icephys_tutorial:

Intracellular Electrophysiology Data using SweepTable
=====================================================

The following tutorial describes storage of intracellular electrophysiology data in NWB using the
SweepTable to manage recordings.

.. warning::
    The use of SweepTable has been deprecated as of PyNWB >v2.0 in favor of the new hierarchical
    intracellular electrophysiology metadata tables to allow for a more complete description of
    intracellular electrophysiology experiments. See the :doc:`Intracellular electrophysiology  <plot_icephys>`
    tutorial for details.
"""

#######################
# Creating and Writing NWB files
# ------------------------------
#
# When creating a NWB file, the first step is to create the :py:class:`~pynwb.file.NWBFile`. The first
# argument is is a brief description of the dataset.

# sphinx_gallery_thumbnail_path = 'figures/gallery_thumbnails_icephys_sweeptable.png'
from datetime import datetime
from uuid import uuid4

import numpy as np
from dateutil.tz import tzlocal

from pynwb import NWBFile

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
    session_id="LONELYMTN001",
)

#######################
# Device metadata
# ^^^^^^^^^^^^^^^
#
# Device metadata is represented by :py:class:`~pynwb.device.Device` objects.
# To create a device, you can use the :py:class:`~pynwb.device.Device` instance method
# :py:meth:`~pynwb.file.NWBFile.create_device`.

device = nwbfile.create_device(name="Heka ITC-1600")

#######################
# Electrode metadata
# ^^^^^^^^^^^^^^^^^^
#
# Intracellular electrode metadata is represented by :py:class:`~pynwb.icephys.IntracellularElectrode` objects.
# To create an electrode group, you can use the :py:class:`~pynwb.file.NWBFile` instance method
# :py:meth:`~pynwb.file.NWBFile.create_icephys_electrode`.

elec = nwbfile.create_icephys_electrode(
    name="elec0", description="a mock intracellular electrode", device=device
)

#######################
# Stimulus data
# ^^^^^^^^^^^^^
#
# Intracellular stimulus and response data are represented with subclasses of
# :py:class:`~pynwb.icephys.PatchClampSeries`. There are two classes for representing stimulus
# data
#
# - :py:class:`~pynwb.icephys.VoltageClampStimulusSeries`
# - :py:class:`~pynwb.icephys.CurrentClampStimulusSeries`
#
# and three classes for representing response
#
# - :py:class:`~pynwb.icephys.VoltageClampSeries`
# - :py:class:`~pynwb.icephys.CurrentClampSeries`
# - :py:class:`~pynwb.icephys.IZeroClampSeries`
#
# Here, we will use :py:class:`~pynwb.icephys.CurrentClampStimulusSeries` to store current clamp stimulus
# data and then add it to our NWBFile as stimulus data using the :py:class:`~pynwb.file.NWBFile` method
# :py:meth:`~pynwb.file.NWBFile.add_stimulus`.

from pynwb.icephys import CurrentClampStimulusSeries

ccss = CurrentClampStimulusSeries(
    name="ccss",
    data=[1, 2, 3, 4, 5],
    starting_time=123.6,
    rate=10e3,
    electrode=elec,
    gain=0.02,
    sweep_number=0,
)

nwbfile.add_stimulus(ccss, use_sweep_table=True)

#######################
# We now add another stimulus series but from a different sweep. TimeSeries
# having the same starting time belong to the same sweep.

from pynwb.icephys import VoltageClampStimulusSeries

vcss = VoltageClampStimulusSeries(
    name="vcss",
    data=[2, 3, 4, 5, 6],
    starting_time=234.5,
    rate=10e3,
    electrode=elec,
    gain=0.03,
    sweep_number=1,
)

nwbfile.add_stimulus(vcss, use_sweep_table=True)

#######################
# Here, we will use :py:class:`~pynwb.icephys.CurrentClampSeries` to store current clamp
# data and then add it to our NWBFile as acquired data using the :py:class:`~pynwb.file.NWBFile` method
# :py:meth:`~pynwb.file.NWBFile.add_acquisition`.

from pynwb.icephys import CurrentClampSeries

ccs = CurrentClampSeries(
    name="ccs",
    data=[0.1, 0.2, 0.3, 0.4, 0.5],
    conversion=1e-12,
    resolution=np.nan,
    starting_time=123.6,
    rate=20e3,
    electrode=elec,
    gain=0.02,
    bias_current=1e-12,
    bridge_balance=70e6,
    capacitance_compensation=1e-12,
    sweep_number=0,
)

nwbfile.add_acquisition(ccs, use_sweep_table=True)

#######################
# And voltage clamp data from the second sweep using
# :py:class:`~pynwb.icephys.VoltageClampSeries`.

from pynwb.icephys import VoltageClampSeries

vcs = VoltageClampSeries(
    name="vcs",
    data=[0.1, 0.2, 0.3, 0.4, 0.5],
    conversion=1e-12,
    resolution=np.nan,
    starting_time=234.5,
    rate=20e3,
    electrode=elec,
    gain=0.02,
    capacitance_slow=100e-12,
    resistance_comp_correction=70.0,
    sweep_number=1,
)

nwbfile.add_acquisition(vcs, use_sweep_table=True)

####################
# .. _icephys_writing:
#
# Once you have finished adding all of your data to the :py:class:`~pynwb.file.NWBFile`,
# write the file with :py:class:`~pynwb.NWBHDF5IO`.

from pynwb import NWBHDF5IO

with NWBHDF5IO("icephys_example.nwb", "w") as io:
    io.write(nwbfile)

####################
# For more details on :py:class:`~pynwb.NWBHDF5IO`, see the :ref:`basic tutorial <basic_writing>`.

####################
# .. _icephys_reading:
#
# Reading electrophysiology data
# ------------------------------
#
# Now that you have written some intracellular electrophysiology data, you can read it back in.

io = NWBHDF5IO("icephys_example.nwb", "r")
nwbfile = io.read()

####################
# For details on retrieving data from an :py:class:`~pynwb.file.NWBFile`, we refer the reader to the
# :ref:`basic tutorial <basic_reading>`. For this tutorial, we will just get back our the
# :py:class:`~pynwb.icephys.CurrentClampStimulusSeries` object we added above.
#
# First, get the :py:class:`~pynwb.icephys.CurrentClampStimulusSeries` we added as stimulus data.

ccss = nwbfile.get_stimulus("ccss")

####################
# Grabbing acquisition data can be done via :py:meth:`~pynwb.file.NWBFile.get_acquisition`

vcs = nwbfile.get_acquisition("vcs")

####################
# We can also get back the electrode we added.

elec = nwbfile.get_icephys_electrode("elec0")

####################
# Alternatively, we can also get this electrode from the :py:class:`~pynwb.icephys.CurrentClampStimulusSeries`
# we retrieved above. This is exposed via the :py:meth:`~pynwb.icephys.PatchClampSeries.electrode` attribute.

elec = ccss.electrode

####################
# And the device name via :py:meth:`~pynwb.file.NWBFile.get_device`

device = nwbfile.get_device("Heka ITC-1600")

####################
# If you have data from multiple electrodes and multiple sweeps, it can be
# tedious and expensive to search all :py:class:`~pynwb.icephys.PatchClampSeries` for the
# :py:class:`~pynwb.base.TimeSeries` with a given sweep.
#
# Fortunately you don't have to do that manually, instead you can just query
# the :py:class:`~pynwb.icephys.SweepTable` which stores the mapping between the
# PatchClampSeries which belongs to a certain sweep number via
# :py:meth:`~pynwb.icephys.SweepTable.get_series`.
#
# The following call will return the voltage clamp data of two timeseries
# consisting of acquisition and stimulus, from sweep 1.

series = nwbfile.sweep_table.get_series(1)

# close the file
io.close()
