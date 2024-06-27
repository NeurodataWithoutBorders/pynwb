"""
.. _modifying_data:

Adding/Removing Containers from an NWB File
============================================

This tutorial explains how to add and remove containers from an existing NWB file and either write the data back to the
same file or export the data to a new file.
"""

###############################################################################
# Adding objects to an NWB file in read/write mode
# ----------------------------------------------------
# PyNWB supports adding container objects to an existing NWB file - that is, reading data from an NWB file, adding a
# container object, such as a new :py:class:`~pynwb.base.TimeSeries` object, and writing the modified
# :py:class:`~pynwb.file.NWBFile` back to the same file path on disk. To do so:
#
# 1. open the file with an :py:class:`~pynwb.NWBHDF5IO` object in read/write mode (``mode='r+'`` or ``mode='a'``)
# 2. read the :py:class:`~pynwb.file.NWBFile`
# 3. add container objects to the :py:class:`~pynwb.file.NWBFile` object
# 4. write the modified :py:class:`~pynwb.file.NWBFile` using the same :py:class:`~pynwb.NWBHDF5IO` object
#
# For example:

import datetime

import numpy as np

# sphinx_gallery_thumbnail_path = 'figures/gallery_thumbnails_add_remove_containers.png'
from pynwb import NWBHDF5IO, NWBFile, TimeSeries

# first, write a test NWB file
nwbfile = NWBFile(
    session_description="demonstrate adding to an NWB file",
    identifier="NWB123",
    session_start_time=datetime.datetime.now(datetime.timezone.utc),
)

filename = "nwbfile.nwb"
with NWBHDF5IO(filename, "w") as io:
    io.write(nwbfile)

# open the NWB file in r+ mode
with NWBHDF5IO(filename, "r+") as io:
    read_nwbfile = io.read()

    # create a TimeSeries and add it to the file under the acquisition group
    data = list(range(100, 200, 10))
    timestamps = np.arange(10, dtype=float)
    test_ts = TimeSeries(
        name="test_timeseries", data=data, unit="m", timestamps=timestamps
    )
    read_nwbfile.add_acquisition(test_ts)

    # write the modified NWB file
    io.write(read_nwbfile)

# confirm the file contains the new TimeSeries in acquisition
with NWBHDF5IO(filename, "r") as io:
    read_nwbfile = io.read()
    print(read_nwbfile)

###############################################################################
# .. note::
#
#   You cannot remove objects from an NWB file using the above method.

###############################################################################
# Modifying an NWB file in this way has limitations. The destination file path must be the same as the source
# file path, and it is not possible to remove objects from an NWB file. You can use the
# :py:meth:`NWBHDF5IO.export <pynwb.NWBHDF5IO.export>` method, detailed below, to modify an NWB file in these ways.
#
# Exporting a written NWB file to a new file path
# -----------------------------------------------
# Use the :py:meth:`NWBHDF5IO.export <pynwb.NWBHDF5IO.export>` method to read data from an existing NWB file,
# modify the data, and write the modified data to a new file path. Modifications to the data can be additions or
# removals of objects, such as :py:class:`~pynwb.base.TimeSeries` objects. This is especially useful if you
# have raw data and processed data in the same NWB file and you want to create a new NWB file with all the contents of
# the original file except for the raw data for sharing with collaborators.
#
# To remove existing containers, use the :py:meth:`~hdmf.utils.LabelledDict.pop` method on any
# :py:class:`~hdmf.utils.LabelledDict` object, such as ``NWBFile.acquisition``, ``NWBFile.processing``,
# ``NWBFile.analysis``, ``NWBFile.processing``, ``NWBFile.scratch``, ``NWBFile.devices``, ``NWBFile.stimulus``,
# ``NWBFile.stimulus_template``, ``NWBFile.electrode_groups``, ``NWBFile.imaging_planes``,
# ``NWBFile.icephys_electrodes``, ``NWBFile.ogen_sites``, ``NWBFile.lab_meta_data``,
# and :py:class:`~pynwb.base.ProcessingModule` objects.
#
# For example:

# first, create a test NWB file with a TimeSeries in the acquisition group
nwbfile = NWBFile(
    session_description="demonstrate export of an NWB file",
    identifier="NWB123",
    session_start_time=datetime.datetime.now(datetime.timezone.utc),
)
data1 = list(range(100, 200, 10))
timestamps1 = np.arange(10, dtype=float)
test_ts1 = TimeSeries(
    name="test_timeseries1", data=data1, unit="m", timestamps=timestamps1
)
nwbfile.add_acquisition(test_ts1)

# then, create a processing module for processed behavioral data
nwbfile.create_processing_module(
    name="behavior", description="processed behavioral data"
)
data2 = list(range(100, 200, 10))
timestamps2 = np.arange(10, dtype=float)
test_ts2 = TimeSeries(
    name="test_timeseries2", data=data2, unit="m", timestamps=timestamps2
)
nwbfile.processing["behavior"].add(test_ts2)

# write these objects to an NWB file
filename = "nwbfile.nwb"
with NWBHDF5IO(filename, "w") as io:
    io.write(nwbfile)

# read the written file
export_filename = "exported_nwbfile.nwb"
with NWBHDF5IO(filename, mode="r") as read_io:
    read_nwbfile = read_io.read()

    # add a new TimeSeries to the behavior processing module
    data3 = list(range(100, 200, 10))
    timestamps3 = np.arange(10, dtype=float)
    test_ts3 = TimeSeries(
        name="test_timeseries3", data=data3, unit="m", timestamps=timestamps3
    )
    read_nwbfile.processing["behavior"].add(test_ts3)

    # use the pop method to remove the original TimeSeries from the acquisition group
    read_nwbfile.acquisition.pop("test_timeseries1")

    # use the pop method to remove a TimeSeries from a processing module
    read_nwbfile.processing["behavior"].data_interfaces.pop("test_timeseries2")

    # call the export method to write the modified NWBFile instance to a new file path.
    # the original file is not modified
    with NWBHDF5IO(export_filename, mode="w") as export_io:
        export_io.export(src_io=read_io, nwbfile=read_nwbfile)

# confirm the exported file does not contain TimeSeries with names 'test_timeseries1' or 'test_timeseries2'
# but does contain a new TimeSeries in processing['behavior'] with name 'test_timeseries3'
with NWBHDF5IO(export_filename, "r") as io:
    read_nwbfile = io.read()
    print(read_nwbfile)
    print(read_nwbfile.processing["behavior"])

###############################################################################
# .. note::
#
#   :py:class:`~pynwb.epoch.TimeIntervals` objects, such as ``NWBFile.epochs``, ``NWBFile.trials``,
#   ``NWBFile.invalid_times``, and custom :py:class:`~pynwb.epoch.TimeIntervals` objects cannot be
#   removed (popped) from ``NWBFile.intervals``.

###############################################################################
# .. warning::
#
#   Removing an object from an NWBFile may break links and references within the file and across files.
#   This is analogous to having shortcuts/aliases to a file on your filesystem and then deleting the file.
#   Extra caution should be taken when removing heavily referenced items such as
#   :py:class:`~pynwb.device.Device` objects,
#   :py:class:`~pynwb.ecephys.ElectrodeGroup` objects, the electrodes table, and the
#   :py:class:`~pynwb.ophys.PlaneSegmentation` table.

###############################################################################
# Exporting with new object IDs
# ---------------------------------
# When exporting a read NWB file to a new file path, the object IDs within the original NWB file will be copied to the
# new file. To make the exported NWB file contain a new set of object IDs, call
# :py:meth:`~hdmf.container.AbstractContainer.generate_new_id` on your :py:class:`~pynwb.file.NWBFile` object.
# This will generate a new object ID for the :py:class:`~pynwb.file.NWBFile` object and all of the objects within
# the NWB file.

export_filename = "exported_nwbfile.nwb"
with NWBHDF5IO(filename, mode="r") as read_io:
    read_nwbfile = read_io.read()
    read_nwbfile.generate_new_id()

    with NWBHDF5IO(export_filename, mode="w") as export_io:
        export_io.export(src_io=read_io, nwbfile=read_nwbfile)

###############################################################################
# For more information about the export functionality, see :ref:`export`
# and the PyNWB documentation for :py:meth:`NWBHDF5IO.export <pynwb.NWBHDF5IO.export>`.
#
# For more information about editing a file in place, see :ref:`editing`.
