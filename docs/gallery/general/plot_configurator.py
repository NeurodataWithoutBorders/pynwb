from datetime import datetime
from uuid import uuid4
from hdmf.term_set import TermSetWrapper, TermSet

import numpy as np
from dateutil import tz

from pynwb import NWBHDF5IO, NWBFile, TimeSeries
from pynwb.behavior import Position, SpatialSeries
from pynwb.epoch import TimeIntervals
from pynwb.file import Subject
from pynwb import unload_termset_config, load_termset_config


session_start_time = datetime(2018, 4, 25, 2, 30, 3, tzinfo=tz.gettz("US/Pacific"))
terms = TermSet(term_schema_path='/Users/mavaylon/Research/NWB/hdmf2/hdmf/docs/gallery/example_term_set.yaml')
#
nwbfile = NWBFile(
    session_description="Mouse exploring an open field",  # required
    identifier=str(uuid4()),  # required
    session_start_time=session_start_time,  # required
    session_id="session_1234",  # optional
    experimenter=[
        "Ryan Ly",
    ],  # optional
    lab="Bag End Laboratory",  # optional
    institution="University of My Institution",  # optional
    experiment_description="I went on an adventure to reclaim vast treasures.",  # optional
    related_publications="DOI:10.1016/j.neuron.2016.12.011",  # optional
)
subject = Subject(
    subject_id="01",
    age="One shouldn't ask",
    description="A human.",
    species="Homo sapiens",
    sex="M",
)

nwbfile.subject = subject

device = nwbfile.create_device(
    name="array", description="the best array", manufacturer="Probe Company 9000"
)

nwbfile.add_electrode_column(name="label", description="label of electrode")

nshanks = 4
nchannels_per_shank = 3
electrode_counter = 0

for ishank in range(nshanks):
    # create an electrode group for this shank
    electrode_group = nwbfile.create_electrode_group(
        name="shank{}".format(ishank),
        description="electrode group for shank {}".format(ishank),
        device=device,
        location='Amygdala'
    )
    # add electrodes to the electrode table
    for ielec in range(nchannels_per_shank):
        nwbfile.add_electrode(
            group=electrode_group,
            label="shank{}elec{}".format(ishank, ielec),
            location='Amygdala'
        )
        electrode_counter += 1

breakpoint()
# # nwbfile.subject = subject
# # breakpoint()
# unload_termset_config()
# load_termset_config()
#
# nwbfile = NWBFile(
#     session_description="Mouse exploring an open field",  # required
#     identifier=str(uuid4()),  # required
#     session_start_time=session_start_time,  # required
#     session_id="session_1234",  # optional
#     experimenter=[
#         "Ryan Ly",
#     ],  # optional
#     lab="Bag End Laboratory",  # optional
#     institution="University of My Institution",  # optional
#     experiment_description="I went on an adventure to reclaim vast treasures.",  # optional
#     related_publications="DOI:10.1016/j.neuron.2016.12.011",  # optional
# )
#
#
# subject = Subject(
#     subject_id="001",
#     age="P90D",
#     description="mouse 5",
#     species="Mus musculus",
#     sex="M",
# )
# breakpoint()
