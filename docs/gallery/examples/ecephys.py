# -*- coding: utf-8 -*-
'''
Extracellular electrophysiology data
============================================

The following examples will reference variables that may not be defined within the block they are used in. For
clarity, we define them here:
'''



import numpy as np

rate = 10.0
np.random.seed(1234)
data_len = 1000
ephys_data = np.random.rand(data_len)
ephys_timestamps = np.arange(data_len) / rate
spatial_timestamps = ephys_timestamps[::10]
spatial_data = np.cumsum(np.random.normal(size=(2, len(spatial_timestamps))), axis=-1).T

#######################
# Creating and Writing NWB files
# ------------------------------
#
# When creating a NWB file, the first step is to create the :py:class:`~pynwb.file.NWBFile`. The first
# argument is the name of the NWB file, and the second argument is a brief description of the dataset.


from datetime import datetime
from pynwb import NWBFile

f = NWBFile('the PyNWB tutorial', 'my first synthetic recording', 'EXAMPLE_ID', datetime.now(),
            experimenter='Dr. Bilbo Baggins',
            lab='Bag End Laboratory',
            institution='University of Middle Earth at the Shire',
            experiment_description='I went on an adventure with thirteen dwarves to reclaim vast treasures.',
            session_id='LONELYMTN')


#######################
# Once you have created your NWB and added all of your data and other necessary metadata, you can write it to disk using
# the :py:class:`~pynwb.form.backends.hdf5.h5tools.HDF5IO` class.


from pynwb import get_manager
from pynwb.form.backends.hdf5 import HDF5IO

filename = "example.h5"
io = HDF5IO(filename, manager=get_manager(), mode='w')
io.write(f)
io.close()

#######################
# Creating Electrode Groups
# ^^^^^^^^^^^^^^^^^^^^^^^^^
#
# Electrode groups (i.e. experimentally relevant groupings of channels) are represented by :py:class:`~pynwb.ecephys.ElectrodeGroup` objects. To create
# an electrode group, you can use the :py:class:`~pynwb.file.NWBFile` instance method :py:meth:`~pynwb.file.NWBFile.create_electrode_group`.
#
# Before creating an :py:class:`~pynwb.ecephys.ElectrodeGroup`, you need to provide some information about the device that was used to record from the electrode.
# This is done by creating a :py:class:`~pynwb.ecephys.Device` object using the instance method :py:meth:`~pynwb.file.NWBFile.create_device`.


device = f.create_device(name='trodes_rig123', source="a source")



#######################
# Once you have created the :py:class:`~pynwb.ecephys.Device`, you can create the :py:class:`~pynwb.ecephys.ElectrodeGroup`.


electrode_name = 'tetrode1'
source = "an hypothetical source"
description = "an example tetrode"
location = "somewhere in the hippocampus"

electrode_group = f.create_electrode_group(electrode_name,
                                           source=source,
                                           description=description,
                                           location=location,
                                           device=device)



#######################
# Finally, you can then create the associated :py:class:`~pynwb.ecephys.ElectrodeTable` and :py:class:`~pynwb.ecephys.ElectrodeTableRegion`.


for idx in [1, 2, 3, 4]:
    f.add_electrode(idx,
                    x=1.0, y=2.0, z=3.0,
                    imp=float(-idx),
                    location='CA1', filtering='none',
                    description='channel %s' % idx, group=electrode_group)

electrode_table_region = f.create_electrode_table_region([0, 2], 'the first and third electrodes')



#######################
# Creating TimeSeries
# ^^^^^^^^^^^^^^^^^^^
#
# TimeSeries objects can be created by instantiating :ref:`timeseries_overview` objects directly and then adding them to
# the :ref:`file_overview` using the instance method :py:func:`~pynwb.file.NWBFile.add_acquisition`.
#
# This first example will demonstrate instantiating two different types of :ref:`timeseries_overview` objects directly,
# and adding them with :py:meth:`~pynwb.file.NWBFile.add_acquisition`.


from pynwb.ecephys import ElectricalSeries
from pynwb.behavior import SpatialSeries

ephys_ts = ElectricalSeries('test_ephys_data',
                            'an hypothetical source',
                            ephys_data,
                            electrode_table_region,
                            timestamps=ephys_timestamps,
                            # Alternatively, could specify starting_time and rate as follows
                            # starting_time=ephys_timestamps[0],
                            # rate=rate,
                            resolution=0.001,
                            comments="This data was randomly generated with numpy, using 1234 as the seed",
                            description="Random numbers generated with numpy.random.rand")
f.add_acquisition(ephys_ts)

spatial_ts = SpatialSeries('test_spatial_timeseries',
                           'a stumbling rat',
                           spatial_data,
                           'origin on x,y-plane',
                           timestamps=spatial_timestamps,
                           resolution=0.1,
                           comments="This data was generated with numpy, using 1234 as the seed",
                           description="This 2D Brownian process generated with "
                                       "np.cumsum(np.random.normal(size=(2, len(spatial_timestamps))), axis=-1).T")
f.add_acquisition(spatial_ts)


#######################
# Creating Epochs
# ^^^^^^^^^^^^^^^
#
# Experimental epochs are represented with :py:class:`~pynwb.epoch.Epoch` objects. To create epochs for an NWB file,
# you can use the :py:class:`~pynwb.file.NWBFile` instance method :py:meth:`~pynwb.file.NWBFile.create_epoch`.


epoch_tags = ('example_epoch',)

f.create_epoch(name='epoch1', start_time=0.0, stop_time=1.0, tags=epoch_tags,
               description="the first test epoch", timeseries=[ephys_ts, spatial_ts])

f.create_epoch(name='epoch2', start_time=0.0, stop_time=1.0, tags=epoch_tags,
               description="the second test epoch", timeseries=[ephys_ts, spatial_ts])

