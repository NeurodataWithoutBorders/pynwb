from datetime import datetime
from uuid import uuid4
from hdmf.common import HERD

import numpy as np
from dateutil import tz

from pynwb import NWBHDF5IO, NWBFile, TimeSeries
from pynwb.behavior import Position, SpatialSeries
from pynwb.file import Subject
from pynwb.misc import AnnotationSeries

session_start_time = datetime(2018, 4, 25, 2, 30, 3, tzinfo=tz.gettz("US/Pacific"))

nwbfile = NWBFile(
    session_description="Mouse exploring an open field",  # required
    identifier=str(uuid4()),  # required
    session_start_time=session_start_time,  # required
    session_id="session_1234",  # optional
    experimenter=[
        "Baggins, Bilbo",
    ],  # optional
    lab="Bag End Laboratory",  # optional
    institution="University of Middle Earth at the Shire",  # optional
    experiment_description="I went on an adventure to reclaim vast treasures.",  # optional
    keywords=["behavior", "exploration", "wanderlust"],  # optional
    related_publications="doi:10.1016/j.neuron.2016.12.011",  # optional
)

subject = Subject(
    subject_id="001",
    age="P90D",
    description="mouse 5",
    species="Mus musculus",
    sex="M",
)

nwbfile.subject = subject


herd = HERD()
nwbfile.external_resources = herd

nwbfile.external_resources.add_ref(container=nwbfile.subject,
                          key=nwbfile.subject.species,
                          entity_id="sadf",
                          entity_uri='asdf')
breakpoint()
io = NWBHDF5IO("basics_tutorial.nwb", mode="w")
io.write(nwbfile)
io.close()


import h5py

# Open the file
f= h5py.File('basics_tutorial.nwb', 'r')
breakpoint()


with NWBHDF5IO("basics_tutorial.nwb", "r") as io:
    read_nwbfile = io.read()
    read_nwbfile.external_resources
breakpoint()
