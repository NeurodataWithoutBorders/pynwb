'''
.. _streaming:

Streaming from an S3 Bucket
===========================

It is possible to read data directly from an S3 bucket, such as data from the `DANDI Archive
<https://dandiarchive.org/>`_. This is especially useful for reading small pieces of data
from a large NWB file stored remotely. In fact, there are two different ways to do this supported by PyNWB.

Method 1: ROS3
~~~~~~~~~~~~~~
ROS3 stands for "read only S3" and is a driver created by the HDF5 group that allows HDF5 to read HDF5 files
stored on s3. Using this method requires that your HDF5 library is installed with the ROS3 driver enabled. This
is not the default configuration, so you will need to make sure you install the right version of h5py that has this
advanced configuration enabled. You can install HDF5 with the ROS3 driver from `conda-forge
<https://conda-forge.org/>`_ using ``conda``. You may first need to uninstall a currently installed version of h5py.

'''

####################
# .. code-block:: bash
#
#   pip uninstall h5py
#   conda install -c conda-forge "h5py>=3.2"
#

####################
# The ``DandiAPIClient`` can be used to get the S3 URL to an NWB file of interest stored in the DANDI Archive.
# If you have not already, install the latest release of the ``dandi`` package.
#
# .. code-block:: bash
#
#   pip install dandi
#
# .. code-block:: python
#
#   from dandi.dandiapi import DandiAPIClient
#
#   dandiset_id = '000006'  # ephys dataset from the Svoboda Lab
#   filepath = 'sub-anm372795/sub-anm372795_ses-20170718.nwb'  # 450 kB file
#   with DandiAPIClient() as client:
#       asset = client.get_dandiset(dandiset_id, 'draft').get_asset_by_path(filepath)
#       s3_path = asset.get_content_url(follow_redirects=1, strip_query=True)

####################
# Finally, instantiate a :py:class:`~pynwb.NWBHDF5IO` object with the S3 URL and specify the driver as "ros3". This
# will download metadata about the file from the S3 bucket to memory. The values of datasets are accessed lazily,
# just like when reading an NWB file stored locally. So, slicing into a dataset will require additional time to
# download the sliced data (and only the sliced data) to memory.
#
# .. code-block:: python
#
#   from pynwb import NWBHDF5IO
#
#   with NWBHDF5IO(s3_path, mode='r', load_namespaces=True, driver='ros3') as io:
#       nwbfile = io.read()
#       print(nwbfile)
#       print(nwbfile.acquisition['lick_times'].time_series['lick_left_times'].data[:])

####################
# Method 2: s3fs
# ~~~~~~~~~~~~~~
# s3fs is a library that creates a virtual filesystem for an S3 store. With this approach, a virtual file is created
# for the file. This virtual filesystem layer will take care of requesting data from the s3 bucket whenever data is
# read from the virtual file.
#
# First install s3fs:
#
# .. code-block:: bash
#
#   pip install s3fs
#
# Then in Python:
#
# .. code-block:: python
#
#   import s3fs
#   import pynwb
#   import h5py
#
#   fs = s3fs.S3FileSystem(anon=True)
#
#   f = fs.open("s3://dandiarchive/blobs/43b/f3a/43bf3a81-4a0b-433f-b471-1f10303f9d35", 'rb')
#   file = h5py.File(f)
#   io = pynwb.NWBHDF5IO(file=file, load_namespaces=True)
#
#   io.read()
#
# The above snippet opens an arbitrary file on DANDI. You can use the ``DandiAPIClient`` to find the s3 path just as above,
# but you will need to adjust this url to give it a prefix of "s3://dandiarchive/" as shown above.


# sphinx_gallery_thumbnail_path = 'figures/gallery_thumbnails_streaming.png'
