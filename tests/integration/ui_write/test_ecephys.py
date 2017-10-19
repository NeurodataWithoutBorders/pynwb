import unittest2 as unittest
import numpy as np
import json
from datetime import datetime
import os

from form.build import GroupBuilder, DatasetBuilder, LinkBuilder, RegionBuilder

from pynwb.ecephys import *

from . import base

class TestElectrodeGroupIO(base.TestMapRoundTrip):

    def setUpContainer(self):
        self.dev1 = Device('dev1', 'a test source')
        return ElectrodeGroup('elec1', 'a test source',
                                        'desc1',
                                        'loc1',
                                        self.dev1)

    def setUpBuilder(self):
        device_builder = GroupBuilder('dev1',
                            attributes={'neurodata_type': 'Device',
                                        'namespace': 'core',
                                        'help': 'A recording device e.g. amplifier',
                                        'source': 'a test source'},
                         )
        return GroupBuilder('elec1',
                            attributes={'neurodata_type': 'ElectrodeGroup',
                                        'namespace': 'core',
                                        'help': 'A physical grouping of channels',
                                        'source': 'a test source'},
                            datasets={
                                'description': DatasetBuilder('description', 'desc1'),
                                'location': DatasetBuilder('location', 'loc1')
                            },
                            links={
                                'device': LinkBuilder('device', device_builder)
                            }
                        )

    def addContainer(self, nwbfile):
        ''' Should take an NWBFile object and add the container to it '''
        nwbfile.set_device(self.dev1)
        nwbfile.set_electrode_group(self.container)

    def getContainer(self, nwbfile):
        ''' Should take an NWBFile object and return the Container'''
        return nwbfile.get_electrode_group(self.container.name)

def make_electrode_table(self):
    self.table = ElectrodeTable('electrodes')
    self.dev1 = Device('dev1', 'a test source')
    self.group = ElectrodeGroup('tetrode1', 'a test source', 'tetrode description', 'tetrode location', self.dev1)
    self.table.add_row(1, 1.0, 2.0, 3.0, -1.0, 'CA1', 'none', 'first channel of tetrode', self.group)
    self.table.add_row(2, 1.0, 2.0, 3.0, -2.0, 'CA1', 'none', 'second channel of tetrode', self.group)
    self.table.add_row(3, 1.0, 2.0, 3.0, -3.0, 'CA1', 'none', 'third channel of tetrode', self.group)
    self.table.add_row(4, 1.0, 2.0, 3.0, -4.0, 'CA1', 'none', 'fourth channel of tetrode', self.group)

class TestElectricalSeriesIO(base.TestMapRoundTrip):

    def setUpContainer(self):
        make_electrode_table(self)
        region = ElectrodeTableRegion(self.table, [0,2], 'the first and third electrodes')
        data = list(zip(range(10), range(10, 20)))
        timestamps = list(map(lambda x: x/10, range(10)))
        ret = ElectricalSeries('test_eS', 'a hypothetical source', data, region, timestamps=timestamps)
        return ret

    def setUpBuilder(self):
        #TODO: This needs to be updated
        device_builder = GroupBuilder('dev1',
                            attributes={'neurodata_type': 'Device',
                                        'namespace': 'core',
                                        'help': 'A recording device e.g. amplifier',
                                        'source': 'a test source'},
                         )
        #TODO: this needs to be made into a DatasetBuilder that represents the ElectrodeTable
        #group_builder = GroupBuilder('elec1',
        #                    attributes={'neurodata_type': 'ElectrodeGroup',
        #                                'namespace': 'core',
        #                                'help': 'A physical grouping of channels',
        #                                'source': 'a test source'},
        #                    datasets={
        #                        'description': DatasetBuilder('description', 'desc1'),
        #                        'location': DatasetBuilder('location', 'loc1'),
        #                    },
        #                    links={
        #                        'device': LinkBuilder('device', device_builder)
        #                    }
        #                )

        table_builder = DatasetBuilder('electrodes', self.table.data,
                             attributes={'neurodata_type': 'ElectrodeTable',
                                         'namespace': 'core',
                                         'help': 'a table for storing data about extracellular electrodes'})
        data = list(zip(range(10), range(10, 20)))
        timestamps = list(map(lambda x: x/10, range(10)))
        return GroupBuilder('test_eS',
                                attributes={'source': 'a hypothetical source',
                                            'namespace': base.CORE_NAMESPACE,
                                            'comments': 'no comments',
                                            'description': 'no description',
                                            'neurodata_type': 'ElectricalSeries',
                                            'help': 'Stores acquired voltage data from extracellular recordings'},
                                datasets={'data': DatasetBuilder('data', data,
                                                                 attributes={'unit': 'volt',
                                                                             'conversion': 1.0,
                                                                             'resolution': 0.0}),
                                          'timestamps': DatasetBuilder('timestamps', timestamps,
                                                                 attributes={'unit': 'Seconds', 'interval': 1}),
                                          'electrodes': RegionBuilder('electrodes', [0,2], table_builder,
                                                                      attributes={'neurodata_type': 'ElectrodeTableRegion',
                                                                                  'namespace': 'core',
                                                                                  'description': 'the first and third electrodes',
                                                                                  'help': 'a subset (i.e. slice or region) of an ElectrodeTable'})
                                          })

    def addContainer(self, nwbfile):
        ''' Should take an NWBFile object and add the container to it '''
        #TODO: this might need to do somethign to add the electrode table
        nwbfile.set_device(self.dev1)
        nwbfile.set_electrode_group(self.group)
        nwbfile.set_electrode_table(self.table)
        nwbfile.add_acquisition(self.container)

    def getContainer(self, nwbfile):
        ''' Should take an NWBFile object and return the Container'''
        return nwbfile.get_acquisition(self.container.name)


class TestClusteringIO(base.TestMapRoundTrip):

    def setUpBuilder(self):
        return GroupBuilder('Clustering',
            attributes={
               'help': 'Clustered spike data, whether from automatic clustering tools (eg, klustakwik) or as a result of manual sorting',
               'source': "an example source for Clustering",
               'neurodata_type': 'Clustering',
               'namespace': base.CORE_NAMESPACE},
            datasets={
               'num': DatasetBuilder('num', [0, 1, 2, 0, 1, 2]),
               'times': DatasetBuilder('times', list(range(10,61,10))),
               'peak_over_rms': DatasetBuilder('peak_over_rms', [100, 101, 102]),
               'description': DatasetBuilder('description', "A fake Clustering interface")}
        )

    def setUpContainer(self):
        return Clustering("an example source for Clustering", "A fake Clustering interface", [0, 1, 2, 0, 1, 2], [100, 101, 102], list(range(10,61,10)))
