'''
.. _streaming:

Streaming NWB files
===================

You can read specific sections within individual data files directly from remote stores such as the
`DANDI Archive <https://dandiarchive.org/>`_. This is especially useful for reading small pieces of data
from a large NWB file stored
remotely. First, you will need to get the location of the file. The code below illustrates how to do this on DANDI
using the dandi API library.

Getting the location of the file on DANDI
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The :py:class:`~dandi.dandiapi.DandiAPIClient` can be used to get the S3 URL of any NWB file stored in the DANDI
Archive. If you have not already, install the latest release of the ``dandi`` package.


.. code-block:: bash

   pip install dandi

Now you can get the url of a particular NWB file using the dandiset ID and the path of that file within the dandiset.

.. code-block:: python

   from dandi.dandiapi import DandiAPIClient

   dandiset_id = '000006'  # ephys dataset from the Svoboda Lab
   filepath = 'sub-anm372795/sub-anm372795_ses-20170718.nwb'  # 450 kB file
   with DandiAPIClient() as client:
       asset = client.get_dandiset(dandiset_id, 'draft').get_asset_by_path(filepath)
       s3_url = asset.get_content_url(follow_redirects=1, strip_query=True)


Streaming Method 1: ROS3
~~~~~~~~~~~~~~~~~~~~~~~~
ROS3 is one of the supported methods for reading data from a remote store. ROS3 stands for "read only S3" and is a
driver created by the HDF5 Group that allows HDF5 to read HDF5 files stored remotely in s3 buckets. Using this method
requires that your HDF5 library is installed with the ROS3 driver enabled. This is not the default configuration,
so you will need to make sure you install the right version of ``h5py`` that has this advanced configuration enabled.
You can install HDF5 with the ROS3 driver from `conda-forge <https://conda-forge.org/>`_ using ``conda``. You may
first need to uninstall a currently installed version of ``h5py``.

.. code-block:: bash

   pip uninstall h5py
   conda install -c conda-forge "h5py>=3.2"

Now instantiate a :py:class:`~pynwb.NWBHDF5IO` object with the S3 URL and specify the driver as "ros3". This
will download metadata about the file from the S3 bucket to memory. The values of datasets are accessed lazily,
just like when reading an NWB file stored locally. So, slicing into a dataset will require additional time to
download the sliced data (and only the sliced data) to memory.

.. code-block:: python

   from pynwb import NWBHDF5IO

   with NWBHDF5IO(s3_url, mode='r', load_namespaces=True, driver='ros3') as io:
       nwbfile = io.read()
       print(nwbfile)
       print(nwbfile.acquisition['lick_times'].time_series['lick_left_times'].data[:])

Streaming Method 2: fsspec
~~~~~~~~~~~~~~~~~~~~~~~~~~~
fsspec is another data streaming approach that is quite flexible and has several performance advantages. This library
creates a virtual filesystem for remote stores. With this approach, a virtual file is created for the file and
the virtual filesystem layer takes care of requesting data from the S3 bucket whenever data is
read from the virtual file.  Note that this implementation is completely unaware of internals of the HDF5 format
and thus can work for **any** file, not only for the purpose of use with H5PY and PyNWB.

First install ``fsspec`` and the dependencies of the :py:class:`~fsspec.implementations.http.HTTPFileSystem`:

.. code-block:: bash

   pip install fsspec requests aiohttp

Then in Python:

.. code-block:: python

    import fsspec
    import pynwb
    import h5py
    from fsspec.implementations.cached import CachingFileSystem

    # first, create a virtual filesystem based on the http protocol and use
    # caching to save accessed data to RAM.
    fs = CachingFileSystem(
        fs=fsspec.filesystem("http"),
        cache_storage="nwb-cache",  # Local folder for the cache
    )

    # next, open the file
    with fs.open(s3_url, "rb") as f:
        with h5py.File(f) as file:
            with pynwb.NWBHDF5IO(file=file, load_namespaces=True) as io:
                nwbfile = io.read()
                print(nwbfile.acquisition['lick_times'].time_series['lick_left_times'].data[:])


fsspec is a library that can be used to access a variety of different store formats, including (at the time of
writing):

.. code-block:: python

    from fsspec.registry import known_implementations
    known_implementations.keys()

file, memory, dropbox, http, https, zip, tar, gcs, gs, gdrive, sftp, ssh, ftp, hdfs, arrow_hdfs, webhdfs, s3, s3a, wandb, oci, adl, abfs, az, cached, blockcache, filecache, simplecache, dask, dbfs, github, git, smb, jupyter, jlab, libarchive, reference

The S3 backend, in particular, may provide additional functionality for accessing data on DANDI. See the
`fsspec documentation on known implementations <https://filesystem-spec.readthedocs.io/en/latest/api.html?highlight=S3#other-known-implementations>`_
for a full updated list of supported store formats.
'''

# sphinx_gallery_thumbnail_path = 'figures/gallery_thumbnails_streaming.png'
