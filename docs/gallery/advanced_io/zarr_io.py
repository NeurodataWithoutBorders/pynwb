"""
Zarr IO
=======

Zarr is an alternative backend option for NWB files. It is a Python package that
provides an implementation of chunked, compressed, N-dimensional arrays. Zarr is a good
option for large datasets because, like HDF5, it is designed to store data on disk and
only load the data into memory when needed. Zarr is also a good option for parallel
computing because it supports concurrent reads and writes.

Zarr read and write is provided by the :hdmf-zarr:`hdmf-zarr` package. First, create an
an NWBFile using PyNWB.
"""

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
# `numcodecs` library. For example, to create a :py:class:`.TimeSeries`
# with a Zarr backend, use the following:

from numcodecs import Blosc
from hdmf_zarr import ZarrDataIO

data_with_zarr_data_io = ZarrDataIO(
    data=np.random.randn(100, 100),
    chunks=(10, 10),
    fillvalue=0,
    compressor=Blosc(cname='zstd', clevel=3, shuffle=Blosc.SHUFFLE)
)

#######################################################################################
# Now add it to the `NWBFile`.

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
# :py:class:`hdmf_zarr.nwb.NWBZarrIO` for read/write

from hdmf_zarr.nwb import NWBZarrIO
import os

path = "zarr_tutorial.nwb.zarr"
absolute_path = os.path.abspath(path)
with NWBZarrIO(path=path, mode="w") as io:
    io.write(nwbfile)

#######################################################################################
# The main reason for using the absolute_path here is for testing purposes to ensure
# links and references work as expected. Otherwise, using the relative path here instead
# is fine.
#
# Reading from Zarr
# -----------------
# To read NWB files from Zarr, replace the :py:class:`~pynwb.NWBHDF5IO` with the analogous
# :py:class:`hdmf_zarr.nwb.NWBZarrIO`.

with NWBZarrIO(path=absolute_path, mode="r") as io:
    read_nwbfile = io.read()

#######################################################################################
# For more information, see the :hdmf-zarr:`hdmf-zarr documentation<>`.

