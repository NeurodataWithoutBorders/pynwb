# -*- coding: utf-8 -*-
'''
.. _ecephys_tutorial:

Intracellular electrophysiology data
============================================

The following examples will reference variables that may not be defined within the block they are used in. For
clarity, we define them here:
'''
from datetime import datetime
from pynwb import NWBFile, NWBHDF5IO, TimeSeries
from pynwb.icephys import IntracellularElectrode, CurrentClampStimulusSeries

filename = 'icephys_example.nwb'

nwbfile = NWBFile(
    source='roundtrip test', session_description='', identifier='',
    session_start_time=datetime.now(), file_create_date=datetime.now())

elec = IntracellularElectrode(
#elec = nwbfile.create_ic_electrode(
    name="elec0", source='', slice='', resistance='', seal='', description='',
    location='', filtering='', initial_access_resistance='', device='')

ccss = CurrentClampStimulusSeries(
    name="ccss", source="command", data=[1,2,3,4,5], unit='A',
    starting_time=123.6, rate=10e3, electrode=elec, gain=0.02)

nwbfile.add_stimulus(ccss)

io = NWBHDF5IO(filename, 'w')
io.write(nwbfile)
io.close()

io = NWBHDF5IO(filename)
nwbfile = io.read()
ccss2 = nwbfile.get_acquisition('ccss')
