from datetime import datetime
from uuid import uuid4

import numpy as np
from dateutil.tz import tzlocal
from hdmf.common import VectorData

from pynwb import NWBHDF5IO, NWBFile
from pynwb.ecephys import LFP, ElectricalSeries, ElectrodeGroup, ElectrodesTable

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

device = nwbfile.create_device(
    name="array", description="the best array", manufacturer="Probe Company 9000"
)

group = ElectrodeGroup( name='foo',
        description="electrode group",
        device=device,
        location="brain area",)
# location_col = VectorData(name='location', description='foo', data=['brain area'])
# group_col = VectorData(name='groups', description='foo', data=[group])

table = ElectrodesTable()
nwbfile.electrodes = table
nwbfile.add_electrode_group(group)
nwbfile.add_electrode(group=group, location='brain')
# breakpoint()
# nwbfile.add_electrode_column(name="label", description="label of electrode")

# nshanks = 4
# nchannels_per_shank = 3
# electrode_counter = 0
# #
# for ishank in range(nshanks):
#     # create an electrode group for this shank
#     electrode_group = nwbfile.create_electrode_group(
#         name="shank{}".format(ishank),
#         description="electrode group for shank {}".format(ishank),
#         device=device,
#         location="brain area",
#     )
#     # add electrodes to the electrode table
#     for ielec in range(nchannels_per_shank):
#         nwbfile.add_electrode(
#             group=electrode_group,
#             label="shank{}elec{}".format(ishank, ielec),
#             location="brain area",
#         )
#         electrode_counter += 1
# breakpoint()
# with NWBHDF5IO("ecephys_tutorial.nwb", "w") as io:
#     io.write(nwbfile)
io= NWBHDF5IO("/Users/mavaylon/Research/NWB/pynwb/tests/back_compat/2.6.0_DynamicTableElectrodes.nwb", "r")
read_nwbfile = io.read()
breakpoint()
