"""
.. _linking_data:

Modular Data Storage using External Files
===========================================

PyNWB supports linking between files using external links.

Example Use Case: Integrating data from multiple files
---------------------------------------------------------

NBWContainer classes (e.g., :py:class:`~pynwb.base.TimeSeries`) support the integration of data stored in external
HDF5 files with NWB data files via external links. To make things more concrete, let's look at the following use
case. We want to simultaneously record multiple data streams during data acquisition. Using the concept of external
links allows us to save each data stream to an external HDF5 files during data acquisition and to
afterward link the data into a single NWB file. In this case, each recording becomes represented by a
separate file-system object that can be set as read-only once the experiment is done.  In the following
we are using :py:meth:`~pynwb.base.TimeSeries` as an example, but the same approach works for other
NWBContainers as well.

.. tip::

    The same strategies we use here for creating External Links also apply to Soft Links.
    The main difference between soft and external links is that soft links point to other
    objects within the same file while external links point to objects in external files.

 .. tip::

    In the case of :py:meth:`~pynwb.base.TimeSeries`, the uncorrected timestamps generated by the acquisition
    system can be stored (or linked) in the *sync* group. In the NWB format, hardware-recorded time data
    must then be corrected to a common time base (e.g., timestamps from all hardware sources aligned) before
    it can be included in the *timestamps* of the *TimeSeries*. This means, in the case
    of :py:meth:`~pynwb.base.TimeSeries` we need to be careful that we are not including data with incompatible
    timestamps in the same file when using external links.


.. warning::

    External links can become stale/break. Since external links are pointing to data in other files
    external links may become invalid any time files are modified on the file system, e.g., renamed,
    moved or access permissions are changed.


Creating test data
^^^^^^^^^^^^^^^^^^

In the following we are creating two :py:meth:`~pynwb.base.TimeSeries` each written to a separate file.
We then show how we can integrate these files into a single NWBFile.
"""

# sphinx_gallery_thumbnail_path = 'figures/gallery_thumbnails_linking_data.png'

from datetime import datetime
from uuid import uuid4

import numpy as np
from dateutil.tz import tzlocal

from pynwb import NWBHDF5IO, NWBFile, TimeSeries

# Create the base data
start_time = datetime(2017, 4, 3, 11, tzinfo=tzlocal())
data = np.arange(1000).reshape((100, 10))
timestamps = np.arange(100, dtype=float)
filename1 = "external1_example.nwb"
filename2 = "external2_example.nwb"
filename3 = "external_linkcontainer_example.nwb"
filename4 = "external_linkdataset_example.nwb"

# Create the first file
nwbfile1 = NWBFile(
    session_description="demonstrate external files",
    identifier=str(uuid4()),
    session_start_time=start_time,
)
# Create the second file
test_ts1 = TimeSeries(
    name="test_timeseries1", data=data, unit="SIunit", timestamps=timestamps
)
nwbfile1.add_acquisition(test_ts1)

# Write the first file
with NWBHDF5IO(filename1, "w") as io:
    io.write(nwbfile1)

# Create the second file
nwbfile2 = NWBFile(
    session_description="demonstrate external files",
    identifier=str(uuid4()),
    session_start_time=start_time,
)
# Create the second file
test_ts2 = TimeSeries(
    name="test_timeseries2",
    data=data,
    unit="SIunit",
    timestamps=timestamps,
)
nwbfile2.add_acquisition(test_ts2)

# Write the second file
with NWBHDF5IO(filename2, "w") as io:
    io.write(nwbfile2)


#####################
# Linking to select datasets
# ^^^^^^^^^^^^^^^^^^^^^^^^^^
#

####################
# Step 1: Create the new NWBFile
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Create the first file
nwbfile4 = NWBFile(
    session_description="demonstrate external files",
    identifier=str(uuid4()),
    session_start_time=start_time,
)


####################
# Step 2: Get the dataset you want to link to
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Now let's open our test files and retrieve our timeseries.
#

# Get the first timeseries
io1 = NWBHDF5IO(filename1, "r")
nwbfile1 = io1.read()
timeseries_1 = nwbfile1.get_acquisition("test_timeseries1")
timeseries_1_data = timeseries_1.data

####################
# Step 3: Create the object you want to link to the data
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# To link to the dataset we can simply assign the data object (here `` timeseries_1.data``) to a new ``TimeSeries``

# Create a new timeseries that links to our data
test_ts4 = TimeSeries(
    name="test_timeseries4",
    data=timeseries_1_data,  # <-------
    unit="SIunit",
    timestamps=timestamps,
)
nwbfile4.add_acquisition(test_ts4)

####################
# In the above case we did not make it explicit how we want to handle the data from
# our TimeSeries, this means that :py:class:`~pynwb.NWBHDF5IO` will need to
# determine on write how to treat the dataset. We can make this explicit and customize this
# behavior on a per-dataset basis by wrapping our dataset using
# :py:class:`~hdmf.backends.hdf5.h5_utils.H5DataIO`

from hdmf.backends.hdf5.h5_utils import H5DataIO

# Create another timeseries that links to the same data
test_ts5 = TimeSeries(
    name="test_timeseries5",
    data=H5DataIO(data=timeseries_1_data, link_data=True),  # <-------
    unit="SIunit",
    timestamps=timestamps,
)
nwbfile4.add_acquisition(test_ts5)

####################
# Step 4: Write the data
# ~~~~~~~~~~~~~~~~~~~~~~~~
#
with NWBHDF5IO(filename4, "w") as io4:
    # Use link_data=True to specify default behavior to link rather than copy data
    io4.write(nwbfile4, link_data=True)
io1.close()

#####################
# .. note::
#
#   In the case of TimeSeries one advantage of linking to just the main dataset is that we can now
#   use our own timestamps in case the timestamps in the original file are not aligned with the
#   clock of the NWBFile we are creating. In this way we can use the linking to "re-align" different
#   TimeSeries without having to copy the main data.


####################
# Linking to whole Containers
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# Appending to files and linking is made possible by passing around the same
# :py:class:`~hdmf.build.manager.BuildManager`. You can get a manager to pass around
# using the :py:meth:`~pynwb.get_manager` function.
#

from pynwb import get_manager

manager = get_manager()

####################
# .. tip::
#
#    You can pass in extensions to :py:meth:`~pynwb.get_manager` using the *extensions* argument.

####################
# Step 1: Get the container object you want to link to
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Now let's open our test files and retrieve our timeseries.
#

# Get the first timeseries
io1 = NWBHDF5IO(filename1, "r", manager=manager)
nwbfile1 = io1.read()
timeseries_1 = nwbfile1.get_acquisition("test_timeseries1")

# Get the second timeseries
io2 = NWBHDF5IO(filename2, "r", manager=manager)
nwbfile2 = io2.read()
timeseries_2 = nwbfile2.get_acquisition("test_timeseries2")

####################
# Step 2: Add the container to another NWBFile
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# To integrate both :py:meth:`~pynwb.base.TimeSeries` into a single file we simply create a new
# :py:meth:`~pynwb.file.NWBFile` and add our existing :py:meth:`~pynwb.base.TimeSeries` to it. PyNWB's
# :py:class:`~pynwb.NWBHDF5IO` backend then automatically detects that the TimeSeries have already
# been written to another file and will create external links for us.
#

# Create a new NWBFile that links to the external timeseries
nwbfile3 = NWBFile(
    session_description="demonstrate external files",
    identifier=str(uuid4()),
    session_start_time=start_time,
)
nwbfile3.add_acquisition(timeseries_1)  # <--------
nwbfile3.add_acquisition(timeseries_2)  # <--------

# Write our third file that includes our two timeseries as external links
with NWBHDF5IO(filename3, "w", manager=manager) as io3:
    io3.write(nwbfile3)
io1.close()
io2.close()


####################
# Copying an NWBFile for linking
# ------------------------------
#
# Using the :py:func:`~pynwb.file.NWBFile.copy` method allows us to easily create a shallow copy
# of a whole NWB file with links to all data in the original file. For example, we may want to
# store processed data in a new file separate from the raw data, while still being able to access
# the raw data. See the :ref:`scratch` tutorial for a detailed example.
#

####################
# Creating a single file for sharing
# -----------------------------------
#
# External links are convenient but to share data we may want to hand a single file with all the
# data to our collaborator rather than having to collect all relevant files. To do this,
# :py:class:`~hdmf.backends.hdf5.h5tools.HDF5IO` (and in turn :py:class:`~pynwb.NWBHDF5IO`)
# provide the convenience function :py:meth:`~hdmf.backends.hdf5.h5tools.HDF5IO.export`,
# which can copy the file and resolves all external links.


####################
# Automatically splitting large data across multiple HDF5 files
# -------------------------------------------------------------------
#
# For extremely large datasets it can be useful to split data across multiple files, e.g., in cases where
# the file stystem does not allow for large files. While we can
# achieve this by writing different components (e.g., :py:meth:`~pynwb.base.TimeSeries`) to different files as described above,
# this option does not allow splitting data from single datasets. An alternative option is to use the
# ``family`` driver in ``h5py`` to automatically split the NWB file into a collection of many HDF5 files.
# The ``family`` driver stores the file on disk as a series of fixed-length chunks (each in its own file).
# In practice, to write very large arrays, we can combine this approach with :ref:`iterative_write` to
# avoid having to load all data into memory. In the example shown here we use a manual approach to
# iterative write by using :py:class:`~hdmf.backends.hdf5.h5_utils.H5DataIO` to create an empty dataset and
# then filling in the data afterward.

####################
# Step 1: Create the NWBFile as usual
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

from pynwb import NWBFile
from pynwb.base import TimeSeries
from datetime import datetime
from hdmf.backends.hdf5 import H5DataIO
import numpy as np

# Create an NWBFile object
nwbfile = NWBFile(session_description='example file family',
                  identifier=str(uuid4()),
                  session_start_time=datetime.now().astimezone())

# Create the data as an empty dataset so that we can write to it later
data = H5DataIO(maxshape=(None, 10),  # make the first dimension expandable
                dtype=np.float32,     # create the data as float32
                shape=(0, 10),        # initial data shape to initialize as empty dataset
                chunks=(1000, 10)
                )

# Create a TimeSeries object
time_series = TimeSeries(name='example_timeseries',
                         data=data,
                         starting_time=0.0,
                         rate=1.0,
                         unit='mV')

# Add the TimeSeries to the NWBFile
nwbfile.add_acquisition(time_series)

####################
# Step 2: Open the new file with the `family` driver and write
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# Here we need to open the file with `h5py` first to set up the driver, and then we can use
# that file with :py:class:`pynwb.NWBHDF5IO`. This is required, because :py:class:`pynwb.NWBHDF5IO`
# currently does not support passing the `memb_size` option required by the `family` driver.

import h5py
from pynwb import  NWBHDF5IO

# Define the size of the individual files, determining the number of files to create
# chunk_size = 1 * 1024**3  # 1GB per file
chunk_size = 1024**2  # 1MB just for testing

# filename pattern
filename_pattern = 'family_nwb_file_%d.nwb'

# Create the HDF5 file using the family driver
with h5py.File(name=filename_pattern, mode='w', driver='family', memb_size=chunk_size) as f:

    # Use NWBHDF5IO to write the NWBFile to the HDF5 file
    with NWBHDF5IO(file=f, mode='w') as io:
        io.write(nwbfile)

        # Write new data iteratively to the file
        for i in range(10):
            start_index = i * 1000
            stop_index = start_index + 1000
            data.dataset.resize((stop_index, 10))          # Resize the dataset
            data.dataset[start_index: stop_index , :] = i  # Set the additional values

####################
# .. note::
#
#    Alternatively, we could have also used the :ref:`iterative_write` features to write the data
#    iteratively directly as part of the `io.write` call instead of manually afterward.

####################
# Step 3: Read a file written with the family driver
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#


# Open the HDF5 file using the family driver
with h5py.File(name=filename_pattern, mode='r', driver='family', memb_size=chunk_size) as f:
    # Use NWBHDF5IO to read the NWBFile from the HDF5 file
    with NWBHDF5IO(file=f, manager=None, mode='r') as io:
        nwbfile = io.read()
        print(nwbfile)


####################
# .. note::
#
#    The filename you provide when using the ``family`` driver must contain a printf-style integer format code
#    (e.g.`%d`), which will be replaced by the file sequence number.
#
# .. note::
#
#    The ``memb_size`` parameter must be set on both write and read. As such, reading the file requires
#    the user to know the ``memb_size`` that was used for writing.
#
# .. note::
#
#    The DANDI archive may not support NWB files that are split in this fashion.
#
# .. note::
#
#    Other file drivers, e.g., `split` or `multi` could be used in a similar fashion.
#    However, not all HDF5 drivers are supported by the the high-level API of
#    `h5py` and as such may require a bit more complex setup via the the
#    low-level HDF5 API in `h5py`.
#

