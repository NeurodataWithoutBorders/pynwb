"""
Editing NWB files
=================

This tutorial demonstrates how to edit NWB files. How and whether it is possible to edit
an NWB file depends on the storage backend and the type of edit. Here, we go through the
common types of edits for HDF5 files. Keep in mind that any edit to an existing NWB file
make it no longer a valid NWB file. We highly recommend making a copy before
editing and running a validation check on the file after editing it.

In-place editing with h5py
---------------------------

Editing a dataset value
~~~~~~~~~~~~~~~~~~~~~~~
You can  change the value(s) of a dataset using :py:mod:`h5py`.

First, let's create an NWB file with data:
"""
from pynwb import NWBHDF5IO, NWBFile, TimeSeries
from datetime import datetime
from dateutil.tz import tzlocal
import numpy as np

nwbfile = NWBFile(
    session_description="my first synthetic recording",
    identifier="EXAMPLE_ID",
    session_start_time=datetime.now(tzlocal()),
    session_id="LONELYMTN",
)

nwbfile.add_acquisition(
    TimeSeries(
        name="synthetic_timeseries",
        description="Random values",
        data=np.random.randn(100, 100),
        unit="m",
        rate=10e3,
    )
)

with NWBHDF5IO("test_edit.nwb", "w") as io:
    io.write(nwbfile)


##############################################
# Now, let's try to edit the values of the dataset:
import h5py

with h5py.File("test_edit.nwb", "r+") as f:
    f["acquisition"]["synthetic_timeseries"]["data"][:10] = 0.0

##############################################
# This will edit the dataset in-place, and should work for all datasets. You can also
# edit attributes in-place:

with h5py.File("test_edit.nwb", "r+") as f:
    f["acquisition"]["synthetic_timeseries"]["data"].attrs["unit"] = "volts"


# Changing the shape of dataset
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Whether it is possible to change the shape of a dataset depends on how the dataset was
# created. If the dataset was created with a flexible shape, then it is possible to
# change in-place. Creating a dataset with a flexible shape is done by specifying the
# ``maxshape`` argument of the :py:class:`~hdmf.backends.hdf5.h5_utils.H5DataIO` class
# constructor. Using a ``None`` value for ``maxshape`` allows the dataset to be reset
# arbitrarily long in that dimension. Chunking is required for datasets with flexible
# shapes. Setting ``maxshape`` automatically sets chunking to ``True`, if not specified.
#
# First, let's create an NWB file with a dataset with a flexible shape:

from pynwb import NWBHDF5IO, NWBFile, TimeSeries
from datetime import datetime
from dateutil.tz import tzlocal
import numpy as np
from hdmf.backends.hdf5.h5_utils import H5DataIO

nwbfile = NWBFile(
    session_description="my first synthetic recording",
    identifier="EXAMPLE_ID",
    session_start_time=datetime.now(tzlocal()),
    session_id="LONELYMTN",
)

data_io = H5DataIO(data=np.random.randn(100, 100), maxshape=(None, 100))

nwbfile.add_acquisition(
    TimeSeries(
        name="synthetic_timeseries",
        description="Random values",
        data=data_io,
        unit="m",
        rate=10e3,
    )
)

with NWBHDF5IO("test_edit2.nwb", "w") as io:
    io.write(nwbfile)

##############################################
# The ``None`` in ``maxshape`` means that the dataset has an unlimited shape. You can
# also use an integer to specify a fixed ``maxshape``. If you do not specify a
# ``maxshape``, then the dataset will have a fixed shape. You can change the shape of
# this dataset.

import h5py

with h5py.File("test_edit2.nwb", "r+") as f:
    f["acquisition"]["synthetic_timeseries"]["data"].resize((200, 100))

##############################################
# This will change the shape of the dataset in-place. If you try to change the shape of
# a dataset with a fixed shape, you will get an error:
#
# .. code-block:: python
#   import h5py
#
#   with h5py.File("test_edit.nwb", "r+") as f:
#       f["acquisition"]["synthetic_timeseries"]["data"].resize((200, 100))
#
#   ValueError: Unable to resize dataset (no object or chunk storage)
#
# Replacing a dataset in h5py
# ----------------------------
# There are several types of dataset edits that cannot be done in-place.
#
#     * Changing the shape of a dataset with a fixed shape
#     * Changing the datatype of a dataset
#     * Changing the compression of a dataset
#     * Changing the chunking of a dataset
#     * Changing the max-shape of a dataset
#     * Changing the fill-value of a dataset
#
# For any of these, you will need to create a new dataset with the new shape, copying
# the data from the old dataset to the new dataset, and deleting the old dataset.

with h5py.File("test_edit2.nwb", "r+") as f:
    data = f["acquisition"]["synthetic_timeseries"]["data"][:]
    del f["acquisition"]["synthetic_timeseries"]["data"]
    f["acquisition"]["synthetic_timeseries"].create_dataset(
        name="data",
        data=data,
        maxshape=(None, 100),
        chunks=(100, 100),
        compression="gzip",
        compression_opts=3,
        fillvalue=0.0,
        dtype=np.float64,
    )

##############################################
# .. note::
#   Because of the way HDF5 works, the ``del`` action will not actually free up any
#   space in the HDF5 file. To free up space in the file, you will need to run the
#   ``h5repack`` command line tool. See the `h5repack documentation
#   <https://support.hdfgroup.org/HDF5/doc/RM/Tools.html#Tools-Repack>`_ for more
#   information.
