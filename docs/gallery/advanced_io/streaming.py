"""
.. _streaming:

Streaming NWB files
===================

You can read specific sections within individual data files directly from remote stores such as the
`DANDI Archive <https://dandiarchive.org/>`_. This is especially useful for reading small pieces of data
from a large NWB file stored remotely. First, you will need to get the location of the file. The code
below illustrates how to do this on DANDI using the dandi API library.

Getting the location of the file on DANDI
-----------------------------------------

The :py:class:`~dandi.dandiapi.DandiAPIClient` can be used to get the S3 URL of any NWB file stored in the DANDI
Archive. If you have not already, install the latest release of the ``dandi`` package.


.. code-block:: bash

   pip install dandi

Now you can get the url of a particular NWB file using the dandiset ID and the path of that file within the dandiset.

.. note::

   To learn more about the dandi API see the
   `DANDI Python API docs <https://dandi.readthedocs.io/en/stable/modref/index.html>`_

"""

# sphinx_gallery_thumbnail_path = 'figures/gallery_thumbnails_streaming.png'

from dandi.dandiapi import DandiAPIClient

dandiset_id = '000006'  # ephys dataset from the Svoboda Lab
filepath = 'sub-anm372795/sub-anm372795_ses-20170718.nwb'  # 450 kB file
with DandiAPIClient() as client:
    asset = client.get_dandiset(dandiset_id, 'draft').get_asset_by_path(filepath)
    s3_url = asset.get_content_url(follow_redirects=1, strip_query=True)

##############################################
# Once you have an S3 URL, you can use it to read the NWB file directly from the remote store. There are several
# ways to do this, including using the ``remfile`` library, the ``fsspec`` library, or the ROS3 driver in h5py.
#
# Streaming data with ``remfile``
# -------------------------------
# ``remfile`` is a library that enables indexing and streaming of files in s3, optimized for reading HDF5 files.
# remfile is simple and fast, especially for the initial load of the nwb file and for accessing small pieces of data.
# It is a lightweight dependency with a very small codebase. Although ``remfile`` is a very new project that has not
# been tested in a variety of use-cases, but it has worked well in our hands.
# 
# You can install ``remfile`` with pip:
#
# .. code-block:: bash
#
#   pip install remfile
#
# Then in use Python:

import h5py
from pynwb import NWBHDF5IO
import remfile

# Create a disk cache to store downloaded data (optional)
cache_dirname = '/tmp/remfile_cache'
disk_cache = remfile.DiskCache(cache_dirname)

# open the file
rem_file = remfile.File(s3_url, disk_cache=disk_cache)
h5py_file = h5py.File(rem_file, "r")
io = NWBHDF5IO(file=h5py_file)
nwbfile = io.read()

# now you can access the data
streamed_data = nwbfile.acquisition["lick_times"].time_series["lick_left_times"].data[:]

# close the file
io.close()
h5py_file.close()
rem_file.close()

##################################
# You can also use contexts to open the file. This will automatically close the file when the context is exited.
# This approach can be a bit cumbersome when exploring files interactively, but is the preferred approach once 
# the program is finalized because it will ensure that the file is closed properly even if an exception is raised.

rem_file = remfile.File(s3_url, disk_cache=disk_cache)
with h5py.File(rem_file, "r") as h5py_file:
    with NWBHDF5IO(file=h5py_file, load_namespaces=True) as io:
        nwbfile = io.read()
        streamed_data = nwbfile.acquisition["lick_times"].time_series["lick_left_times"].data[:]

# After the contexts end, the file is closed, so you cannot download new data from the file.

#################################
# Streaming data with ``fsspec``
# ------------------------------
# ``fsspec`` is a data streaming approach that is quite flexible. This library creates a virtual filesystem for remote
# stores. With this approach, a virtual file is created for the file and the virtual filesystem layer takes care of
# requesting data from the S3 bucket whenever data is read from the virtual file.  Note that this implementation is
# completely unaware of internals of the HDF5 format and thus can work for **any** file, not only for the purpose of
# use with ``h5py`` and PyNWB. ``fsspec`` can also be used to access data from other storage backends, such as Google
# Drive or Dropbox.
#
# First install ``fsspec`` and the dependencies of the :py:class:`~fsspec.implementations.http.HTTPFileSystem`:
#
# .. code-block:: bash
#
#    pip install fsspec requests aiohttp
#
# Then in Python:

import fsspec
import pynwb
import h5py
from fsspec.implementations.cached import CachingFileSystem

# first, create a virtual filesystem based on the http protocol
fs = fsspec.filesystem("http")

# create a cache to save downloaded data to disk (optional)
fs = CachingFileSystem(
    fs=fs,
    cache_storage="nwb-cache",  # Local folder for the cache
)

# open the file
f = fs.open(s3_url, "rb")
file = h5py.File(f)
io = pynwb.NWBHDF5IO(file=file)
nwbfile = io.read()

# now you can access the data
streamed_data = nwbfile.acquisition['lick_times'].time_series['lick_left_times'].data[:]

# close the file
io.close()
file.close()
f.close()

##################################
# You can also use context managers to open the file. This will automatically close the file when the context is exited.

with fs.open(s3_url, "rb") as f:
    with h5py.File(f) as file:
        with pynwb.NWBHDF5IO(file=file) as io:
            nwbfile = io.read()
            print(nwbfile.acquisition['lick_times'].time_series['lick_left_times'].data[:])

##################################
# fsspec can be used to access a variety of different stores, including (at the time of writing):
#
# .. code-block:: python
#
#     from fsspec.registry import known_implementations
#     known_implementations.keys()
#
# abfs, adl, arrow_hdfs, asynclocal, az, blockcache, box, cached, dask, data, dbfs, dir, dropbox, dvc,
# file, filecache, ftp, gcs, gdrive, generic, git, github, gs, hdfs, hf, http, https, jlab, jupyter,
# lakefs, libarchive, local, memory, oci, ocilake, oss, reference, root, s3, s3a, sftp, simplecache,
# smb, ssh, tar, wandb, webdav, webhdfs, zip
#
# The S3 backend, in particular, may provide additional functionality for accessing data on DANDI. See the
# `fsspec documentation on known implementations 
# <https://filesystem-spec.readthedocs.io/en/latest/api.html?highlight=S3#other-known-implementations>`_
# for a full updated list of supported store formats.
#
# One downside of the fsspec method is that fsspec is not optimized for reading HDF5 files, and so streaming data
# using this method can be slow. ``remfile`` may be a faster alternative.
#
# Streaming data with ROS3
# ------------------------
# ROS3 stands for "read only S3" and is a driver created by the HDF5 Group that allows HDF5 to read HDF5 files stored
# remotely in s3 buckets. Using this method requires that your HDF5 library is installed with the ROS3 driver enabled.
# With ROS3 support enabled in h5py, we can instantiate a :py:class:`~pynwb.NWBHDF5IO` object with the S3 URL and
# specify the driver as "ros3". Like the other methods, you can use a context manager to open the file and close it,
# or open the file and close it manually.

from pynwb import NWBHDF5IO

# open with context manager
with NWBHDF5IO(s3_url, mode='r', driver='ros3') as io:
    nwbfile = io.read()
    streamed_data = nwbfile.acquisition['lick_times'].time_series['lick_left_times'].data[:]

# open and close manually
io = NWBHDF5IO(s3_url, mode='r', driver='ros3')
nwbfile = io.read()
streamed_data = nwbfile.acquisition['lick_times'].time_series['lick_left_times'].data[:]
io.close()

##################################
# This will download metadata about the file from the S3 bucket to memory. The values of datasets are accessed lazily,
# just like when reading an NWB file stored locally. So, slicing into a dataset will download the sliced data (and
# only the sliced data) and load it directly to memory.
#
# .. note::
#
#    Pre-built h5py packages on PyPI do not include this S3 support. If you want this feature, we recommend installing
#    ``h5py`` using conda: 
#
#    .. code-block:: bash
#
#        pip uninstall h5py
#        conda install h5py
#
# Alternatively, you can build h5py from source against an HDF5 build with S3 support, but this is more complicated.
