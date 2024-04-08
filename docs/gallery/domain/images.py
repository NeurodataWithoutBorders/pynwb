"""
.. _images:

Storing Image Data in NWB
==========================

This tutorial will demonstrate the usage of the :py:mod:`pynwb.image` module for adding
images to an :py:class:`~pynwb.file.NWBFile`.

Image data can be a collection of individual images or movie segments (as a movie is simply a series of images),
about the subject, the environment, the presented stimuli, or other parts
related to the experiment. This tutorial focuses in particular on the usage of:

* :py:class:`~pynwb.image.OpticalSeries` for series of images that were presented as stimulus
* :py:class:`~pynwb.image.ImageSeries`, for series of images (movie segments);
* :py:class:`~pynwb.image.GrayscaleImage`, :py:class:`~pynwb.image.RGBImage`,
  :py:class:`~pynwb.image.RGBAImage`, for static images;

The following examples will reference variables that may not be defined within the block they are used in. For
clarity, we define them here:
"""
# Define file paths used in the tutorial

import os

# sphinx_gallery_thumbnail_path = 'figures/gallery_thumbnails_image_data.png'
from datetime import datetime
from uuid import uuid4

import numpy as np
from dateutil import tz
from dateutil.tz import tzlocal
from PIL import Image

from pynwb import NWBHDF5IO, NWBFile
from pynwb.base import Images
from pynwb.image import GrayscaleImage, ImageSeries, OpticalSeries, RGBAImage, RGBImage

nwbfile_path = os.path.abspath("images_tutorial.nwb")
moviefiles_path = [
    os.path.abspath("image/file_1.tiff"),
    os.path.abspath("image/file_2.tiff"),
    os.path.abspath("image/file_3.tiff"),
]

####################
# Create an NWB File
# ------------------
#
# Create an :py:class:`~pynwb.file.NWBFile` object with the required fields
# (``session_description``, ``identifier``, ``session_start_time``) and additional metadata.

session_start_time = datetime(2018, 4, 25, 2, 30, 3, tzinfo=tz.gettz("US/Pacific"))

nwbfile = NWBFile(
    session_description="my first synthetic recording",
    identifier=str(uuid4()),
    session_start_time=datetime.now(tzlocal()),
    experimenter=[
        "Baggins, Bilbo",
    ],
    lab="Bag End Laboratory",
    institution="University of Middle Earth at the Shire",
    experiment_description="I went on an adventure to reclaim vast treasures.",
    session_id="LONELYMTN001",
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
# :py:class:`~pynwb.image.OpticalSeries` is for time series of images that were presented
# to the subject as stimuli.
# We will create an :py:class:`~pynwb.image.OpticalSeries` object with the name
# ``"StimulusPresentation"`` representing what images were shown to the subject and at what times.
#
# Image data can be stored either in the HDF5 file or as an external image file.
# For this tutorial, we will use fake image data with shape of ``('time', 'x', 'y', 'RGB') = (200, 50, 50, 3)``.
# As in all :py:class:`~pynwb.base.TimeSeries`, the first dimension is time.
# The second and third dimensions represent x and y.
# The fourth dimension represents the RGB value (length of 3) for color images.
#
# NWB differentiates between acquired data and data that was presented as stimulus.
# We can add it to the :py:class:`~pynwb.file.NWBFile` object as stimulus data using
# the :py:meth:`~pynwb.file.NWBFile.add_stimulus` method.
#

image_data = np.random.randint(low=0, high=255, size=(200, 50, 50, 3), dtype=np.uint8)
optical_series = OpticalSeries(
    name="StimulusPresentation",  # required
    distance=0.7,  # required
    field_of_view=[0.2, 0.3, 0.7],  # required
    orientation="lower left",  # required
    data=image_data,
    unit="n.a.",
    format="raw",
    starting_frame=[0.0],
    rate=1.0,
    comments="no comments",
    description="The images presented to the subject as stimuli",
)

nwbfile.add_stimulus(stimulus=optical_series)

####################
# ImageSeries: Storing series of images as acquisition
# ----------------------------------------------------
#
# :py:class:`~pynwb.image.ImageSeries` is a general container for time series of images acquired during
# the experiment. Image data can be stored either in the HDF5 file or as an external image file.
# When color images are stored in the HDF5 file the color channel order is expected to be RGB.
#
# We can add raw data to the :py:class:`~pynwb.file.NWBFile` object as *acquisition* using
# the :py:meth:`~pynwb.file.NWBFile.add_acquisition` method.
#

image_data = np.random.randint(low=0, high=255, size=(200, 50, 50, 3), dtype=np.uint8)
behavior_images = ImageSeries(
    name="ImageSeries",
    data=image_data,
    description="Image data of an animal moving in environment.",
    unit="n.a.",
    format="raw",
    rate=1.0,
    starting_time=0.0,
)

nwbfile.add_acquisition(behavior_images)

####################
# External Files
# ^^^^^^^^^^^^^^
#
# External files (e.g. video files of the behaving animal) can be added to the :py:class:`~pynwb.file.NWBFile`
# by creating an :py:class:`~pynwb.image.ImageSeries` object using the 
# :py:attr:`~pynwb.image.ImageSeries.external_file` attribute that specifies
# the path to the external file(s) on disk.
# The file(s) path must be relative to the path of the NWB file.
# Either ``external_file`` or ``data`` must be specified, but not both.
#
# If the sampling rate is constant, use :py:attr:`~pynwb.base.TimeSeries.rate` and 
# :py:attr:`~pynwb.base.TimeSeries.starting_time` to specify time.
# For irregularly sampled recordings, use :py:attr:`~pynwb.base.TimeSeries.timestamps` to specify time for each sample
# image.
#
# Each external image may contain one or more consecutive frames of the full :py:class:`~pynwb.image.ImageSeries`.
# The :py:attr:`~pynwb.image.ImageSeries.starting_frame` attribute serves as an index to indicate which frame
# each file contains.
# For example, if the ``external_file`` dataset has three paths to files and the first and the second file have 2 
# frames, and the third file has 3 frames, then this attribute will have values `[0, 2, 4]`.

external_file = [
    os.path.relpath(movie_path, nwbfile_path) for movie_path in moviefiles_path
]
# We have 3 movie files each containing multiple frames. We here need to specify the timestamp for each frame.
timestamps = [0.0, 0.04, 0.07, 0.1, 0.14, 0.16, 0.21]
behavior_external_file = ImageSeries(
    name="ExternalFiles",
    description="Behavior video of animal moving in environment.",
    unit="n.a.",
    external_file=external_file,
    format="external",
    starting_frame=[0, 2, 4],
    timestamps=timestamps,
)

nwbfile.add_acquisition(behavior_external_file)

####################
# .. note::
#          See the :dandi:`External Links in NWB and DANDI </2022/03/03/external-links-organize.html>`
#          guidelines of the :dandi:`DANDI <>` data archive for best practices on how to organize
#          external files, e.g., movies and images.
#
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
# ``RGBAImage.data`` must be 3D where the first and second dimensions
# represent x and y. The third dimension has length 4 and represents the RGBA value.
#

img = Image.open("docs/source/figures/logo_pynwb.png")  # an example image

rgba_logo = RGBAImage(
    name="pynwb_RGBA_logo",
    data=np.array(img),
    resolution=70.0,  # in pixels / cm
    description="RGBA version of the PyNWB logo.",
)

####################
# RGBImage: for color images
# ^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# :py:class:`~pynwb.image.RGBImage` is for storing data of RGB color image.
# ``RGBImage.data`` must be 3D where the first and second dimensions
# represent x and y. The third dimension has length 3 and represents the RGB value.
#

rgb_logo = RGBImage(
    name="pynwb_RGB_logo",
    data=np.array(img.convert("RGB")),
    resolution=70.0,
    description="RGB version of the PyNWB logo.",
)

####################
# GrayscaleImage: for grayscale images
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# :py:class:`~pynwb.image.GrayscaleImage` is for storing grayscale image data.
# ``GrayscaleImage.data`` must be 2D where the first and second dimensions represent x and y.
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

nwbfile.add_acquisition(images)

####################
# IndexSeries for repeated images
# -------------------------------
#
# You may want to set up a time series of images where some images are repeated many
# times. You could create an :py:class:`~pynwb.image.ImageSeries` that repeats the data
# each time the image is shown, but that would be inefficient, because it would store
# the same data multiple times. A better solution would be to store the unique images
# once and reference those images. This is how :py:class:`~pynwb.image.IndexSeries`
# works. First, create an :py:class:`~pynwb.base.Images` container with the order of
# images defined using an :py:class:`~pynwb.base.ImageReferences`. Then create an
# :py:class:`~pynwb.image.IndexSeries` that indexes into the
# :py:class:`~pynwb.base.Images`.

from scipy import misc

from pynwb.base import ImageReferences
from pynwb.image import GrayscaleImage, Images, IndexSeries, RGBImage

gs_face = GrayscaleImage(
    name="gs_face",
    data=misc.face(gray=True),
    description="Grayscale version of a raccoon.",
    resolution=35.433071,
)

rgb_face = RGBImage(
    name="rgb_face",
    data=misc.face(),
    resolution=70.0,
    description="RGB version of a raccoon.",
)

images = Images(
    name="raccoons",
    images=[rgb_face, gs_face],
    description="A collection of raccoons.",
    order_of_images=ImageReferences("order_of_images", [rgb_face, gs_face]),
)

idx_series = IndexSeries(
    name="stimuli",
    data=[0, 1, 0, 1],
    indexed_images=images,
    unit="N/A",
    timestamps=[0.1, 0.2, 0.3, 0.4],
)

####################
# Here `data` contains the (0-indexed) index of the displayed image as they are ordered
# in the :py:class:`~pynwb.base.ImageReferences`.
#
# Writing the images to an NWB File
# ---------------------------------------
# As demonstrated in the :ref:`basic_writing` tutorial, we will use :py:class:`~pynwb.NWBHDF5IO`
# to write the file.

with NWBHDF5IO(nwbfile_path, "w") as io:
    io.write(nwbfile)

####################
# Reading and accessing data
# --------------------------
#
# To read the NWB file, use another :py:class:`~pynwb.NWBHDF5IO` object,
# and use the :py:meth:`~pynwb.NWBHDF5IO.read` method to retrieve an
# :py:class:`~pynwb.file.NWBFile` object.
#
# We can access the data added as acquisition to the NWB File by indexing ``nwbfile.acquisition``
# with the name of the :py:class:`~pynwb.image.ImageSeries` object "ImageSeries".
#
# We can also access :py:class:`~pynwb.image.OpticalSeries` data that was added to the NWB File
# as stimuli by indexing ``nwbfile.stimulus`` with the name of the :py:class:`~pynwb.image.OpticalSeries`
# object "StimulusPresentation".
# Data arrays are read passively from the file.
# Accessing the ``data`` attribute of the :py:class:`~pynwb.image.OpticalSeries` object
# does not read the data values into memory, but returns an HDF5 object that can be indexed to read data.
# Use the ``[:]`` operator to read the entire data array into memory.

with NWBHDF5IO(nwbfile_path, "r") as io:
    read_nwbfile = io.read()
    print(read_nwbfile.acquisition["ImageSeries"])
    print(read_nwbfile.stimulus["StimulusPresentation"].data[:])
