from hdmf.term_set import TermSet, TermSetWrapper
from pynwb.resources import HERD
from pynwb import NWBHDF5IO, NWBFile
from glob import glob
from tqdm import tqdm
from dandi.dandiapi import DandiAPIClient
import fsspec
from fsspec.implementations.cached import CachingFileSystem
import h5py
import pynwb
from pynwb.file import Subject

from hdmf.common import VectorData

from datetime import datetime
from dateutil import tz
import yaml

from datetime import datetime
from uuid import uuid4

import numpy as np
from dateutil.tz import tzlocal

from pynwb import NWBHDF5IO, NWBFile, get_type_map
from pynwb.file import ElectrodeTable
from pynwb.ecephys import LFP, ElectricalSeries

from pynwb import unload_termset_config, load_termset_config, get_loaded_config

experimenter_termset = TermSet(term_schema_path='/Users/mavaylon/Research/NWB/pynwb/src/pynwb/config/experimenter_termset.yaml')
location_termset = TermSet(term_schema_path='/Users/mavaylon/Research/NWB/pynwb/src/pynwb/config/location_termset.yaml')
species_termset = TermSet(term_schema_path='/Users/mavaylon/Research/NWB/pynwb/src/pynwb/config/nwb_subject_termset.yaml')

# et = ElectrodeTable()
# breakpoint()
# # tm=get_type_map()
# cc=get_loaded_config()
# breakpoint()
# unload_termset_config()
# cc2=get_loaded_config()
#
load_termset_config()
cc2=get_loaded_config()
breakpoint()
load_termset_config('/Users/mavaylon/Research/NWB/hdmf2/hdmf/tests/unit/test_extension_config.yaml')
cc3=get_loaded_config()

breakpoint()

tm=get_type_map()
location_termset = TermSet(term_schema_path='/Users/mavaylon/Research/NWB/pynwb/docs/gallery/general/location_termset.yaml')


# Example with Electrophys location, with species, with orcid

nwbfile = NWBFile(
    session_description="my first synthetic recording",
    identifier=str(uuid4()),
    session_start_time=datetime.now(tzlocal()),
    experimenter=[
        "Ryan Ly",
    ],
    lab="Bag End Laboratory",
    institution="University of Middle Earth at the Shire",
    experiment_description="I went on an adventure to reclaim vast treasures.",
    session_id="LONELYMTN001",
)

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
        location='Amygdala',
    )
    # add electrodes to the electrode table
    for ielec in range(nchannels_per_shank):
        nwbfile.add_electrode(
            group=electrode_group,
            label="shank{}elec{}".format(ishank, ielec),
            location='Amygdala',
        )
        electrode_counter += 1

nwbfile.electrodes.to_dataframe()
breakpoint()

# Example with Electrophys location, with species, with orcid

# nwbfile = NWBFile(
#     session_description="my first synthetic recording",
#     identifier=str(uuid4()),
#     session_start_time=datetime.now(tzlocal()),
#     experimenter=TermSetWrapper(value=['Oliver Rübel', 'Ryan Ly'], termset=experimenter_termset),
#     lab="Bag End Laboratory",
#     institution="University of Middle Earth at the Shire",
#     experiment_description="I went on an adventure to reclaim vast treasures.",
#     session_id="LONELYMTN001",
# )
#
# subject = Subject(
#     subject_id="01",
#     age="One shouldn't ask",
#     description="A human.",
#     species=TermSetWrapper(value="Homo sapiens", termset=species_termset),
#     sex="M",
# )
#
# nwbfile.subject = subject
# device = nwbfile.create_device(
#     name="array", description="the best array", manufacturer="Probe Company 9000"
# )
#
# nwbfile.add_electrode_column(name="label", description="label of electrode")
#
# nshanks = 4
# nchannels_per_shank = 3
# electrode_counter = 0
#
# for ishank in range(nshanks):
#     # create an electrode group for this shank
#     electrode_group = nwbfile.create_electrode_group(
#         name="shank{}".format(ishank),
#         description="electrode group for shank {}".format(ishank),
#         device=device,
#         location=TermSetWrapper(value='Amygdala', termset=location_termset),
#     )
#     # add electrodes to the electrode table
#     for ielec in range(nchannels_per_shank):
#         nwbfile.add_electrode(
#             group=electrode_group,
#             label="shank{}elec{}".format(ishank, ielec),
#             location='Amygdala'
#         )
#         electrode_counter += 1
# breakpoint()
# with NWBHDF5IO("basics_tutorial.nwb",herd_path='./HERD.zip', mode= "w") as io:
#     io.write(nwbfile)
#
# # Automatically writes HERD using TermSetWrapper as the flag.
# with NWBHDF5IO("basics_tutorial.nwb",herd_path='HERD.zip', mode="r") as io:
#     read_nwbfile = io.read()
