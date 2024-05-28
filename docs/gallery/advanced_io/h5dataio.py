"""
Defining HDF5 Dataset I/O Settings (chunking, compression, etc.)
================================================================

The HDF5 storage backend supports a broad range of advanced dataset I/O options, such as,
chunking and compression. Here we demonstrate how to use these features
from PyNWB.
"""

####################
# Wrapping data arrays with :py:class:`~hdmf.backends.hdf5.h5_utils.H5DataIO`
# ---------------------------------------------------------------------------
#
# In order to customize the I/O of datasets using the HDF I/O backend we simply need to wrap our datasets
# using :py:class:`~hdmf.backends.hdf5.h5_utils.H5DataIO`. Using H5DataIO allows us to keep the Container
# classes independent of the I/O backend while still allowing us to customize HDF5-specific I/O features.
#
# Before we get started, lets create an NWBFile for testing so that we can add our data to it.
#

from datetime import datetime

from dateutil.tz import tzlocal

from pynwb import NWBFile

start_time = datetime(2017, 4, 3, 11, tzinfo=tzlocal())

nwbfile = NWBFile(
    session_description="demonstrate advanced HDF5 I/O features",
    identifier="NWB123",
    session_start_time=start_time,
)


####################
# Normally if we create a :py:class:`~pynwb.base.TimeSeries` we would do

import numpy as np

from pynwb import TimeSeries

data = np.arange(100, 200, 10)
timestamps = np.arange(10)
test_ts = TimeSeries(
    name="test_regular_timeseries",
    data=data,
    unit="SIunit",
    timestamps=timestamps,
)
nwbfile.add_acquisition(test_ts)

####################
# Now let's say we want to chunk and compress the recorded data values. We now simply need to wrap our data with
# :py:class:`~hdmf.backends.hdf5.h5_utils.H5DataIO`. Everything else remains the same

from hdmf.backends.hdf5.h5_utils import H5DataIO

test_ts = TimeSeries(
    name="test_compressed_timeseries",
    data=H5DataIO(data=data, compression=True),  # <----
    unit="SIunit",
    timestamps=timestamps,
)
nwbfile.add_acquisition(test_ts)

####################
# This simple approach gives us access to a broad range of advanced I/O features, such as, chunking and
# compression. For a complete list of all available settings see :py:class:`~hdmf.backends.hdf5.h5_utils.H5DataIO`.
# Here, the settings for chunking and compression are determined automatically.

####################
# Chunking
# --------
#
# By default, data arrays are stored *contiguously*. This means that on disk/in memory the elements of a
# multi-dimensional, such as, ```[[1 2] [3 4]]``` are actually stored in a one-dimensional buffer
# ```1 2 3 4```. Using chunking allows us to break up our array into chunks so that our array will be
# stored not in one but multiple buffers, e.g., ``[1 2] [3 4]``. Using this approach allows optimization
# of data locality for I/O operations and enables the application of filters (e.g., compression) on a
# per-chunk basis.

#####################
# .. tip::
#
#    For an introduction to chunking and compression in HDF5 and h5py in particular see also the online book
#    `Python and HDF5 <https://www.safaribooksonline.com/library/view/python-and-hdf5/9781491944981/ch04.html>`__
#    by Andrew Collette.


####################
# To use chunking we again, simply need to wrap our dataset via :py:class:`~hdmf.backends.hdf5.h5_utils.H5DataIO`.
# Using chunking then also allows to also create resizable arrays simply by defining the ``maxshape`` of the array.

data = np.arange(10000).reshape((1000, 10))
wrapped_data = H5DataIO(
    data=data,
    chunks=True,  # <---- Enable chunking
    maxshape=(None, 10),  # <---- Make the time dimension unlimited and hence resizable
)
test_ts = TimeSeries(
    name="test_chunked_timeseries",
    data=wrapped_data,  # <----
    unit="SIunit",
    starting_time=0.0,
    rate=10.0,
)
nwbfile.add_acquisition(test_ts)

####################
# .. hint::
#
#   By also specifying ``fillvalue`` we can define the value that should be used when reading uninitialized
#   portions of the dataset. If no fill value has been defined, then HDF5 will use a type-appropriate default value.
#

####################
# .. note::
#
#    Chunking can help improve data read/write performance by allowing us to align chunks with common
#    read/write operations. You can find a discussion on how chunking can help in the
#    `Python and HDF5 book  <https://www.oreilly.com/library/view/python-and-hdf5/9781491944981/ch04.html>`__.
#    by Andrew Collette. But you should also know that, with great power comes great responsibility! I.e., if you choose
#    a bad chunk size e.g., too small chunks that don't align with our read/write operations, then chunking can
#    also harm I/O performance.

####################
# Compression and Other I/O Filters
# ---------------------------------
#
# HDF5 supports I/O filters, i.e, data transformation (e.g, compression) that are applied transparently on
# read/write operations.  I/O filters operate on a per-chunk basis in HDF5 and as such require the use of chunking.
# Chunking will be automatically enabled by h5py when compression and other I/O filters are enabled.
#
# To use compression, we can wrap our dataset using :py:class:`~hdmf.backends.hdf5.h5_utils.H5DataIO` and
# define the appropriate options:

wrapped_data = H5DataIO(
    data=data,
    compression="gzip",  # <---- Use GZip
    compression_opts=4,  # <---- Optional GZip aggression option
)
test_ts = TimeSeries(
    name="test_gzipped_timeseries",
    data=wrapped_data,  # <----
    unit="SIunit",
    starting_time=0.0,
    rate=10.0,
)
nwbfile.add_acquisition(test_ts)

####################
# .. hint::
#
#   In addition to ``compression``, :py:class:`~hdmf.backends.hdf5.h5_utils.H5DataIO` also allows us to
#   enable the ``shuffle`` and ``fletcher32`` HDF5 I/O filters.

####################
# Writing the data
# ----------------
#
#
# Writing the data now works as usual.

from pynwb import NWBHDF5IO

with NWBHDF5IO("advanced_io_example.nwb", "w") as io:
    io.write(nwbfile)

####################
# Reading the data
# ----------------
#
#
# Nothing has changed for read. All the above advanced I/O features are handled transparently.

io = NWBHDF5IO("advanced_io_example.nwb", "r")
nwbfile = io.read()

####################
# Now lets have a look to confirm that all our I/O settings where indeed used.

for k, v in nwbfile.acquisition.items():
    print(
        "name=%s, chunks=%s, compression=%s, maxshape=%s"
        % (k, v.data.chunks, v.data.compression, v.data.maxshape)
    )
io.close()
####################
#
# .. code-block:: python
#
#   name=test_regular_timeseries, chunks=None, compression=None, maxshape=(10,)
#   name=test_compressed_timeseries, chunks=(10,), compression=gzip, maxshape=(10,)
#   name=test_chunked_timeseries, chunks=(250, 5), compression=None, maxshape=(None, 10)
#   name=test_gzipped_timeseries, chunks=(250, 5), compression=gzip, maxshape=(1000, 10)
#
# As we can see, the datasets have been chunked and compressed correctly. Also, as expected, chunking
# was automatically enabled for the compressed datasets.


####################
# Wrapping ``h5py.Datasets`` with :py:class:`~hdmf.backends.hdf5.h5_utils.H5DataIO`
# ---------------------------------------------------------------------------------
#
# Just for completeness, :py:class:`~hdmf.backends.hdf5.h5_utils.H5DataIO` also allows us to customize
# how ``h5py.Dataset`` objects should be handled on write by the PyNWBs HDF5 backend via the ``link_data``
# parameter. If ``link_data`` is set to ``True`` then a ``SoftLink`` or ``ExternalLink`` will be created to
# point to the HDF5 dataset On the other hand, if ``link_data`` is set to ``False`` then the dataset
# be copied using `h5py.Group.copy <https://docs.h5py.org/en/latest/high/group.html#h5py.Group.copy>`__
# **without copying attributes** and **without expanding soft links, external links, or references**.
#
# .. note::
#
#   When wrapping an ``h5py.Dataset`` object using H5DataIO, then  all settings except ``link_data``
#   will be ignored as the h5py.Dataset will either be linked to or copied as on write.

####################
# Dynamically Loaded Filters
# --------------------------
#
# HDF5 allows you to install additional filters and use these filters as plugins. Some of these filters may have
# superior performance to the default *GZIP* when it comes to read speed, write speed, or compression ratio. You can
# install several of the most popular filter plugins using the
# `hdf5plugin library <http://www.silx.org/doc/hdf5plugin/latest/index.html>`_.
#
# First, use ``pip`` to install hdf5plugin:
#
# ``pip install hdf5plugin``

####################
# This command automatically installs the filters. Here is an example of how you would use the Z Standard algorithm:

import hdf5plugin
from hdmf.backends.hdf5.h5_utils import H5DataIO

from pynwb.file import TimeSeries

wrapped_data = H5DataIO(
    data=data,
    **hdf5plugin.Zstd(clevel=3),  # set the compression and compression_opts parameters
    allow_plugin_filters=True,
)

test_ts = TimeSeries(
    name="test_gzipped_timeseries",
    data=wrapped_data,
    unit="SIunit",
    starting_time=0.0,
    rate=10.0,
)

####################
# See a list of supported compressors
# `here <http://www.silx.org/doc/hdf5plugin/latest/usage.html#write-compressed-datasets>`_.

####################
# .. note::
#
#    *h5py* (and *HDF5* more broadly) supports a number of different compression
#    algorithms, e.g., *GZIP*, *SZIP*, or *LZF* (or even custom compression filters).
#    However, only *GZIP* is built by default with HDF5, i.e., while data compressed
#    with *GZIP* can be read on all platforms and installation of HDF5, other
#    compressors may not be installed, so some users may not be able to access those
#    datasets.

####################
# Disclaimer
# ----------
#
# External links included in the tutorial are being provided as a convenience and for informational purposes only;
# they do not constitute an endorsement or an approval by the authors of any of the products, services or opinions of
# the corporation or organization or individual. The authors bear no responsibility for the accuracy, legality or
# content of the external site or for that of subsequent links. Contact the external site for answers to questions
# regarding its content.

# sphinx_gallery_thumbnail_path = 'figures/gallery_thumbnails_h5dataio.png'
