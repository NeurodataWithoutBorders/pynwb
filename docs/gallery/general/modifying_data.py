"""
.. _modifying_data:

Modifying data in an NWB file
=========================================

This tutorial will focus on how to modify data from an existing NWB file and write the data back to the
same NWB file or export the data to a new NWB file.
"""

###############################################################################
# Modifying an NWB file in read/write mode
# --------------------------------------------
# PyNWB supports modifying an existing NWB file - that is, reading data from an NWB file, modifying that data, and
# writing the modified data back to the same NWB file on disk. To do so, open the file with an
# :py:class:`~pynwb.NWBHDF5IO` object in read/write mode (``mode='r+'`` or ``mode='a'``), read the file contents,
# modify the :py:class:`~pynwb.file.NWBFile` or one of its containers in memory, and write the modified .
# :py:class:`~pynwb.file.NWBFile` using the same :py:class:`~pynwb.NWBHDF5IO` object.
#
# For example:

from pynwb import NWBFile, NWBHDF5IO, TimeSeries
import datetime

# first, write a test NWB file
nwbfile = NWBFile(
    session_description='demonstrate export of NWB files',
    identifier='NWB123',
    session_start_time=datetime.datetime.now(datetime.timezone.utc),
)

filename = 'nwbfile.nwb'
with NWBHDF5IO(filename, 'w') as io:
    io.write(nwbfile)

# open the NWB file in r+ mode
with NWBHDF5IO(filename, 'r+') as io:
    read_nwbfile = io.read()

    # create a TimeSeries and add it to the file under the acquisition group
    data = list(range(100, 200, 10))
    timestamps = list(range(10))
    test_ts = TimeSeries(
        name='test_timeseries',
        data=data,
        unit='m',
        timestamps=timestamps
    )
    nwbfile.add_acquisition(test_ts)

    # write the modified NWB file
    io.write(read_nwbfile)

breakpoint()

###############################################################################
# Modifying an NWB file in this way has limitations. Removal of data will not shrink the file size.
# A different method -- export -- which is detailed below, must be used to remove data from an existing NWB file.
# However, addition of data, such as new `:py:class:`~pynwb.base.TimeSeries` objects in the example above,
# can easily be done.

#
#
#
###############################################################################
# .. warning::
#
#   NWB datasets that have been written to disk are read as :py:class:`h5py.Dataset <h5py.Dataset>` objects. If you
#   modify the data in these ``Dataset`` objects directly, the data is modified on disk immediately (the
#   :py:meth:`~pynwb.NWBHDF5IO.write` method does not need to be called and the :py:class:`~pynwb.NWBHDF5IO`
#   instance does not need to be closed. Modifying datasets directly in this way can lead to files that do not
#   validate or cannot be opened, so take caution when using this method.
#   Note: only chunked datasets or datasets with ``maxshape`` set can be resized.
#   See https://docs.h5py.org/en/stable/high/dataset.html#chunked-storage for more details.

###############################################################################
# Exporting a written NWB file to a new file path
# -----------------------------------------------
# To export an NWB file, first read the written NWB file, then create a new
# :py:class:`~pynwb.NWBHDF5IO` object for exporting the data, then call
# :py:meth:`~pynwb.NWBHDF5IO.export` on the
# :py:class:`~pynwb.NWBHDF5IO` object, passing in the IO object used to read the :py:class:`~pynwb.file.NWBFile`
# You may also pass in the :py:class:`~pynwb.file.NWBFile` itself, which may be modified in memory between
# reading and exporting.
#
# For example:

from pynwb import NWBFile, NWBHDF5IO
import datetime

# first, write a test NWB file
nwbfile = NWBFile(
    session_description='demonstrate export of NWB files',
    identifier='NWB123',
    session_start_time=datetime.datetime.now(datetime.timezone.utc),
)

filename = 'nwbfile.nwb'
with NWBHDF5IO(filename, 'w') as io:
    io.write(nwbfile)

export_filename = 'exported_nwbfile.nwb'
with NWBHDF5IO(filename, mode='r') as read_io:  # read the written file
    with NWBHDF5IO(export_filename, mode='w') as export_io:  # create a new IO object to export to a new file
        export_io.export(src_io=read_io)

###############################################################################
# Modifying a written NWB file and exporting it to a new file path
# ----------------------------------------------------------------
# The above example is analogous to using the file system to copy the file. However, the power of the export
# function comes from the ability to modify the NWB file in memory and write the modified NWB file to a new file path.
# You can add new container objects (e.g., `:py:class:`~pynwb.base.TimeSeries` objects) or remove existing ones.
# This is especially useful if you want to have raw data and processed data in the same NWB file and you want a new
# NWB file containing only the processed data.
#
# For example:

# first, create a test NWB file with a TimeSeries in the acquisition group

filename = 'nwbfile.nwb'
with NWBHDF5IO(filename, 'w') as io:
    io.write(nwbfile)

# read the written file
with NWBHDF5IO(filename, mode='r') as read_io:
    read_nwbfile = read_io.read()

    # remove the TimeSeries from the acquisition group
    read_nwbfile.acquisition.pop('test_timeseries')

    export_filename = 'exported_nwbfile.nwb'
    with NWBHDF5IO(export_filename, mode='w') as export_io:
        export_io.export(src_io=read_io, nwbfile=read_nwbfile)

###############################################################################
# .. note::
#
#   Certain fields of the NWB file cannot be removed.
