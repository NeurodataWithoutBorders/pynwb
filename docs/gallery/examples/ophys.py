# -*- coding: utf-8 -*-
'''
Writing Calcium Imaging data
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



import os
from datetime import datetime

from pynwb import NWBFile, NWBHDF5IO
from pynwb.ophys import TwoPhotonSeries, OpticalChannel, ImageSegmentation, Fluorescence


#######################
# Creating and Writing NWB files
# ------------------------------
#
# When creating a NWB file, the first step is to create the :py:class:`~pynwb.file.NWBFile`. The first
# argument is the name of the NWB file, and the second argument is a brief description of the dataset.


nwb_path = 'ophys_example.nwb'
# create your NWBFile object
nwbfile = NWBFile('the PyNWB tutorial', 'my first synthetic recording', 'EXAMPLE_ID', datetime.now(),
                  experimenter='Dr. Bilbo Baggins',
                  lab='Bag End Laboratory',
                  institution='University of Middle Earth at the Shire',
                  experiment_description='I went on an adventure with thirteen dwarves to reclaim vast treasures.',
                  session_id='LONELYMTN')

#######################
# Adding metadata about acquisition
# ---------------------------------
#
# Before you can add your data, you will need to provide some information about how that data was generated.
# This amounts describing the imaging plane and the optical channel used.


optical_channel = OpticalChannel('test_optical_channel', 'optical channel source',
                                 'optical channel description', '3.14')
imaging_plane = nwbfile.create_imaging_plane('test_imaging_plane',
                                             'ophys integration tests',
                                             optical_channel,
                                             'imaging plane description',
                                             'imaging_device_1',
                                             '6.28', '2.718', 'GFP', 'somewhere in the brain',
                                             (1, 2, 1, 2, 3), 4.0, 'manifold unit', 'A frame to refer to')


#######################
# Adding two-photon image data
# ----------------------------
#
# Now that you have your :py:class:`~pynwb.ophys.ImagingPlane`, you can create a
# :py:class:`~pynwb.ophys.TwoPhotonSeries` - the class representing two photon imaging data.
#
# From here you have two options. The first option is to supply the image data to PyNWB, using the `data` argument.
# The other option is the provide a path the images. These two options have trade-offs, so it is worth spending time
# considering how you want to store this data [#]_.
#
# .. [#] If you pass in the image data directily,
#    you will not need to worry about distributing the image files with your NWB file. However, we recognize that
#    using commong image formats have tools built around them, so working with the original file formats can make
#    one's life much simpler. NWB currently does not have the ability to read and parse native image formats. It
#    is up to downstream users to read these file formats.


image_series = TwoPhotonSeries(name='test_iS', source='a hypothetical source', dimension=[2],
                               external_file=['images.tiff'], imaging_plane=imaging_plane,
                               starting_frame=[0], format='tiff', timestamps=list())
nwbfile.add_acquisition(image_series)


#######################
# Storing image segmentation output
# ---------------------------------
#
# Now that the raw data is stored, you can add the image segmentation results. This is done with the
# :py:class:`~pynwb.ophys.ImageSegmentation` data interface. This class has the ability to store segmentation
# from one or more imaging planes; hence the :py:class:`~pynwb.ophys.PlaneSegmentation` class.


mod = nwbfile.create_processing_module('img_seg_example', 'ophys demo', 'an example of writing Ca2+ imaging data')
img_seg = ImageSegmentation('a toy image segmentation container')
mod.add_data_interface(img_seg)
ps = img_seg.create_plane_segmentation('integration test PlaneSegmentation', 'plane segmentation description',
                                       imaging_plane, 'test_plane_seg_name', image_series)


#######################
# Now that you have your :py:class:`~pynwb.ophys.PlaneSegmentation` object, you can add the resulting ROIs.
# This is done using the method :py:func:`~pynwb.ophys.PlaneSegmentation.add_roi`. The first argument to this
# method is the `pixel_mask` and the second method is the `image_mask`. Both of these arguments are required
# for schema compliance--the NWB schema requires that you store both the image mask and the pixel mask.


w, h = 3, 3
pix_mask1 = [(0, 0, 1.1), (1, 1, 1.2), (2, 2, 1.3)]
img_mask1 = [[0.0 for x in range(w)] for y in range(h)]
img_mask1[0][0] = 1.1
img_mask1[1][1] = 1.2
img_mask1[2][2] = 1.3
ps.add_roi(pix_mask1, img_mask1)

pix_mask2 = [(0, 0, 2.1), (1, 1, 2.2)]
img_mask2 = [[0.0 for x in range(w)] for y in range(h)]
img_mask2[0][0] = 2.1
img_mask2[1][1] = 2.2
ps.add_roi(pix_mask2, img_mask2)


#######################
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
#
# .. [#] You can also store dF/F data using the :py:class:`~pynwb.ophys.DfOverF` class.


fl = Fluorescence('a toy fluorescence container')
mod.add_data_interface(fl)


#######################
# Because this data stores information about specific ROIs, you will need to provide a reference to the ROIs
# that you will be storing data for. This is done using a :py:class:`~pynwb.ophys.ROITableRegion`, which can be
# created with :py:func:`~pynwb.ophys.PlaneSegmentation.create_roi_table_region`.


rt_region = ps.create_roi_table_region([0], 'the first of two ROIs')


#######################
# Now that you have an :py:class:`~pynwb.ophys.ROITableRegion`, you can create your an :py:class:`~pynwb.ophys.RoiResponseSeries`.


data = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
timestamps = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
rrs = fl.create_roi_response_series('test_roi_response_series', 'RoiResponseSeries integration test',
                                    data, 'lumens', rt_region, timestamps=timestamps)


#######################
# .. note:: You can also store more than one :py:class:`~pynwb.ophys.RoiResponseSeries` by calling
#    :py:func:`~pynwb.ophys.Fluorescence.create_roi_response_series` again.


# write data
with NWBHDF5IO(nwb_path, 'w') as io:
    io.write(nwbfile)

# read data back in
io = NWBHDF5IO(nwb_path, 'r')
nwbfile = io.read()

# get the processing module
mod = nwbfile.get_processing_module('img_seg_example')

# get the PlaneSegmentation from the ImageSegmentation data interface
ps = mod['ImageSegmentation'].get_plane_segmentation()
img_mask1 = ps.get_image_mask(0)
pix_mask1 = ps.get_pixel_mask(0)
img_mask2 = ps.get_image_mask(1)
pix_mask2 = ps.get_pixel_mask(1)

# get the RoiResponseSeries from the Fluorescence data interface
rrs = mod['Fluorescence'].get_roi_response_series()
# get the data...
rrs_data = rrs.data                           # noqa: F841
rrs_timestamps = rrs.timestamps               # noqa: F841
# and now do something cool!

io.close()
if os.path.exists(nwb_path):
    os.remove(nwb_path)
