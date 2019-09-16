# -*- coding: utf-8 -*-
'''
Calcium imaging data
============================

This tutorial will demonstrate how to write calcium imaging data. The workflow demonstrated here involves
three main steps:

1. Acquiring two-photon images
2. Image segmentation
3. Fluorescence and dF/F response

This tutorial assumes that transforming data between these three states is done by users--PyNWB does not provide
analysis functionality.

The following examples will reference variables that may not be defined within the block they are used in. For
clarity, we define them here:
'''

from datetime import datetime
from dateutil.tz import tzlocal

import numpy as np

from pynwb import NWBFile
from pynwb.ophys import TwoPhotonSeries, OpticalChannel, ImageSegmentation, Fluorescence
from pynwb.device import Device


####################
# Creating and Writing NWB files
# ------------------------------
#
# When creating a NWB file, the first step is to create the :py:class:`~pynwb.file.NWBFile`.


nwbfile = NWBFile('my first synthetic recording', 'EXAMPLE_ID', datetime.now(tzlocal()),
                  experimenter='Dr. Bilbo Baggins',
                  lab='Bag End Laboratory',
                  institution='University of Middle Earth at the Shire',
                  experiment_description=('I went on an adventure with thirteen '
                                          'dwarves to reclaim vast treasures.'),
                  session_id='LONELYMTN')

####################
# Adding metadata about acquisition
# ---------------------------------
#
# Before you can add your data, you will need to provide some information about how that data was generated.
# This amounts describing the device, imaging plane and the optical channel used.


device = Device('imaging_device_1')
nwbfile.add_device(device)
optical_channel = OpticalChannel('my_optchan', 'description', 500.)
imaging_plane = nwbfile.create_imaging_plane('my_imgpln', optical_channel, 'a very interesting part of the brain',
                                             device, 600., 300., 'GFP', 'my favorite brain location',
                                             np.ones((5, 5, 3)), 4.0, 'manifold unit', 'A frame to refer to')


####################
# Adding two-photon image data
# ----------------------------
#
# Now that you have your :py:class:`~pynwb.ophys.ImagingPlane`, you can create a
# :py:class:`~pynwb.ophys.TwoPhotonSeries` - the class representing two photon imaging data.
#
# From here you have two options. The first option is to supply the image data to PyNWB, using the `data` argument.
# The other option is the provide a path the images. These two options have trade-offs, so it is worth spending time
# considering how you want to store this data [#]_.


image_series = TwoPhotonSeries(name='test_iS', dimension=[2],
                               external_file=['images.tiff'], imaging_plane=imaging_plane,
                               starting_frame=[0], format='tiff', starting_time=0.0, rate=1.0)
nwbfile.add_acquisition(image_series)


####################
# Storing image segmentation output
# ---------------------------------
#
# Now that the raw data is stored, you can add the image segmentation results. This is done with the
# :py:class:`~pynwb.ophys.ImageSegmentation` data interface. This class has the ability to store segmentation
# from one or more imaging planes; hence the :py:class:`~pynwb.ophys.PlaneSegmentation` class.


mod = nwbfile.create_processing_module('ophys', 'contains optical physiology processed data')
img_seg = ImageSegmentation()
mod.add(img_seg)
ps = img_seg.create_plane_segmentation('output from segmenting my favorite imaging plane',
                                       imaging_plane, 'my_planeseg', image_series)


####################
# Now that you have your :py:class:`~pynwb.ophys.PlaneSegmentation` object, you can add the resulting ROIs.
# This is done using the method :py:func:`~pynwb.ophys.PlaneSegmentation.add_roi`. The first argument to this
# method is the `pixel_mask` and the second method is the `image_mask`. The NWB schema allows for either argument
# to be provided.


w, h = 3, 3
pix_mask1 = [(0, 0, 1.1), (1, 1, 1.2), (2, 2, 1.3)]
img_mask1 = [[0.0 for x in range(w)] for y in range(h)]
img_mask1[0][0] = 1.1
img_mask1[1][1] = 1.2
img_mask1[2][2] = 1.3
ps.add_roi(pixel_mask=pix_mask1, image_mask=img_mask1)

pix_mask2 = [(0, 0, 2.1), (1, 1, 2.2)]
img_mask2 = [[0.0 for x in range(w)] for y in range(h)]
img_mask2[0][0] = 2.1
img_mask2[1][1] = 2.2
ps.add_roi(pixel_mask=pix_mask2, image_mask=img_mask2)


####################
# Storing fluorescence measurements
# ---------------------------------
#
# Now that ROIs are stored, you can store fluorescence (or dF/F [#]_) data for these regions of interest.
# This type of data is stored using the :py:class:`~pynwb.ophys.RoiResponseSeries` class. You will not need
# to instantiate this class directly to create objects of this type, but it is worth noting that this is the
# class you will work with after you read data back in.
#
#
# First, create a data interface to store this data in


fl = Fluorescence()
mod.add(fl)


####################
# Because this data stores information about specific ROIs, you will need to provide a reference to the ROIs
# that you will be storing data for. This is done using a :py:class:`~pynwb.core.DynamicTableRegion`, which can be
# created with :py:func:`~pynwb.ophys.PlaneSegmentation.create_roi_table_region`.


rt_region = ps.create_roi_table_region('the first of two ROIs', region=[0])

####################
# Now that you have an :py:class:`~pynwb.core.DynamicTableRegion`, you can create your an
# :py:class:`~pynwb.ophys.RoiResponseSeries`.


data = [0., 1., 2., 3., 4., 5., 6., 7., 8., 9.]
timestamps = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
rrs = fl.create_roi_response_series('my_rrs', data, rt_region, unit='lumens', timestamps=timestamps)


####################
# .. note:: You can also store more than one :py:class:`~pynwb.ophys.RoiResponseSeries` by calling
#    :py:func:`~pynwb.ophys.Fluorescence.create_roi_response_series` again.


####################
# Once we have finished adding all of our data to our :py:class:`~pynwb.file.NWBFile`, make sure to write the file.
# Writing (and reading) is carried out using :py:class:`~pynwb.NWBHDF5IO`.

from pynwb import NWBHDF5IO

with NWBHDF5IO('ophys_example.nwb', 'w') as io:
    io.write(nwbfile)

####################
# Reading an NWBFile
# ------------------
#
# Reading is carried out using the :py:class:`~pynwb.NWBHDF5IO` class. Unlike with writing, using
# :py:class:`~pynwb.NWBHDF5IO` as a context manager is not supported and will raise an exception [#]_.


io = NWBHDF5IO('ophys_example.nwb', 'r')
nwbfile = io.read()


####################
# Getting your data out
# ---------------------
#
# After you read the NWB file, you can access individual components of your data file.
# To get the :py:class:`~pynwb.base.ProcessingModule` back, you can index into the
# :py:func:`~pynwb.file.NWBFile.processing` attribute with the name of the
# :py:class:`~pynwb.base.ProcessingModule`.


mod = nwbfile.processing['ophys']

####################
# Now you can retrieve the :py:class:`~pynwb.ophys.ImageSegmentation` object by indexing into the
# :py:class:`~pynwb.base.ProcessingModule` with the name of the :py:class:`~pynwb.ophys.ImageSegmentation` container.
# In our case, this is just "ImageSegmentation", since we did not provide a name and kept the default name.
#

ps = mod['ImageSegmentation'].get_plane_segmentation()

####################
# Once you have the original :py:class:`~pynwb.ophys.PlaneSegmentation` object, you can retrieve your
# image masks and pixel masks using standard indexing.
#

img_mask1 = ps['image_mask'][0]
pix_mask1 = ps['pixel_mask'][0]
img_mask2 = ps['image_mask'][1]
pix_mask2 = ps['pixel_mask'][1]

####################
# To get back the fluorescence time series data, first access the :py:class:`~pynwb.ophys.Fluorescence` object we added
# (like we did above with :py:class:`~pynwb.ophys.ImageSegmentation`) and then retrieve the
# :py:class:`~pynwb.ophys.RoiResponseSeries` using :py:func:`~pynwb.ophys.Fluorescence.create_roi_response_series` [#]_.
rrs = mod['Fluorescence'].get_roi_response_series()


# get the data...
rrs_data = rrs.data
rrs_timestamps = rrs.timestamps
rrs_rois = rrs.rois
# and now do something cool!

####################
#
# .. [#] If you pass in the image data directly,
#    you will not need to worry about distributing the image files with your NWB file. However, we recognize that
#    common image formats have tools built around them, so working with the original file formats can make
#    one's life much simpler. NWB currently does not have the ability to read and parse native image formats. It
#    is up to downstream users to read these file formats.
#
# .. [#] You can also store dF/F data using the :py:class:`~pynwb.ophys.DfOverF` class.
#
# .. [#] Neurodata sets can be *very* large, so individual components of the dataset are only loaded into memory when
#    you requst them. This functionality is only possible if closing of the :py:class:`~pynwb.NWBHDF5IO`
#    object is handled by the user.
#
# .. [#] If you added more than one :py:class:`~pynwb.ophys.RoiResponseSeries`, you will need to
#    provide the name of the :py:class:`~pynwb.ophys.RoiResponseSeries` you want to retrieve to
#    :py:func:`~pynwb.ophys.Fluorescence.create_roi_response_series`. This same behavior is exhibited
#    with :py:class:`~pynwb.ophys.ImageSegmentation` and various other objects through the PyNWB API.
