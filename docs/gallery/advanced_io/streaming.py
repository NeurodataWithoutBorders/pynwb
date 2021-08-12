'''
Streaming from an S3 Bucket
===========================

Using PyNWB 2, HDMF 3, and h5py 3.2+, you can now stream data from an NWB file stored in an S3 bucket, such as data
from the `DANDI Archive <https://dandiarchive.org/>`_. This is especially useful for reading small pieces of data
from a large NWB file stored remotely.
'''

####################
# Streaming data from an S3 bucket requires having HDF5 installed with the ROS3 (read-only S3) driver.
# You can install HDF5 with the ROS3 driver from `conda-forge <https://conda-forge.org/>`_ using ``conda``.
# You may first need to uninstall a currently installed version of h5py.
#
# .. code-block:: bash
#
#   pip uninstall h5py
#   conda install -c conda-forge "h5py>=3.2"
#

####################
# Next, use the ``DandiAPIClient`` to get the S3 URL to an NWB file of interest stored in the DANDI Archive.
# If you have not already, install the latest release of the ``dandi`` package (version 0.27 or larger).
#
# .. code-block:: bash
#
#   pip install dandi
#
# .. code-block:: python
#
#   from pynwb.utils import get_dandi_s3_url
#   from dandi.dandiapi import DandiAPIClient
#
#   dandiset_id = '000006'  # ephys dataset from the Svoboda Lab
#   filepath = 'sub-anm372795/sub-anm372795_ses-20170718.nwb'  # 450 kB file
#   with DandiAPIClient() as client:
#     asset = client.get_dandiset(dandiset_id, 'draft').get_asset_by_path('filepath')
#     s3_path = asset.get_content_url(follow_redirects=1, strip_query=True)

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
#

# sphinx_gallery_thumbnail_path = 'figures/gallery_thumbnails_streaming.png'
