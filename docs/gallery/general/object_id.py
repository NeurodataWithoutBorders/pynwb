"""
.. _object_ids:

Object IDs in NWB
=================

This example focuses on how to access object IDs from NWB container objects and NWB container objects by
object ID. Every NWB container object has an object ID that is a UUID_ string, such as
"123e4567-e89b-12d3-a456-426655440000". These IDs have a non-zero probability of being duplicated, but are practically
unique and used widely across computing platforms as if they are unique.

The object ID of an NWB container object can be accessed using the
:py:attr:`~hdmf.container.AbstractContainer.object_id` method.

.. _UUID: https://en.wikipedia.org/wiki/Universally_unique_identifier

"""

from datetime import datetime

import numpy as np
from dateutil.tz import tzlocal

# sphinx_gallery_thumbnail_path = 'figures/gallery_thumbnails_objectid.png'
from pynwb import NWBFile, TimeSeries

# set up the NWBFile
start_time = datetime(2019, 4, 3, 11, tzinfo=tzlocal())
nwbfile = NWBFile(
    session_description="demonstrate NWB object IDs",
    identifier="NWB456",
    session_start_time=start_time,
)

# make some simulated data
timestamps = np.linspace(0, 100, 1024)
data = (
    np.sin(0.333 * timestamps)
    + np.cos(0.1 * timestamps)
    + np.random.randn(len(timestamps))
)
test_ts = TimeSeries(name="raw_timeseries", data=data, unit="m", timestamps=timestamps)

# add it to the NWBFile
nwbfile.add_acquisition(test_ts)

# print the object ID of the NWB file
print(nwbfile.object_id)

# print the object ID of the TimeSeries
print(test_ts.object_id)

####################
# The :py:class:`~pynwb.file.NWBFile` class has the :py:meth:`~pynwb.file.NWBFile.objects` property, which provides a
# dictionary of all neurodata_type objects in the `NWBFile`, indexed by each object's object ID.

print(nwbfile.objects)

####################
# You can iterate through the `objects` dictionary as with any other Python dictionary.

for oid in nwbfile.objects:
    print(nwbfile.objects[oid])

for obj in nwbfile.objects.values():
    print('%s: %s "%s"' % (obj.object_id, obj.neurodata_type, obj.name))

####################
# If you have stored the object ID of a particular NWB container object, you can use it as a key on `NWBFile.objects` to
# get the object.

ts_id = test_ts.object_id
my_ts = nwbfile.objects[ts_id]  # test_ts == my_ts

####################
#
# .. note::
#    It is important to note that the object ID is NOT a unique hash of the data. If the contents of an NWB container
#    change, the object ID remains the same.
#
