"""
.. _editing:

Editing NWB files
=================

This tutorial demonstrates how to edit NWB files in-place to make small changes to
existing containers. To add or remove containers from an NWB file, see
:ref:`modifying_data`. How and whether it is possible to edit an NWB file depends on the
storage backend and the type of edit.

.. warning::

     Manually editing an existing NWB file can make the file invalid if you are not
     careful. We highly recommend making a copy before editing and running a validation
     check on the file after editing it. See :ref:`validating`.


Editing datasets
----------------
When reading an HDF5 NWB file, PyNWB exposes :py:class:`h5py.Dataset` objects, which can
be edited in place. For this to work, you must open the file in read/write mode
(``"r+"`` or ``"a"``).

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
# Now, let's edit the values of the dataset

with NWBHDF5IO("test_edit.nwb", "r+") as io:
    nwbfile = io.read()
    nwbfile.acquisition["synthetic_timeseries"].data[:10] = 0.0


##############################################
# You can edit the attributes of that dataset through the ``attrs`` attribute:

with NWBHDF5IO("test_edit.nwb", "r+") as io:
    nwbfile = io.read()
    nwbfile.acquisition["synthetic_timeseries"].data.attrs["unit"] = "volts"

##############################################
# Changing the shape of dataset
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Whether it is possible to change the shape of a dataset depends on how the dataset was
# created. If the dataset was created with a flexible shape, then it is possible to
# change in-place. Creating a dataset with a flexible shape is done by specifying the
# ``maxshape`` argument of the :py:class:`~hdmf.backends.hdf5.h5_utils.H5DataIO` class
# constructor. Using a ``None`` value for a component of the ``maxshape`` tuple allows
# the size of the corresponding dimension to grow, such that is can be be reset arbitrarily long
# in that dimension. Chunking is required for datasets with flexible shapes. Setting ``maxshape``,
# hence,  automatically sets chunking to ``True``, if not specified.
#
# First, let's create an NWB file with a dataset with a flexible shape:

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
# The ``None`` value  in the first component of ``maxshape`` means that the
# the first dimension of the dataset is unlimited. By setting the second dimension
# of ``maxshape`` to ``100``, that dimension is fixed to be no larger than ``100``.
# If you do not specify a``maxshape``, then the shape of the dataset will be fixed
# to the shape that the dataset was created with. Here, you can change the shape of
# the first dimension of this dataset.


with NWBHDF5IO("test_edit2.nwb", "r+") as io:
    nwbfile = io.read()
    nwbfile.acquisition["synthetic_timeseries"].data.resize((200, 100))

##############################################
# This will change the shape of the dataset in-place. If you try to change the shape of
# a dataset with a fixed shape, you will get an error.
#
# .. note::
#   There are several types of dataset edits that cannot be done in-place: changing the
#   shape of a dataset with a fixed shape, or changing the datatype, compression,
#   chunking, max-shape, or fill-value of a dataset. For any of these, we recommend using
#   the :py:class:`pynwb.NWBHDF5IO.export` method to export the data to a new file. See
#   :ref:`modifying_data` for more information.
#
# Editing groups
# --------------
# Editing of groups is not yet supported in PyNWB.
# To edit the attributes of a group, open the file and edit it using ``h5py``:

import h5py

with h5py.File("test_edit.nwb", "r+") as f:
    f["acquisition"]["synthetic_timeseries"].attrs["description"] = "Random values in volts"

##############################################
# .. warning::
#    Be careful not to edit values that will bring the file out of compliance with the
#    NWB specification.
#
# Renaming groups and datasets
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Rename groups and datasets in-place using the :py:meth:`~h5py.Group.move` method. For example, to rename
# the ``"synthetic_timeseries"`` group:

with h5py.File("test_edit.nwb", "r+") as f:
    f["acquisition"].move("synthetic_timeseries", "synthetic_timeseries_renamed")

##############################################
# You can use this same technique to move a group or dataset to a different location in
# the file. For example, to move the ``"synthetic_timeseries_renamed"`` group to the
# ``"analysis"`` group:

with h5py.File("test_edit.nwb", "r+") as f:
    f["acquisition"].move(
        "synthetic_timeseries_renamed",
        "/analysis/synthetic_timeseries_renamed",
    )
