"""
.. _streaming:

Streaming NWB files
===================

You can read specific sections within individual data files directly from remote stores such as the
`DANDI Archive <https://dandiarchive.org/>`_. This is especially useful for reading small pieces of data
from a large NWB file stored
remotely. First, you will need to get the location of the file. The code below illustrates how to do this on DANDI
using the dandi API library.

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
# Streaming Method 1: fsspec
# --------------------------
# fsspec is another data streaming approach that is quite flexible and has several performance advantages. This library
# creates a virtual filesystem for remote stores. With this approach, a virtual file is created for the file and
# the virtual filesystem layer takes care of requesting data from the S3 bucket whenever data is
# read from the virtual file.  Note that this implementation is completely unaware of internals of the HDF5 format
# and thus can work for **any** file, not only for the purpose of use with H5PY and PyNWB.
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

# next, open the file
with fs.open(s3_url, "rb") as f:
    with h5py.File(f) as file:
        with pynwb.NWBHDF5IO(file=file) as io:
            nwbfile = io.read()
            print(nwbfile.acquisition['lick_times'].time_series['lick_left_times'].data[:])

##################################
# fsspec is a library that can be used to access a variety of different store formats, including (at the time of
# writing):
#
# .. code-block:: python
#
#     from fsspec.registry import known_implementations
#     known_implementations.keys()
#
# file, memory, dropbox, http, https, zip, tar, gcs, gs, gdrive, sftp, ssh, ftp, hdfs, arrow_hdfs, webhdfs, s3, s3a,
# wandb, oci, adl, abfs, az, cached, blockcache, filecache, simplecache, dask, dbfs, github, git, smb, jupyter, jlab,
# libarchive, reference
#
# The S3 backend, in particular, may provide additional functionality for accessing data on DANDI. See the
# `fsspec documentation on known implementations <https://filesystem-spec.readthedocs.io/en/latest/api.html?highlight=S3#other-known-implementations>`_
# for a full updated list of supported store formats.
#
# One downside of this fsspec method is that fsspec is not optimized for reading HDF5 files, and so streaming data
# using this method can be slow. A faster alternative is ``remfile`` described below.
#
# Streaming Method 2: ROS3
# ------------------------
# ROS3 stands for "read only S3" and is a driver created by the HDF5 Group that allows HDF5 to read HDF5 files stored
# remotely in s3 buckets. Using this method requires that your HDF5 library is installed with the ROS3 driver enabled.
# With ROS3 support enabled in h5py, we can instantiate a :py:class:`~pynwb.NWBHDF5IO` object with the S3 URL and
# specify the driver as "ros3".

from pynwb import NWBHDF5IO

with NWBHDF5IO(s3_url, mode='r', driver='ros3') as io:
    nwbfile = io.read()
    print(nwbfile)
    print(nwbfile.acquisition['lick_times'].time_series['lick_left_times'].data[:])

##################################
# This will download metadata about the file from the S3 bucket to memory. The values of datasets are accessed lazily,
# just like when reading an NWB file stored locally. So, slicing into a dataset will require additional time to
# download the sliced data (and only the sliced data) to memory.
#
# .. note::
#
#    Pre-built h5py packages on PyPI do not include this S3 support. If you want this feature, you could use packages
#    from conda-forge, or build h5py from source against an HDF5 build with S3 support. You can install HDF5 with
#    the ROS3 driver from `conda-forge <https://conda-forge.org/>`_ using ``conda``. You may
#    first need to uninstall a currently installed version of ``h5py``.
#
#    .. code-block:: bash
#
#        pip uninstall h5py
#        conda install -c conda-forge "h5py>=3.2"
#
# Besides the extra burden of installing h5py from a non-PyPI source, one downside of this ROS3 method is that
# this method does not support automatic retries in case the connection fails.


##################################################
# Method 3: remfile
# -----------------
# ``remfile`` is another library that enables indexing and streaming of files in s3. remfile is simple and fast,
# especially for the initial load of the nwb file and for accessing small pieces of data. The caveats of ``remfile``
# are that it is a very new project that has not been tested in a variety of use-cases and caching options are
# limited compared to ``fsspec``. `remfile` is a simple, lightweight dependency with a very small codebase.
#
# You can install ``remfile`` with pip:
#
# .. code-block:: bash
#
#   pip install remfile
#

import h5py
from pynwb import NWBHDF5IO
import remfile

rem_file = remfile.File(s3_url)

with h5py.File(rem_file, "r") as h5py_file:
    with NWBHDF5IO(file=h5py_file, load_namespaces=True) as io:
        nwbfile = io.read()
        print(nwbfile.acquisition["lick_times"].time_series["lick_left_times"].data[:])

##################################################
# Which streaming method to choose?
# ---------------------------------
#
# From a user perspective, once opened, the :py:class:`~pynwb.file.NWBFile` works the same with
# fsspec, ros3, or remfile.  However, in general, we currently recommend using fsspec for streaming
# NWB files because it is more performant and reliable than ros3 and more widely tested than remfile.
# However, if you are experiencing long wait times for the initial file load on your network, you
# may want to try remfile.
#
# Advantages of fsspec include:
#
# 1. supports caching, which will dramatically speed up repeated requests for the
#    same region of data,
# 2. automatically retries when s3 fails to return, which helps avoid errors when accessing data due to
#    intermittent errors in connections with S3 (remfile does this as well),
# 3. works also with other storage backends (e.g., GoogleDrive or Dropbox, not just S3) and file formats, and
# 4. in our experience appears to provide faster out-of-the-box performance than the ros3 driver.
