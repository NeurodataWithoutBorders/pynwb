'''
Parallel I/O using MPI
======================

The HDF5 storage backend supports parallel I/O using the Message Passing Interface (MPI).
Using this feature requires that you install ``hdf5`` and ``h5py`` against an MPI driver, and you
install ``mpi4py``. The basic installation of pynwb will not work. Setup can be tricky, and
is outside the scope of this tutorial (for now), and the following assumes that you have
HDF5 installed in a MPI configuration.
'''

# sphinx_gallery_thumbnail_path = 'figures/gallery_thumbnails_parallelio.png'

####################
# Here we:
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
