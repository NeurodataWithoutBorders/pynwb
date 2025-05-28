from datetime import datetime
from uuid import uuid4

import numpy as np
from dateutil import tz

from pynwb import NWBHDF5IO, NWBFile, TimeSeries


nwbfile = NWBFile(
    session_description="Mouse exploring an open field",  # required
    identifier=str(uuid4()),  # required
    session_start_time=datetime(2018, 4, 25, 2, 30, 3, tzinfo=tz.gettz("US/Pacific")),  # required
    experimenter=[
        "Baggins, Bilbo",
    ],  # optional
 )

waveforms_list = [
    np.array([  # unit 1
        [  # electrode 1
            [1, 2, 3, 4, 5],  # spike time 1 [sample 1, sample 2, ...]
            [2, 3, 4, 5, 6],  # spike time 2
        ],
        [  # electrode 2
            [3, 4, 5, 6, 7],  # spike time 1 [sample 1, sample 2, ...]
            [2, 3, 4, 5, 6],  # spike time 2
        ],
    ]),
    np.array([  # unit 2
        [  # electrode 1
            [10, 20, 30, 40, 50],  # spike time 1 [sample 1, sample 2, ...]
        ],
        [  # electrode 2
            [100, 200, 300, 400, 500],  # spike time 1 [sample 1, sample 2, ...]
        ],
    ]),
]
# mean and sd across spike times
waveform_mean_list = [np.mean(i, axis=1) for i in waveforms_list]
waveform_sd_list = [np.std(i, axis=1) for i in waveforms_list]

electrodes_list = [[1, 2], [3]]
for unit_id in range(2):
    nwbfile.add_unit(
        id=unit_id,
        electrodes=electrodes_list[unit_id],
        waveforms=waveforms_list[unit_id],
        waveform_mean=waveform_mean_list[unit_id],  # does not support different number of electrodes
        waveform_sd=waveform_sd_list[unit_id],  # does not support different number of electrodes
    )

    breakpoint()

with NWBHDF5IO("temp.nwb", "w") as io:
    io.write(nwbfile)
