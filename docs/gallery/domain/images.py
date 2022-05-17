"""
.. _images:

Images
==================================

This tutorial will demonstrate the usage of the :py:mod:`pynwb.image` module for adding
images to an :py:class:`~pynwb.file.NWBFile`.

Image data can be of individual images or of movie segments (as a movie is simply a series of images),
about the subject, the environment, the presented stimuli, or other kind
that relates to the experiment.

* :py:class:`~pynwb.image.GrayscaleImage`, :py:class:`~pynwb.image.RGBImage`, :py:class:`~pynwb.image.RGBAImage`, for static images;
* :py:class:`~pynwb.image.ImageSeries`, :py:class:`~pynwb.image.ImageMaskSeries` for series of images (movie segments);
* :py:class:`~pynwb.image.OpticalSeries` for series of images that were presented as stimulus
* :py:class:`~pynwb.image.IndexSeries` for storing indices to image frames stored in an :py:class:`~pynwb.image.ImageSeries`

The following examples will reference variables that may not be defined within the block they are used in. For
clarity, we define them here:
"""
from datetime import datetime
from dateutil import tz

import numpy as np
from PIL.Image import Image

from pynwb import NWBFile
from pynwb.base import Images
from pynwb.image import RGBAImage, RGBImage, GrayscaleImage, OpticalSeries, ImageSeries

####################
# Create an NWB File
# ------------------
#
# Create an :py:class:`~pynwb.file.NWBFile` object with the required fields
# (``session_description``, ``identifier``, ``session_start_time``) and additional metadata.

session_start_time = datetime(2018, 4, 25, 2, 30, 3, tzinfo=tz.gettz("US/Pacific"))

nwbfile = NWBFile(
    session_description="Mouse exploring an open field",  # required
    identifier="Mouse5_Day3",  # required
    session_start_time=session_start_time,  # required
    session_id="session_1234",  # optional
    experimenter="My Name",  # optional
    lab="My Lab Name",  # optional
    institution="University of My Institution",  # optional
    related_publications="DOI:10.1016/j.neuron.2016.12.011",  # optional
)

nwbfile

####################
#
# .. seealso::
#    You can learn more about the :py:class:`~pynwb.file.NWBFile` format in the :ref:`basics` tutorial.
#
# OpticalSeries: Storing series of images as stimuli
# --------------------------------------------------
#
# :py:class:`~pynwb.image.OpticalSeries` is for series of images that were presented
# to the experimental subject as stimuli.
# We will create an :py:class:`~pynwb.image.OpticalSeries` object with the name
# ``"StimulusPresentation"`` representing what images were shown to the subject and at what times.
#
# Image data can be stored either in the HDF5 file or as an external image file.
# For this tutorial, we will use a fake image data with shape of (200, 50, 50, 3).
# Images may be 3D or 4D (grayscale or RBG), where the first dimension must be time (frame).
# The second and third dimensions represent x and y.
# The fourth dimension represents the RGB value (length of 3) for color images.
#
# NWB differentiates between raw, acquired data and data that was presented as stimulus.
# We can add it to the :py:class:`~pynwb.file.NWBFile` object as stimulus data using
# the :py:meth:`~pynwb.file.NWBFile.add_stimulus` method.
#

image_data = np.random.uniform(low=0, high=255, size=(200, 50, 50, 3)).astype(int)
optical_series = OpticalSeries(
    name="StimulusPresentation",  # required
    distance=0.7,  # required
    field_of_view=[0.2, 0.3, 0.7],  # required
    orientation="lower left",  # required
    data=image_data,
    unit="m",
    format="raw",
    starting_frame=[0.0],
    rate=1.0,
    comments="no comments",
    description="The images presented to the subject as stimuli",
)

nwbfile.add_stimulus(timeseries=optical_series)

####################
# ImageSeries: Storing series of images as acquisition
# ----------------------------------------------------
#
# :py:class:`~pynwb.image.ImageSeries` is a general container for series of images acquired during
# the experiment. Image data can be stored either in the HDF5 file or as an external image file.
#
# We can add raw data to the :py:class:`~pynwb.file.NWBFile` object as *acquisition* using
# the :py:meth:`~pynwb.file.NWBFile.add_acquisition` method.
#

image_data = np.random.uniform(low=0, high=255, size=(200, 50, 50, 3)).astype(int)

behavior_images = ImageSeries(
    name="ImageSeries",
    data=image_data,
    description="Image data of an animal moving in environment.",
    unit="pixels",
    format="raw",
    starting_frame=[0.0],
    rate=1.0,
)

nwbfile.add_acquisition(behavior_images)

####################
# Static images
# -------------
#
# Static images can be stored in an :py:class:`~pynwb.file.NWBFile` object by creating an
# :py:class:`~pynwb.image.RGBAImage`, :py:class:`~pynwb.image.RGBImage` or
# :py:class:`~pynwb.image.GrayscaleImage` object with the image data.
#
# .. note::
#          All basic image types :py:class:`~pynwb.image.RGBAImage`, :py:class:`~pynwb.image.RGBImage`, and
#          :py:class:`~pynwb.image.GrayscaleImage` provide the optional: 1) ``description`` parameter to include a
#          text description about the image and 2) ``resolution`` parameter to specify the *pixels / cm* resolution
#          of the image.
#
# RGBAImage: for color images with transparency
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# :py:class:`~pynwb.image.RGBAImage` is for storing data of color image with transparency.
# :py:attr:`~pynwb.image.RGBAImage.data` must be 3D where the first and second dimensions
# represent x and y. The third dimension has length 4 and represents the RGBA value.,
#

img = Image.open("docs/source/figures/logo_pynwb.png")  # an example image

rgba_logo = RGBAImage(
    name="pynwb_RGBA_logo",
    data=np.array(img),
    resolution=70,  # in pixels / cm
    description="RGBA version of the PyNWB logo.",
)

####################
# RGBImage: for color images
# ^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# :py:class:`~pynwb.image.RGBImage` is for storing data of RGB color image.
# :py:attr:`~pynwb.image.RGBImage.data` must be 3D where the first and second dimensions
# represent x and y. The third dimension has length 3 and represents the RGB value.,
#

rgb_logo = RGBImage(
    name="pynwb_RGB_logo",
    data=np.array(img.convert("RGB")),
    resolution=70,
    description="RGB version of the PyNWB logo.",
)

####################
# GrayscaleImage: for grayscale images
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# :py:class:`~pynwb.image.GrayscaleImage` is for storing grayscale image data.
# :py:attr:`~pynwb.image.GrayscaleImage.data` must be 2D where the first and second dimensions
# represent x and y.
#

gs_logo = GrayscaleImage(
    name="pynwb_Grayscale_logo",
    data=np.array(img.convert("L")),
    description="Grayscale version of the PyNWB logo.",
    resolution=35.433071,
)

####################
# Images: a container for images
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# Add the images to an :py:class:`~pynwb.base.Images` container
# that accepts any of these image types.

images = Images(
    name="logo_images",
    images=[rgb_logo, rgba_logo, gs_logo],
    description="A collection of logo images presented to the subject.",
)

####################
# Create a Processing Module
# ----------------------------------
#
# Create a processing module called ``"images"`` for storing image data in the :py:class:`~pynwb.file.NWBFile`
# using the :py:meth:`~pynwb.file.NWBFile.create_processing_module` method, then and add the
# :py:class:`~pynwb.base.Images` container to the processing module.


images_module = nwbfile.create_processing_module(
    name="images", description="Static images presented to the subject."
)

images_module.add(images)

####################
# .. seealso::
#    You can read more about the basic concepts of processing modules in the :ref:`modules_overview` tutorial.
#
