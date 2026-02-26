# -*- coding: utf-8 -*-
"""
Optogenetics
============


This tutorial will demonstrate how to write optogenetics data.

Creating an NWBFile object
--------------------------

When creating a NWB file, the first step is to create the :py:class:`~pynwb.file.NWBFile` object.
"""

# sphinx_gallery_thumbnail_path = 'figures/gallery_thumbnails_ogen.png'
from datetime import datetime
from uuid import uuid4

from dateutil.tz import tzlocal

from pynwb import NWBFile

nwbfile = NWBFile(
    session_description="my first synthetic recording",
    identifier=str(uuid4()),
    session_start_time=datetime.now(tzlocal()),
    experimenter="Baggins, Bilbo",
    lab="Bag End Laboratory",
    institution="University of Middle Earth at the Shire",
    experiment_description="I went on an adventure to reclaim vast treasures.",
    session_id="LONELYMTN",
)

####################
# Adding optogenetic data
# -----------------------
# The :py:mod:`~pynwb.ogen` module contains two data types that you will need to write optogenetics data,
# :py:class:`~pynwb.ogen.OptogeneticStimulusSite`, which contains metadata about the stimulus site, and
# :py:class:`~pynwb.ogen.OptogeneticSeries`, which contains the power applied by the laser over time, in watts.
#
# In pynwb, device-related metadata is split into two levels:
# :py:class:`~pynwb.device.DeviceModel` stores metadata shared across devices of the same type (e.g., manufacturer,
# model number), while :py:class:`~pynwb.device.Device` represents the specific physical device used in an
# experiment.
#
# First, you need to create a :py:class:`~pynwb.device.Device` object linked to the :py:class:`~pynwb.file.NWBFile`
# to represent the optogenetic stimulation system. It is recommended to add as much metadata about the
# system/device as possible to inform others using the data. A :py:class:`~pynwb.device.Device` object has
# an optional ``model`` field that points to a :py:class:`~pynwb.device.DeviceModel` object, which stores
# information about the device model. This can be useful when searching a set of NWB files or a data archive
# for all files that use a specific device model, or expressing that multiple devices in a session use the
# same device model. The fields ``description`` and ``model_number`` for
# :py:class:`~pynwb.device.DeviceModel` and the fields ``description``, ``model``, and ``serial_number`` for
# :py:class:`~pynwb.device.Device` are optional, but recommended. ``DeviceModel.manufacturer`` is required.
device_model = nwbfile.create_device_model(
    name="Thorlabs M470F3 Model",
    description="470nm fiber-coupled LED, 17.2mW output for channelrhodopsin activation",
    manufacturer="Thorlabs",
    model_number="M470F3",
)

device = nwbfile.create_device(
    name="Thorlabs M470F3",
    description="470nm fiber-coupled LED used for optogenetic stimulation",
    model=device_model,
    serial_number="SN-00123456",
)

####################
# Now, you can create an :py:class:`~pynwb.ogen.OptogeneticStimulusSite`. The easiest way to do this is to use the
# :py:meth:`~pynwb.file.NWBFile.create_ogen_site` method.

ogen_site = nwbfile.create_ogen_site(
    name="OptogeneticStimulusSite",
    device=device,
    description="This is an example optogenetic site.",
    excitation_lambda=600.0,  # nm
    location="VISrl",
)


####################
# Another equivalent approach would be to create a :py:class:`~pynwb.ogen.OptogeneticStimulusSite` and then add it to
# the :py:class:`~pynwb.file.NWBFile`:

from pynwb.ogen import OptogeneticStimulusSite

ogen_stim_site = OptogeneticStimulusSite(
    name="OptogeneticStimulusSite2",
    device=device,
    description="This is an example optogenetic site.",
    excitation_lambda=600.0,  # nm
    location="VISrl",
)

nwbfile.add_ogen_site(ogen_stim_site)

####################
# The second approach is necessary if you have an extension of :py:class:`~pynwb.ogen.OptogeneticStimulusSite`.
#
# With the :py:class:`~pynwb.ogen.OptogeneticStimulusSite` added, you can now create a
# :py:class:`~pynwb.ogen.OptogeneticSeries`. Here, we will generate some random data using numpy and specify the
# timing using ``rate``. By default, the starting time of the time series is the session start time, specified in
# :py:class:`~pynwb.file.NWBFile`.
# If you have samples at irregular intervals, you should use ``timestamps`` instead.

import numpy as np

from pynwb.ogen import OptogeneticSeries

ogen_series = OptogeneticSeries(
    name="OptogeneticSeries",
    data=np.random.randn(20),  # watts
    site=ogen_site,
    rate=30.0,  # Hz
)

nwbfile.add_stimulus(ogen_series)
