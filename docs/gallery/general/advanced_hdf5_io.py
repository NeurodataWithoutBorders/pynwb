'''
Advanced HDF5 I/O
=====================

The HDF5 storage backend supports a broad range of advanced dataset I/O options, such as,
chunking and compression. Here we demonstrate how to use these features
from PyNWB.
'''

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
create_date = datetime(2017, 4, 15, 12, tzinfo=tzlocal())

nwbfile = NWBFile(session_description='demonstrate advanced HDF5 I/O features',
                  identifier='NWB123',
                  session_start_time=start_time,
                  file_create_date=create_date)


####################
# Normally if we create a timeseries we would do

from pynwb import TimeSeries
import numpy as np

data = np.arange(100, 200, 10)
timestamps = np.arange(10)
test_ts = TimeSeries(name='test_regular_timeseries',
                     data=data,
                     unit='SIunit',
                     timestamps=timestamps)
nwbfile.add_acquisition(test_ts)

####################
# Now let's say we want to compress the recorded data values. We now simply need to wrap our data with H5DataIO.
# Everything else remains the same

from hdmf.backends.hdf5.h5_utils import H5DataIO
wrapped_data = H5DataIO(data=data, compression=True)     # <----
test_ts = TimeSeries(name='test_compressed_timeseries',
                     data=wrapped_data,                  # <----
                     unit='SIunit',
                     timestamps=timestamps)
nwbfile.add_acquisition(test_ts)

####################
# This simple approach gives us access to a broad range of advanced I/O features, such as, chunking and
# compression. For a complete list of all available settings see :py:class:`~hdmf.backends.hdf5.h5_utils.H5DataIO`

####################
# Chunking
# --------
#
# By default, data arrays are stored *contiguously*. This means that on disk/in memory the elements of a
# multi-dimensional, such as, ```[[1 2] [3 4]]``` are actually stored in a one-dimensional buffer
# ```1 2 3 4```. Using chunking, allows us to break up our array into chunks so that our array will be
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
wrapped_data = H5DataIO(data=data,
                        chunks=True,          # <---- Enable chunking
                        maxshape=(None, 10)   # <---- Make the time dimension unlimited and hence resizeable
                        )
test_ts = TimeSeries(name='test_chunked_timeseries',
                     data=wrapped_data,                  # <----
                     unit='SIunit',
                     starting_time=0.0,
                     rate=10.0)
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
#    read/write operations. The following blog post provides an example
#    `http://geology.beer/2015/02/10/hdf-for-large-arrays/ <http://geology.beer/2015/02/10/hdf-for-large-arrays/>`__.
#    for this. But you should also know that, with great power comes great responsibility! I.e., if you choose a
#    bad chunk size e.g., too small chunks that don't align with our read/write operations, then chunking can
#    also harm I/O performance.

####################
# Compression and Other I/O Filters
# -----------------------------------
#
# HDF5 supports I/O filters, i.e, data transformation (e.g, compression) that are applied transparently on
# read/write operations.  I/O filters operate on a per-chunk basis in HDF5 and as such require the use of chunking.
# Chunking will be automatically enabled by h5py when compression and other I/O filters are enabled.
#
# To use compression, we can wrap our dataset using :py:class:`~hdmf.backends.hdf5.h5_utils.H5DataIO` and
# define the approbriate opions:

wrapped_data = H5DataIO(data=data,
                        compression='gzip',              # <---- Use GZip
                        compression_opts=4,              # <---- Optional GZip aggression option
                        )
test_ts = TimeSeries(name='test_gzipped_timeseries',
                     data=wrapped_data,                  # <----
                     unit='SIunit',
                     starting_time=0.0,
                     rate=10.0)
nwbfile.add_acquisition(test_ts)

####################
# .. hint::
#
#   In addition to ``compression``, :py:class:`~hdmf.backends.hdf5.h5_utils.H5DataIO` also allows us to
#   enable the ``shuffle`` and ``fletcher32`` HDF5 I/O filters.

####################
# .. note::
#
#    *h5py* (and *HDF5* more broadly) support a number of different compression
#    algorithms, e.g., *GZIP*, *SZIP*, or *LZF* (or even custom compression filters).
#    However, only *GZIP* is built by default with HDF5, i.e., while data compressed
#    with *GZIP* can be read on all platforms and installation of HDF5, other
#    compressors may not be installed everywhere so that not all users may
#    be able to access those files.
#


####################
# Writing the data
# ----------------
#
#
# Writing the data now works as usual.

from pynwb import NWBHDF5IO

io = NWBHDF5IO('advanced_io_example.nwb', 'w')
io.write(nwbfile)
io.close()

####################
# Reading the data
# ----------------
#
#
# Again, nothing has changed for read. All of the above advanced I/O features are handled transparently.

io = NWBHDF5IO('advanced_io_example.nwb', 'r')
nwbfile = io.read()

####################
# Now lets have a look to confirm that all our I/O settings where indeed used.

for k, v in nwbfile.acquisition.items():
    print("name=%s, chunks=%s, compression=%s, maxshape=%s" % (k,
                                                               v.data.chunks,
                                                               v.data.compression,
                                                               v.data.maxshape))

####################
#
# .. code-block:: python
#
#   name=test_regular_timeseries, chunks=None, compression=None, maxshape=(10,)
#   name=test_compressed_timeseries, chunks=(10,), compression=gzip, maxshape=(10,)
#   name=test_chunked_timeseries, chunks=(250, 5), compression=None, maxshape=(None, 10)
#   name=test_gzipped_timeseries, chunks=(250, 5), compression=gzip, maxshape=(1000, 10)
#
# As we can see, the datasets have been chunked and compressed correctly. Alos, as expected, chunking
# was automatically enabled for the compressed datasets.


####################
# Wrapping ``h5py.Datasets`` with :py:class:`~hdmf.backends.hdf5.h5_utils.H5DataIO`
# ---------------------------------------------------------------------------------
#
# Just for completeness, :py:class:`~hdmf.backends.hdf5.h5_utils.H5DataIO` also allows us to customize
# how ``h5py.Dataset`` objects should be handled on write by the PyNWBs HDF5 backend via the ``link_data``
# parameter. If ``link_data`` is set to ``True`` then a ``SoftLink`` or ``ExternalLink`` will be created to
# point to the HDF5 dataset On the other hand, if ``link_data`` is set to ``False`` then the dataset
# be copied using `h5py.Group.copy <http://docs.h5py.org/en/latest/high/group.html#Group.copy>`__
# **without copying attributes** and **without expanding soft links, external links, or references**.
#
# .. note::
#
#   When wrapping an ``h5py.Dataset`` object using H5DataIO, then  all settings except ``link_data``
#   will be ignored as the h5py.Dataset will either be linked to or copied as on write.
#

####################
# Parallel I/O using MPI
# ----------------------
#
# The HDF5 storage backend supports parallel I/O using the Message Passing Interface (MPI).
# Using this feature requires that you install ``hdf5`` and ``h5py`` against an MPI driver, and you
# install ``mpi4py``. The basic installation of pynwb will not work. Setup can be tricky, and
# is outside the scope of this tutorial (for now), and the following assumes that you have
# HDF5 installed in a MPI configuration. Here we:
#
# 1. **Instantiate a dataset for parallel write**: We create TimeSeries with 4 timestamps that we
# will write in parallel
#
# 2. **Write to that file in parallel using MPI**: Here we assume 4 MPI ranks while each rank writes
# the data for a different timestamp.
#
# 3. **Read from the file in parallel using MPI**: Here each of the 4 MPI ranks reads one time
# step from the file
#
# .. code-block:: python
#
#   from mpi4py import MPI
#   import numpy as np
#   from dateutil import tz
#   from pynwb import NWBHDF5IO, NWBFile, TimeSeries
#   from datetime import datetime
#   from hdmf.data_utils import DataChunkIterator
#
#   start_time = datetime(2018, 4, 25, 2, 30, 3, tzinfo=tz.gettz('US/Pacific'))
#   fname = 'test_parallel_pynwb.nwb'
#   rank = MPI.COMM_WORLD.rank  # The process ID (integer 0-3 for 4-process run)
#
#   # Create file on one rank. Here we only instantiate the dataset we want to
#   # write in parallel but we do not write any data
#   if rank == 0:
#       nwbfile = NWBFile('aa', 'aa', start_time)
#       data = DataChunkIterator(data=None, maxshape=(4,), dtype=np.dtype('int'))
#
#       nwbfile.add_acquisition(TimeSeries('ts_name', description='desc', data=data,
#                                          rate=100., unit='m'))
#       with NWBHDF5IO(fname, 'w') as io:
#           io.write(nwbfile)
#
#   # write to dataset in parallel
#   with NWBHDF5IO(fname, 'a', comm=MPI.COMM_WORLD) as io:
#       nwbfile = io.read()
#       print(rank)
#       nwbfile.acquisition['ts_name'].data[rank] = rank
#
#   # read from dataset in parallel
#   with NWBHDF5IO(fname, 'r', comm=MPI.COMM_WORLD) as io:
#       print(io.read().acquisition['ts_name'].data[rank])

####################
# To specify details about chunking, compression and other HDF5-specific I/O options,
# we can wrap data via ``H5DataIO``, e.g,
#
# .. code-block:: python
#
#   data = H5DataIO(DataChunkIterator(data=None, maxshape=(100000, 100),
#                                     dtype=np.dtype('float')),
#                                     chunks=(10, 10), maxshape=(None, None))
#
# would initialize your dataset with a shape of (100000, 100) and maxshape of (None, None)
# and your own custom chunking of (10, 10).

####################
# Disclaimer
# ----------------
#
# External links included in the tutorial are being provided as a convenience and for informational purposes only;
# they do not constitute an endorsement or an approval by the authors of any of the products, services or opinions of
# the corporation or organization or individual. The authors bear no responsibility for the accuracy, legality or
# content of the external site or for that of subsequent links. Contact the external site for answers to questions
# regarding its content.
