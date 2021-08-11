'''
Streaming from an S3 Bucket
===========================

Using PyNWB 2, HDMF 3, and h5py 3.2+, you can now stream data from an NWB file stored in an S3 bucket, such as data
from the `DANDI Archive <https://dandiarchive.org/>`_. This is especially useful for reading small pieces of data
from a large NWB file stored remotely.
'''

# sphinx_gallery_thumbnail_path = ''  # TODO

####################
# Streaming data from an S3 bucket requires having HDF5 installed with the ROS3 (read-only S3) driver.
# The example code below also requires the ``requests`` package to be installed.
# You can install HDF5 with the ROS3 driver from `conda-forge <https://conda-forge.org/>`_ using ``conda``.
# You may first need to uninstall a currently installed version of h5py.
#
# .. code-block:: bash
#
#   pip uninstall h5py
#   conda install -c conda-forge "h5py>=3.2" requests
#

####################
# Next, in Python, import the ``requests`` package and define helper functions for accessing data
# from the DANDI Archive.
#
# .. code-block:: python
#
#   import requests
#
#   def _search_dandi_assets(url, filepath):
#       response = requests.request("GET", url, headers={"Accept": "application/json"}).json()
#
#       for asset in response["results"]:
#           if filepath == asset["path"]:
#               return asset["asset_id"]
#
#       if response.get("next", None):
#           return _search_dandi_assets(response["next"], filepath)
#
#       return None
#
#
#   def get_dandi_asset_id(dandiset_id, filepath):
#       url = f"https://api.dandiarchive.org/api/dandisets/{dandiset_id}/versions/draft/assets/"
#       asset_id = _search_dandi_assets(url, filepath)
#       if asset_id is None:
#           raise ValueError(f'path {filepath} not found in dandiset {dandiset_id}.')
#       return asset_id
#
#
#   def get_dandi_s3_url(dandiset_id, filepath):
#       """Get the s3 location for any NWB file on DANDI"""
#
#       asset_id = get_dandi_asset_id(dandiset_id, filepath)
#       url = f"https://api.dandiarchive.org/api/dandisets/{dandiset_id}/versions/draft/assets/{asset_id}/download/"
#
#       s3_url = requests.request(url=url, method='head').url
#       if '?' in s3_url:
#           return s3_url[:s3_url.index('?')]
#       return s3_url

####################
# Next, use the helper functions above to get the S3 URL to an NWB file of interest stored in the DANDI Archive.
#
# .. code-block:: python
#
#   dandiset_id = '000006'  # ephys dataset, Svoboda Lab
#   filepath = 'sub-anm372795/sub-anm372795_ses-20170718.nwb'  # 450 kB file
#   s3_path = get_dandi_s3_url(dandiset_id, filepath)

####################
# Finally, instantiate a :py:class:`~pynwb.NWBHDF5IO` object with the S3 URL and specify the driver as "ros3". This
# will download metadata about the file from the S3 bucket to memory. Datasets are accessed lazily, just like when
# reading an NWB file stored locally. So, slicing into a dataset will require additional time to download the sliced
# data to memory.
#
# .. code-block:: python
#
#   from pynwb import NWBHDF5IO
#
#   with NWBHDF5IO(s3_path, mode='r', load_namespaces=True, driver='ros3') as io:
#       nwbfile = io.read()
#       print(nwbfile)
#       print(nwbfile.acquisition['lick_times'].time_series['lick_left_times'])
#       print(nwbfile.acquisition['lick_times'].time_series['lick_left_times'].data[:])
#
