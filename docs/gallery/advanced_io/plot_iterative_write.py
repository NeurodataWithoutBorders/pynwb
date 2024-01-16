"""
Iterative Data Write
====================

This example demonstrate how to iteratively write data arrays with applications to
writing large arrays without loading all data into memory and streaming data write.

"""

####################
# Introduction
# ------------


####################
# What is Iterative Data Write?
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# In the typical write process, datasets are created and written as a whole. In contrast,
# iterative data write refers to the writing of the contents of a dataset in an incremental,
# iterative fashion.

####################
# Why Iterative Data Write?
# ^^^^^^^^^^^^^^^^^^^^^^^^^
#
# The possible applications for iterative data write are broad. Here we list a few typical applications
# for iterative data write in practice.
#
# * **Large data arrays** A central challenge when dealing with large data arrays is that it is often
#   not feasible to load all of the data into memory. Using an iterative data write process allows us
#   to avoid this problem by writing the data one-subblock-at-a-time, so that we only need to hold
#   a small subset of the array in memory at any given time.
# * **Data streaming** In the context of streaming data we are faced with several issues:
#   **1)** data is not available in-memory but arrives in subblocks as the stream progresses
#   **2)** caching the data of a stream in-memory is often prohibitively expensive and volatile
#   **3)** the total size of the data is often unknown ahead of time.
#   Iterative data write allows us to address issues 1) and 2) by enabling us to save data to a
#   file incrementally as it arrives from the data stream. Issue 3) is addressed in the HDF5
#   storage backend via support for chunking, enabling the creation of resizable arrays.
#
#   * **Data generators** Data generators are in many ways similar to data streams only that the
#     data is typically being generated locally and programmatically rather than from an external
#     data source.
#
# * **Sparse data arrays** In order to reduce storage size of sparse arrays a challenge is that while
#   the data array (e.g., a matrix) may be large, only a few values are set. To avoid storage overhead
#   for storing the full array we can employ (in HDF5) a combination of chunking, compression, and
#   and iterative data write to significantly reduce storage cost for sparse data.
#

####################
# Iterating Over Data Arrays
# ^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# In PyNWB the process of iterating over large data arrays is implemented via the concept of
# :py:class:`~hdmf.data_utils.DataChunk` and :py:class:`~hdmf.data_utils.AbstractDataChunkIterator`.
#
# * :py:class:`~hdmf.data_utils.DataChunk` is a simple data structure used to describe
#   a subset of a larger data array (i.e., a data chunk), consisting of:
#
#   * ``DataChunk.data`` : the array with the data value(s) of the chunk and
#   * ``DataChunk.selection`` : the NumPy index tuple describing the location of the chunk in the whole array.
#
# * :py:class:`~hdmf.data_utils.AbstractDataChunkIterator` then defines a class for iterating over large
#   data arrays one-:py:class:`~hdmf.data_utils.DataChunk`-at-a-time.
#
# * :py:class:`~hdmf.data_utils.DataChunkIterator` is a specific implementation of an
#   :py:class:`~hdmf.data_utils.AbstractDataChunkIterator` that accepts any iterable and assumes
#   that we iterate over the first dimension of the data array. :py:class:`~hdmf.data_utils.DataChunkIterator`
#   also supports buffered read, i.e., multiple values from the input iterator can be combined to a single chunk.
#   This is useful for buffered I/O operations, e.g., to improve performance by accumulating data in memory and
#   writing larger blocks at once.
#
# * :py:class:`~hdmf.data_utils.GenericDataChunkIterator` is a semi-abstract version of a
#   :py:class:`~hdmf.data_utils.AbstractDataChunkIterator` that automatically handles the selection of
#   buffer regions and resolves communication of compatible chunk regions. Users specify chunk
#   and buffer shapes or sizes and the iterator will manage how to break the data up for write.
#   For further details, see the
#   :hdmf-docs:`GenericDataChunkIterator tutorial <tutorials/plot_generic_data_chunk_tutorial.html>`.
#

####################
# Iterative Data Write: API
# ^^^^^^^^^^^^^^^^^^^^^^^^^
#
# On the front end, all a user needs to do is to create or wrap their data in a
# :py:class:`~hdmf.data_utils.AbstractDataChunkIterator`. The I/O backend (e.g.,
# :py:class:`~hdmf.backends.hdf5.h5tools.HDF5IO` or :py:class:`~pynwb.NWBHDF5IO`) then
# implements the iterative processing of the data chunk iterators. PyNWB also provides with
# :py:class:`~hdmf.data_utils.DataChunkIterator` a specific implementation of a data chunk iterator
# which we can use to wrap common iterable types (e.g., generators, lists, or numpy arrays).
# For more advanced use cases we then need to implement our own derived class of
# :py:class:`~hdmf.data_utils.AbstractDataChunkIterator`.
#
# .. tip::
#
#    Currently the HDF5 I/O backend of PyNWB (:py:class:`~hdmf.backends.hdf5.h5tools.HDF5IO`,
#    :py:class:`~pynwb.NWBHDF5IO`) processes iterative data writes one-dataset-at-a-time. This means, that
#    while you may have an arbitrary number of iterative data writes, the write is performed in order.
#    In the future we may use a queuing process to enable the simultaneous processing of multiple iterative writes at
#    the same time.
#
# Preparations:
# ^^^^^^^^^^^^^
#
# The data write in our examples really does not change. We, therefore, here create a
# simple helper function first to write a simple NWBFile containing a single timeseries to
# avoid repetition of the same code and to allow us to focus on the important parts of this tutorial.

# sphinx_gallery_thumbnail_path = 'figures/gallery_thumbnails_iterative_write.png'
from datetime import datetime
from uuid import uuid4

from dateutil.tz import tzlocal

from pynwb import NWBHDF5IO, NWBFile, TimeSeries


def write_test_file(filename, data, close_io=True):
    """

    Simple helper function to write an NWBFile with a single timeseries containing data
    :param filename: String with the name of the output file
    :param data: The data of the timeseries
    :param close_io: Close and destroy the NWBHDF5IO object used for writing (default=True)

    :returns: None if close_io==True otherwise return NWBHDF5IO object used for write
    """

    # Create a test NWBfile
    start_time = datetime(2017, 4, 3, 11, tzinfo=tzlocal())
    nwbfile = NWBFile(
        session_description="demonstrate iterative write",
        identifier=str(uuid4()),
        session_start_time=start_time,
    )

    # Create our time series
    test_ts = TimeSeries(
        name="synthetic_timeseries",
        data=data,
        unit="n/a",
        rate=1.0,
    )
    nwbfile.add_acquisition(test_ts)

    # Write the data to file
    io = NWBHDF5IO(filename, "w")
    io.write(nwbfile)
    if close_io:
        io.close()
        del io
        io = None
    return io


####################
# Example: Write Data from Generators and Streams
# -----------------------------------------------
#
# Here we use a simple data generator but PyNWB does not make any assumptions about what happens
# inside the generator. Instead of creating data programmatically, you may hence, e.g., receive
# data from an acquisition system (or other source). We can use the same approach to write streaming data.

####################
# Step 1: Define the data generator
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
from math import pi, sin
from random import random

import numpy as np


def iter_sin(chunk_length=10, max_chunks=100):
    """
    Generator creating a random number of chunks (but at most max_chunks) of length chunk_length containing
    random samples of sin([0, 2pi]).
    """
    x = 0
    num_chunks = 0
    while x < 0.5 and num_chunks < max_chunks:
        val = np.asarray([sin(random() * 2 * pi) for i in range(chunk_length)])
        x = random()
        num_chunks += 1
        yield val
    return


####################
# Step 2: Wrap the generator in a DataChunkIterator
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#

from hdmf.data_utils import DataChunkIterator

data = DataChunkIterator(data=iter_sin(10))

####################
# Step 3: Write the data as usual
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# Here we use our wrapped generator to create the data for a synthetic time series.

write_test_file(filename="basic_iterwrite_example.nwb", data=data)

####################
# Discussion
# ^^^^^^^^^^
# Note, here we don't actually know how long our timeseries will be.

print(
    "maxshape=%s, recommended_data_shape=%s, dtype=%s"
    % (str(data.maxshape), str(data.recommended_data_shape()), str(data.dtype))
)

####################
# As we can see :py:class:`~hdmf.data_utils.DataChunkIterator` automatically recommends
# in its ``maxshape`` that the first dimensions of our array should be unlimited (``None``) and the second
# dimension should be ``10`` (i.e., the length of our chunk. Since :py:class:`~hdmf.data_utils.DataChunkIterator`
# has no way of knowing the minimum size of the array it automatically recommends the size of the first
# chunk as the minimum size (i.e, ``(1, 10)``) and also infers the data type automatically from the first chunk.
# To further customize this behavior we may also define the ``maxshape``, ``dtype``, and ``buffer_size`` when
# we create the :py:class:`~hdmf.data_utils.DataChunkIterator`.
#
# .. tip::
#
#    We here used :py:class:`~hdmf.data_utils.DataChunkIterator` to conveniently wrap our data stream.
#    :py:class:`~hdmf.data_utils.DataChunkIterator` assumes that our generator yields in **consecutive order**
#    a **single** complete element along the **first dimension** of our array (i.e., iterate over the first
#    axis and yield one-element-at-a-time). This behavior is useful in many practical cases. However, if
#    this strategy does not match our needs, then using :py:class:`~hdmf.data_utils.GenericDataChunkIterator`
#    or implementing your own derived :py:class:`~hdmf.data_utils.AbstractDataChunkIterator` may be more
#    appropriate. We show an example of how to implement your own :py:class:`~hdmf.data_utils.AbstractDataChunkIterator`
#    next. See the :hdmf-docs:`GenericDataChunkIterator tutorial <tutorials/plot_generic_data_chunk_tutorial.html>` as
#    part of the HDMF documentation for details on how to use :py:class:`~hdmf.data_utils.GenericDataChunkIterator`.
#


####################
# Example: Optimizing Sparse Data Array I/O and Storage
# -----------------------------------------------------
#
# Step 1: Create a data chunk iterator for our sparse matrix
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

from hdmf.data_utils import AbstractDataChunkIterator, DataChunk


class SparseMatrixIterator(AbstractDataChunkIterator):
    def __init__(self, shape, num_chunks, chunk_shape):
        """
        :param shape: 2D tuple with the shape of the matrix
        :param num_chunks: Number of data chunks to be created
        :param chunk_shape: The shape of each chunk to be created
        :return:
        """
        self.shape, self.num_chunks, self.chunk_shape = shape, num_chunks, chunk_shape
        self.__chunks_created = 0

    def __iter__(self):
        return self

    def __next__(self):
        """
        Return in each iteration a fully occupied data chunk of self.chunk_shape values at a random
        location within the matrix. Chunks are non-overlapping. REMEMBER: h5py does not support all
        the fancy indexing that numpy does so we need to make sure our selection can be
        handled by the backend.
        """
        if self.__chunks_created < self.num_chunks:
            data = np.random.rand(np.prod(self.chunk_shape)).reshape(self.chunk_shape)
            xmin = (
                np.random.randint(0, int(self.shape[0] / self.chunk_shape[0]), 1)[0]
                * self.chunk_shape[0]
            )
            xmax = xmin + self.chunk_shape[0]
            ymin = (
                np.random.randint(0, int(self.shape[1] / self.chunk_shape[1]), 1)[0]
                * self.chunk_shape[1]
            )
            ymax = ymin + self.chunk_shape[1]
            self.__chunks_created += 1
            return DataChunk(data=data, selection=np.s_[xmin:xmax, ymin:ymax])
        else:
            raise StopIteration

    next = __next__

    def recommended_chunk_shape(self):
        # Here we can optionally recommend what a good chunking could be.
        return self.chunk_shape

    def recommended_data_shape(self):
        # We know the full size of the array. In cases where we don't know the full size
        # this should be the minimum size.
        return self.shape

    @property
    def dtype(self):
        # The data type of our array
        return np.dtype(float)

    @property
    def maxshape(self):
        # We know the full shape of the array. If we don't know the size of a dimension
        # beforehand we can set the dimension to None instead
        return self.shape


#####################
# Step 2: Instantiate our sparse matrix
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#

# Setting for our random sparse matrix
xsize = 1000000
ysize = 1000000
num_chunks = 1000
chunk_shape = (10, 10)
num_values = num_chunks * np.prod(chunk_shape)

# Create our sparse matrix data.
data = SparseMatrixIterator(
    shape=(xsize, ysize), num_chunks=num_chunks, chunk_shape=chunk_shape
)

#####################
# In order to also enable compression and other advanced HDF5 dataset I/O features we can then also
# wrap our data via :py:class:`~hdmf.backends.hdf5.h5_utils.H5DataIO`.
from hdmf.backends.hdf5.h5_utils import H5DataIO

matrix2 = SparseMatrixIterator(
    shape=(xsize, ysize), num_chunks=num_chunks, chunk_shape=chunk_shape
)
data2 = H5DataIO(data=matrix2, compression="gzip", compression_opts=4)

######################
# We can now also customize the chunking, fill value, and other settings
#
from hdmf.backends.hdf5.h5_utils import H5DataIO

# Increase the chunk size and add compression
matrix3 = SparseMatrixIterator(
    shape=(xsize, ysize), num_chunks=num_chunks, chunk_shape=chunk_shape
)
data3 = H5DataIO(data=matrix3, chunks=(100, 100), fillvalue=np.nan)

# Increase the chunk size and add compression
matrix4 = SparseMatrixIterator(
    shape=(xsize, ysize), num_chunks=num_chunks, chunk_shape=chunk_shape
)
data4 = H5DataIO(
    data=matrix4,
    compression="gzip",
    compression_opts=4,
    chunks=(100, 100),
    fillvalue=np.nan,
)

####################
# Step 3: Write the data as usual
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# Here we simply use our ``SparseMatrixIterator`` as input for our ``TimeSeries``

write_test_file(filename="basic_sparse_iterwrite_example.nwb", data=data)
write_test_file(filename="basic_sparse_iterwrite_compressed_example.nwb", data=data2)
write_test_file(filename="basic_sparse_iterwrite_largechunks_example.nwb", data=data3)
write_test_file(
    filename="basic_sparse_iterwrite_largechunks_compressed_example.nwb", data=data4
)

####################
# Check the results
# ^^^^^^^^^^^^^^^^^
#
# Now lets check out the size of our data file and compare it against the expected full size of our matrix
import os

expected_size = xsize * ysize * 8  # This is the full size of our matrix in bytes
occupied_size = num_values * 8  # Number of non-zero values in out matrix
file_size = os.stat(
    "basic_sparse_iterwrite_example.nwb"
).st_size  # Real size of the file
file_size_compressed = os.stat("basic_sparse_iterwrite_compressed_example.nwb").st_size
file_size_largechunks = os.stat(
    "basic_sparse_iterwrite_largechunks_example.nwb"
).st_size
file_size_largechunks_compressed = os.stat(
    "basic_sparse_iterwrite_largechunks_compressed_example.nwb"
).st_size
mbfactor = 1000.0 * 1000  # Factor used to convert to MegaBytes

print("1) Sparse Matrix Size:")
print("   Expected Size :  %.2f MB" % (expected_size / mbfactor))
print("   Occupied Size :  %.5f MB" % (occupied_size / mbfactor))
print("2) NWB HDF5 file (no compression):")
print("   File Size     :  %.2f MB" % (file_size / mbfactor))
print("   Reduction     :  %.2f x" % (expected_size / file_size))
print("3) NWB HDF5 file (with GZIP compression):")
print("   File Size     :  %.5f MB" % (file_size_compressed / mbfactor))
print("   Reduction     :  %.2f x" % (expected_size / file_size_compressed))
print("4) NWB HDF5 file (large chunks):")
print("   File Size     :  %.5f MB" % (file_size_largechunks / mbfactor))
print("   Reduction     :  %.2f x" % (expected_size / file_size_largechunks))
print("5) NWB HDF5 file (large chunks with compression):")
print("   File Size     :  %.5f MB" % (file_size_largechunks_compressed / mbfactor))
print("   Reduction     :  %.2f x" % (expected_size / file_size_largechunks_compressed))

####################
# Discussion
# ^^^^^^^^^^
#
# * **1) vs 2):** While the full matrix would have a size of ``8TB`` the HDF5 file is only ``0.88MB``. This is roughly
#   the same as the real occupied size of ``0.8MB``. When using chunking, HDF5 does not allocate the full dataset but
#   only allocates chunks that actually contain data. In (2) the size of our chunks align perfectly with the
#   occupied chunks of our sparse matrix, hence, only the minimal amount of storage needs to be allocated.
#   A slight overhead (here 0.08MB) is expected because our file contains also the additional objects from
#   the NWBFile, plus some overhead for managing all the HDF5 metadata for all objects.
# * **3) vs 2):**  Adding compression does not yield any improvement here. This is expected, because, again we
#   selected the chunking here in a way that we already allocated the minimum amount of storage to represent our data
#   and lossless compression of random data is not efficient.
# * **4) vs 2):** When we increase our chunk size to ``(100,100)`` (i.e., ``100x`` larger than the chunks produced by
#   our matrix generator) we observe an accordingly roughly ``100x`` increase in file size. This is expected
#   since our chunks now do not align perfectly with the occupied data and each occupied chunk is allocated fully.
# * **5) vs 4):** When using compression for the larger chunks we see a significant reduction
#   in file size (``1.14MB`` vs. ``80MB``). This is because the allocated chunks now contain in addition to the random
#   values large areas of constant fill values, which compress easily.
#
# **Advantages:**
#
# * We only need to hold one :py:class:`~hdmf.data_utils.DataChunk` in memory at any given time
# * Only the data chunks in the HDF5 file that contain non-default values are ever being allocated
# * The overall size of our file is reduced significantly
# * Reduced I/O load
# * On read, users can use the array as usual
#
# .. tip::
#
#    With great power comes great responsibility **!** I/O and storage cost will depend, among other factors,
#    on the chunk size, compression options, and the write pattern, i.e., the number and structure of the
#    :py:class:`~hdmf.data_utils.DataChunk` objects written. For example, using ``(1,1)`` chunks and writing them
#    one value at a time would result in poor I/O performance in most practical cases, because of the large number of
#    chunks and large number of small I/O operations required.
#
# .. tip::
#
#    A word of caution, while this approach helps optimize storage, the in-memory representation on read is
#    still a dense numpy array. This behavior is convenient for many user interactions with the data but
#    can be problematic with regard to performance/memory when accessing large data subsets.
#
#   .. code-block:: python
#
#       io = NWBHDF5IO('basic_sparse_iterwrite_example.nwb', 'r')
#       nwbfile = io.read()
#       data = nwbfile.get_acquisition('synthetic_timeseries').data  # <-- PyNWB does lazy load; no problem
#       subset = data[10:100, 10:100]                                # <-- Loading a subset is fine too
#       alldata = data[:]            # <-- !!!! This would load the complete (1000000 x 1000000) array !!!!
#
# .. tip::
#
#    As we have seen here, our data chunk iterator may produce chunks in arbitrary order and locations within the
#    array. In the case of the HDF5 I/O backend we need to take care that the selection we yield can be understood
#    by h5py.

####################
# Example: Convert large binary data arrays
# -----------------------------------------
#
# When converting large data files, a typical problem is that it is often too expensive to load all the data
# into memory. This example is very similar to the data generator example only that instead of generating
# data on-the-fly in-memory we are loading data from a file one-chunk-at-a-time in our generator.
#

####################
# Create example data
# ^^^^^^^^^^^^^^^^^^^

import numpy as np

# Create the test data
datashape = (100, 10)  # This is not really large, but we just want to show how it works
num_values = np.prod(datashape)
arrdata = np.arange(num_values).reshape(datashape)
# Write the test data to disk
temp = np.memmap(
    "basic_sparse_iterwrite_testdata.npy", dtype="float64", mode="w+", shape=datashape
)
temp[:] = arrdata
del temp  # Flush to disk

####################
# Step 1: Create a generator for our array
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# Note, we here use a generator for simplicity but we could equally well also implement our own
# :py:class:`~hdmf.data_utils.AbstractDataChunkIterator` or use :py:class:`~hdmf.data_utils.GenericDataChunkIterator`.


def iter_largearray(filename, shape, dtype="float64"):
    """
    Generator reading [chunk_size, :] elements from our array in each iteration.
    """
    for i in range(shape[0]):
        # Open the file and read the next chunk
        newfp = np.memmap(filename, dtype=dtype, mode="r", shape=shape)
        curr_data = newfp[i : (i + 1), ...][0]
        del newfp  # Reopen the file in each iterator to prevent accumulation of data in memory
        yield curr_data
    return


####################
# Step 2: Wrap the generator in a DataChunkIterator
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#

from hdmf.data_utils import DataChunkIterator

data = DataChunkIterator(
    data=iter_largearray(
        filename="basic_sparse_iterwrite_testdata.npy", shape=datashape
    ),
    maxshape=datashape,
    buffer_size=10,
)  # Buffer 10 elements into a chunk, i.e., create chunks of shape (10,10)


####################
# Step 3: Write the data as usual
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#

write_test_file(filename="basic_sparse_iterwrite_largearray.nwb", data=data)

####################
# .. tip::
#
#       Again, if we want to explicitly control how our data will be chunked (compressed etc.)
#       in the HDF5 file then we need to wrap our :py:class:`~hdmf.data_utils.DataChunkIterator`
#       using :py:class:`~hdmf.backends.hdf5.h5_utils.H5DataIO`

####################
# Discussion
# ^^^^^^^^^^
# Let's verify that our data was written correctly

# Read the NWB file
from pynwb import NWBHDF5IO  # noqa: F811

with NWBHDF5IO("basic_sparse_iterwrite_largearray.nwb", "r") as io:
    nwbfile = io.read()
    data = nwbfile.get_acquisition("synthetic_timeseries").data
    # Compare all the data values of our two arrays
    data_match = np.all(arrdata == data[:])  # Don't do this for very large arrays!
    # Print result message
    if data_match:
        print("Success: All data values match")
    else:
        print("ERROR: Mismatch between data")

####################
# Example: Convert arrays stored in multiple files
# ------------------------------------------------
#
# In practice, data from recording devices may be distributed across many files, e.g., one file per time range
# or one file per recording channel. Using iterative data write provides an elegant solution to this problem
# as it allows us to process large arrays one-subarray-at-a-time. To make things more interesting we'll show
# this for the case where each recording channel (i.e., the second dimension of our ``TimeSeries``) is broken up
# across files.

####################
# Create example data
# ^^^^^^^^^^^^^^^^^^^

import numpy as np

# Create the test data
num_channels = 10
num_steps = 100
channel_files = [
    "basic_sparse_iterwrite_testdata_channel_%i.npy" % i for i in range(num_channels)
]
for f in channel_files:
    temp = np.memmap(f, dtype="float64", mode="w+", shape=(num_steps,))
    temp[:] = np.arange(num_steps, dtype="float64")
    del temp  # Flush to disk

#####################
# Step 1: Create a data chunk iterator for our multifile array
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

from hdmf.data_utils import AbstractDataChunkIterator, DataChunk  # noqa: F811


class MultiFileArrayIterator(AbstractDataChunkIterator):
    def __init__(self, channel_files, num_steps):
        """
        :param channel_files: List of files with the channels
        :param num_steps: Number of timesteps per channel
        :return:
        """
        self.shape = (num_steps, len(channel_files))
        self.channel_files = channel_files
        self.num_steps = num_steps
        self.__curr_index = 0

    def __iter__(self):
        return self

    def __next__(self):
        """
        Return in each iteration the data from a single file
        """
        if self.__curr_index < len(channel_files):
            newfp = np.memmap(
                channel_files[self.__curr_index],
                dtype="float64",
                mode="r",
                shape=(self.num_steps,),
            )
            curr_data = newfp[:]
            i = self.__curr_index
            self.__curr_index += 1
            del newfp
            return DataChunk(data=curr_data, selection=np.s_[:, i])
        else:
            raise StopIteration

    next = __next__

    def recommended_chunk_shape(self):
        return None  # Use autochunking

    def recommended_data_shape(self):
        return self.shape

    @property
    def dtype(self):
        return np.dtype("float64")

    @property
    def maxshape(self):
        return self.shape


#####################
# Step 2: Instantiate our multi file iterator
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#

data = MultiFileArrayIterator(channel_files, num_steps)

####################
# Step 3: Write the data as usual
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#

write_test_file(filename="basic_sparse_iterwrite_multifile.nwb", data=data)

####################
# Discussion
# ^^^^^^^^^^
#
# That's it ;-)
#
# .. tip::
#
#    Common mistakes that will result in errors on write:
#
#    * The size of a :py:class:`~hdmf.data_utils.DataChunk` does not match the selection.
#    * The selection for the :py:class:`~hdmf.data_utils.DataChunk` is not supported by h5py
#      (e.g., unordered lists etc.)
#
#    Other common mistakes:
#
#    * Choosing inappropriate chunk sizes. This typically means bad performance with regard to I/O and/or storage cost.
#    * Using auto chunking without supplying a good recommended_data_shape. h5py auto chunking can only make a good
#      guess of what the chunking should be if it (at least roughly) knows what the shape of the array will be.
#    * Trying to wrap a data generator using the default :py:class:`~hdmf.data_utils.DataChunkIterator`
#      when the generator does not comply with the assumptions of the default implementation (i.e., yield
#      individual, complete elements along the first dimension of the array one-at-a-time). Depending on the generator,
#      this may or may not result in an error on write, but the array you are generating will probably end up
#      at least not having the intended shape.
#    * The shape of the chunks returned by the ``DataChunkIterator`` do not match the shape of the chunks of the
#      target HDF5 dataset. This can result in slow I/O performance, for example, when each chunk of an HDF5 dataset
#      needs to be updated multiple times on write. For example, when using compression this would mean that HDF5
#      may have to read, decompress, update, compress, and write a particular chunk each time it is being updated.
#
#

####################
# Alternative Approach: User-defined dataset write
# ------------------------------------------------
#
# In the above cases we used the built-in capabilities of PyNWB to perform iterative data write. To
# gain more fine-grained control of the write process we can alternatively use PyNWB to setup the full
# structure of our NWB file and then update select datasets afterwards. This approach is useful, e.g.,
# in context of parallel write and any time we need to optimize write patterns.
#
#

####################
# Step 1: Initially allocate the data as empty
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
from hdmf.backends.hdf5.h5_utils import H5DataIO

# Use H5DataIO to specify how to setup the dataset in the file
dataio = H5DataIO(
    shape=(0, 10),  # Initial shape. If the shape is known then set to full shape
    dtype=np.dtype("float"),  # dtype of the dataset
    maxshape=(None, 10),  # Make the time dimension resizable
    chunks=(131072, 2),  # Use 2MB chunks
    compression="gzip",  # Enable GZip compression
    compression_opts=4,  # GZip aggression
    shuffle=True,  # Enable shuffle filter
    fillvalue=np.nan,  # Use NAN as fillvalue
)

# Write a test NWB file with our dataset and keep the NWB file (i.e., the NWBHDF5IO object) open
io = write_test_file(
    filename="basic_alternative_custom_write.nwb", data=dataio, close_io=False
)

####################
# Step 2: Get the dataset(s) to be updated
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#

# Let's check what the data looks like before we write
print(
    "Before write: Shape= %s, Chunks= %s, Maxshape=%s"
    % (
        str(dataio.dataset.shape),
        str(dataio.dataset.chunks),
        str(dataio.dataset.maxshape),
    )
)

# Allocate space. Only needed if we didn't set the initial shape large enough
dataio.dataset.resize((8, 10))

# Write 1s in timesteps 0-2
dataio.dataset[0:3, :] = 1

# Write 2s in timesteps 3-5
# NOTE: timesteps 6 and 7 are not being initialized
dataio.dataset[3:6, :] = 2

# Close the file
io.close()


####################
# Check the results
# ^^^^^^^^^^^^^^^^^

from pynwb import NWBHDF5IO  # noqa

io = NWBHDF5IO("basic_alternative_custom_write.nwb", mode="r")
nwbfile = io.read()
dataset = nwbfile.get_acquisition("synthetic_timeseries").data
print(
    "After write: Shape= %s, Chunks= %s, Maxshape=%s"
    % (str(dataset.shape), str(dataset.chunks), str(dataset.maxshape))
)
print(dataset[:])
io.close()

####################
# We allocated our data to be ``shape=(8, 10)`` but we only wrote data to the first 6 rows of the
# array. As expected, we therefore, see our ``fillvalue`` of ``nan`` in the last two rows of the data.
#
