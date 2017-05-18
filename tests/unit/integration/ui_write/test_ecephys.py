import unittest
import numpy as np
import json
from datetime import datetime
import os

from form.build import GroupBuilder, DatasetBuilder, LinkBuilder

from pynwb.ecephys import Device, ElectrodeGroup, ElectricalSeries, SpikeEventSeries

from . import base

class TestElectrodeGroup(base.TestNWBContainerIO):

    def setUpContainer(self):
        dev1 = Device('dev1')
        channel_description = ['ch1', 'ch2']
        channel_location = ['lo1', 'lo2']
        channel_filtering = ['fi1', 'fi2']
        channel_coordinates = ['co1', 'co2']
        channel_impedance = ['im1', 'im2']
        self.container = ElectrodeGroup('elec1',
                                        channel_description,
                                        channel_location,
                                        channel_filtering,
                                        channel_coordinates,
                                        channel_impedance,
                                        'desc1',
                                        'loc1',
                                        dev1)

    def setUpBuilder(self):
        device_builder = GroupBuilder('dev1',
                            attributes={'neurodata_type': 'Device', 'namespace': 'core'},
                         )
        self.builder = GroupBuilder('elec1',
                            attributes={'neurodata_type': 'ElectrodeGroup', 'namespace': 'core'},
                            datasets={
                                'channel_description': DatasetBuilder('channel_description', ['ch1', 'ch2']),
                                'channel_location': DatasetBuilder('channel_location', ['lo1', 'lo2']),
                                'channel_filtering': DatasetBuilder('channel_filtering', ['fi1', 'fi2']),
                                'channel_coordinates': DatasetBuilder('channel_coordinates', ['co1', 'co2']),
                                'channel_impedance': DatasetBuilder('channel_impedance', ['im1', 'im2']),
                                'description': DatasetBuilder('description', 'desc1'),
                                'location': DatasetBuilder('location', 'loc1')
                            },
                            links={
                                'device': LinkBuilder('device', device_builder)
                            }
                        )


@unittest.skip('skipping for now')
class TestElectricalSeriesIO(base.TestNWBContainerIO):

    def setUpContainer(self):
        dev1 = Device('dev1')
        channel_description = ('ch1', 'ch2')
        channel_location = ('lo1', 'lo2')
        channel_filtering = ('fi1', 'fi2')
        channel_coordinates = ('co1', 'co2')
        channel_impedance = ('im1', 'im2')
        elec1 = ElectrodeGroup('elec1', channel_description, channel_location, channel_filtering, channel_coordinates, channel_impedance, 'desc1', 'loc1', dev1)
        data = [
            list(range(10)),
            list(range(10, 20)),
        ]
        timestamps = list(map(lambda x: x/10, range(10)))
        self.container = ElectricalSeries('test_eS', 'a hypothetical source', data, elec1, timestamps=timestamps)

    def setUpBuilder(self):
        device_builder = GroupBuilder('dev1',
                            attributes={'neurodata_type': 'Device', 'namespace': 'core'},
                         )
        elcgrp_builder = GroupBuilder('elec1',
                            attributes={'neurodata_type': 'ElectrodeGroup', 'namespace': 'core'},
                            datasets={
                                'channel_description': DatasetBuilder('channel_description', ['ch1', 'ch2']),
                                'channel_location': DatasetBuilder('channel_location', ['lo1', 'lo2']),
                                'channel_filtering': DatasetBuilder('channel_filtering', ['fi1', 'fi2']),
                                'channel_coordinates': DatasetBuilder('channel_coordinates', ['co1', 'co2']),
                                'channel_impedance': DatasetBuilder('channel_impedance', ['im1', 'im2']),
                                'description': DatasetBuilder('description', 'desc1'),
                                'location': DatasetBuilder('location', 'loc1')
                            },
                            links={
                                'device': LinkBuilder('device', device_builder)
                            }
                        )
        data = [
            list(range(10)),
            list(range(10, 20)),
        ]
        timestamps = list(map(lambda x: x/10, range(10)))
        self.builder = GroupBuilder('test_eS',
                                attributes={'ancestry': 'TimeSeries',
                                            'source': 'a hypothetical source',
                                            'namespace': base.CORE_NAMESPACE,
                                            'neurodata_type': 'ElectricalSeries',
                                            'help': 'General purpose TimeSeries'},
                                datasets={'data': DatasetBuilder('data', data,
                                                                 attributes={'unit': 'volt',
                                                                             'conversion': 1.0,
                                                                             'resolution': np.nan}),
                                          'timestamps': DatasetBuilder('timestamps', timestamps,
                                                                 attributes={'unit': 'Seconds', 'interval': 1})},
                                links={'electrode_group': LinkBuilder('electrode_group', elcgrp_builder)})

