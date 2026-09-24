"""
Zarr IO
=======

Zarr is an alternative backend option for NWB files. It is a Python package that
provides an implementation of chunked, compressed, N-dimensional arrays. Zarr is a good
option for large datasets because, like HDF5, it is designed to store data on disk and
only load the data into memory when needed. Zarr is also a good option for parallel
computing because it supports concurrent reads and writes.

Note that the Zarr native storage formats are optimized for storage in cloud storage
(e.g., S3). For very large files, Zarr will create many files which can lead to
issues for traditional file system (that are not cloud object stores) due to limitations
on the number of files per directory (this affects local disk, GDrive, Dropbox etc.).

Zarr read and write is provided by the :hdmf-zarr:`hdmf-zarr<>` package. First, create an
an NWBFile using PyNWB.
"""

# sphinx_gallery_thumbnail_path = 'figures/gallery_thumbnail_plot_nwbzarrio.png'


from datetime import datetime
from dateutil.tz import tzlocal

import numpy as np
from pynwb import NWBFile, TimeSeries

# Create the NWBFile. Substitute your NWBFile generation here.
nwbfile = NWBFile(
    session_description="my first synthetic recording",
    identifier="EXAMPLE_ID",
    session_start_time=datetime.now(tzlocal()),
    session_id="LONELYMTN",
)

#######################################################################################
# Dataset Configuration
# ---------------------
# Like HDF5, Zarr provides options to chunk and compress datasets. To leverage these
# features, replace all :py:class:`~hdmf.backends.hdf5.h5_utils.H5DataIO` with the analogous
# :py:class:`~hdmf_zarr.utils.ZarrDataIO`, which takes compressors specified by the
# :py:mod:`numcodecs` library. For example, here is an example :py:class:`.TimeSeries`
# where the ``data`` Dataset is compressed with a Blosc-zstd compressor:

from numcodecs import Blosc
from hdmf_zarr import ZarrDataIO

data_with_zarr_data_io = ZarrDataIO(
    data=np.random.randn(100, 100),
    chunks=(10, 10),
    fillvalue=0,
    compressor=Blosc(cname='zstd', clevel=3, shuffle=Blosc.SHUFFLE)
)

#######################################################################################
# Now add it to the :py:class:`.NWBFile`.

nwbfile.add_acquisition(
    TimeSeries(
        name="synthetic_timeseries",
        data=data_with_zarr_data_io,
        unit="m",
        rate=10e3,
    )
)

#######################################################################################
# Writing to Zarr
# ---------------
# To write NWB files to Zarr, replace the :py:class:`~pynwb.NWBHDF5IO` with
# :py:class:`hdmf_zarr.nwb.NWBZarrIO`.

from hdmf_zarr.nwb import NWBZarrIO
import os

path = "zarr_tutorial.nwb.zarr"
absolute_path = os.path.abspath(path)
with NWBZarrIO(path=path, mode="w") as io:
    io.write(nwbfile)

#######################################################################################
# .. note::
#   The main reason for using the ``absolute_path`` here is for testing purposes to
#   ensure links and references work as expected. Otherwise, using the relative path
#   here instead is fine.
#
# Reading from Zarr
# -----------------
# To read NWB files from Zarr, replace the :py:class:`~pynwb.NWBHDF5IO` with the analogous
# :py:class:`hdmf_zarr.nwb.NWBZarrIO`.

with NWBZarrIO(path=absolute_path, mode="r") as io:
    read_nwbfile = io.read()

#######################################################################################
# Streaming from DANDI
# -------------------
# One of the advantages of Zarr is its ability to efficiently stream data from cloud storage.
# Here's how to stream NWB files stored in Zarr format from the DANDI archive:

from dandi.dandiapi import DandiAPIClient
import zarr
import s3fs

# Initialize DANDI client and get a dandiset
client = DandiAPIClient()
dandiset = client.get_dandiset("000001", "draft")  # Replace with your dandiset ID

# Get an asset's S3 URL
asset = next(dandiset.get_assets())
s3_url = asset.get_content_url(follow_redirects=1, strip_query=True)

# Set up S3 access
fs = s3fs.S3FileSystem(anon=True)
store = zarr.S3Store(s3_url, client_kwargs={'S3': {'anon': True}})

# Stream data efficiently
with NWBZarrIO(path=store, mode='r') as io:
    nwbfile = io.read()
    
    # Example: Access specific chunks of data
    # This only loads the requested timepoints into memory
    if 'neural_data' in nwbfile.acquisition:
        chunk = nwbfile.acquisition['neural_data'].data[:1000]

    # Process data in chunks for memory efficiency
    chunk_size = 1000
    if 'neural_data' in nwbfile.acquisition:
        total_size = len(nwbfile.acquisition['neural_data'].data)
        for i in range(0, total_size, chunk_size):
            chunk = nwbfile.acquisition['neural_data'].data[i:i+chunk_size]
            # Process your chunk here
            chunk_mean = chunk.mean()

# Clean up S3 filesystem cache
fs.clear_instance_cache()

#######################################################################################
# .. note::
#    For more information, see the :hdmf-zarr:`hdmf-zarr documentation<>`.
