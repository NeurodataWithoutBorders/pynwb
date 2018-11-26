from pynwb.form.build import GroupBuilder, LinkBuilder, ReferenceBuilder, DatasetBuilder
from pynwb import NWBFile
from pynwb.icephys import (IntracellularElectrode, PatchClampSeries, CurrentClampStimulusSeries,
                           SweepTable,
                           VoltageClampStimulusSeries, CurrentClampSeries,
                           VoltageClampSeries, IZeroClampSeries)
from pynwb.device import Device

from . import base

from abc import ABCMeta
from six import with_metaclass


class TestIntracellularElectrode(base.TestMapRoundTrip):

    def setUpContainer(self):
        self.device = Device(name='device_name')
        self.elec = IntracellularElectrode(name="elec0", slice='tissue slice',
                                           resistance='something measured in ohms',
                                           seal='sealing method', description='a fake electrode object',
                                           location='Springfield Elementary School',
                                           filtering='a meaningless free-form text field',
                                           initial_access_resistance='I guess this changes',
                                           device=self.device)
        return self.elec

    def setUpBuilder(self):
        device = GroupBuilder('device_name',
                              attributes={'help': 'A recording device e.g. amplifier',
                                          'namespace': 'core',
                                          'neurodata_type': 'Device'})
        datasets = [
            DatasetBuilder('slice', data=u'tissue slice'),
            DatasetBuilder('resistance', data=u'something measured in ohms'),
            DatasetBuilder('seal', data=u'sealing method'),
            DatasetBuilder('description', data=u'a fake electrode object'),
            DatasetBuilder('location', data=u'Springfield Elementary School'),
            DatasetBuilder('filtering', data=u'a meaningless free-form text field'),
            DatasetBuilder('initial_access_resistance', data=u'I guess this changes'),
        ]
        elec = GroupBuilder('elec0',
                            attributes={'help': 'Metadata about an intracellular electrode',
                                        'namespace': 'core',
                                        'neurodata_type': 'IntracellularElectrode',
                                        },
                            datasets={d.name: d for d in datasets},
                            links={
                                'device': LinkBuilder(device, 'device')
                            })
        return elec

    def addContainer(self, nwbfile):
        ''' Should take an NWBFile object and add the container to it '''
        nwbfile.add_ic_electrode(self.elec)
        nwbfile.add_device(self.device)

    def getContainer(self, nwbfile):
        ''' Should take an NWBFile object and return the Container'''
        return nwbfile.get_ic_electrode(self.container.name)


class TestPatchClampSeries(with_metaclass(ABCMeta, base.TestDataInterfaceIO)):

    def setUpElectrode(self):

        self.device = Device(name='device_name')
        self.elec = IntracellularElectrode(name="elec0", slice='tissue slice',
                                           resistance='something measured in ohms',
                                           seal='sealing method', description='a fake electrode object',
                                           location='Springfield Elementary School',
                                           filtering='a meaningless free-form text field',
                                           initial_access_resistance='I guess this changes',
                                           device=self.device)

    def addContainer(self, nwbfile):
        ''' Should take an NWBFile object and add the container to it '''
        nwbfile.add_ic_electrode(self.elec)
        nwbfile.add_device(self.device)
        super(TestPatchClampSeries, self).addContainer(nwbfile)

    def setUpContainer(self):
        self.setUpElectrode()
        return PatchClampSeries(name="pcs", data=[1, 2, 3, 4, 5], unit='A',
                                starting_time=123.6, rate=10e3, electrode=self.elec, gain=0.126,
                                stimulus_description="gotcha ya!", sweep_number=4711)


class TestCurrentClampStimulusSeries(TestPatchClampSeries):

    def setUpContainer(self):
        self.setUpElectrode()
        return CurrentClampStimulusSeries(name="ccss", data=[1, 2, 3, 4, 5], unit='A',
                                          starting_time=123.6, rate=10e3, electrode=self.elec, gain=0.126)


class TestVoltageClampStimulusSeries(TestPatchClampSeries):

    def setUpContainer(self):
        self.setUpElectrode()
        return VoltageClampStimulusSeries(name="vcss", data=[1, 2, 3, 4, 5], unit='A',
                                          starting_time=123.6, rate=10e3, electrode=self.elec, gain=0.126)


class TestCurrentClampSeries(TestPatchClampSeries):

    def setUpContainer(self):
        self.setUpElectrode()
        return CurrentClampSeries(name="ccs", data=[1, 2, 3, 4, 5], unit='A',
                                  starting_time=123.6, rate=10e3, electrode=self.elec, gain=0.126,
                                  bias_current=1.2, bridge_balance=2.3, capacitance_compensation=3.45)


class TestVoltageClampSeries(TestPatchClampSeries):

    def setUpContainer(self):
        self.setUpElectrode()
        return VoltageClampSeries(name="vcs", data=[1, 2, 3, 4, 5], unit='A',
                                  starting_time=123.6, rate=10e3, electrode=self.elec,
                                  gain=0.126, capacitance_fast=1.2, capacitance_slow=2.3,
                                  resistance_comp_bandwidth=3.45, resistance_comp_correction=4.5,
                                  resistance_comp_prediction=5.678, whole_cell_capacitance_comp=6.789,
                                  whole_cell_series_resistance_comp=0.7)


class TestIZeroClampSeries(TestPatchClampSeries):

    def setUpContainer(self):
        self.setUpElectrode()
        return IZeroClampSeries(name="izcs", data=[1, 2, 3, 4, 5], unit='A',
                                starting_time=123.6, rate=10e3, electrode=self.elec, gain=0.126,
                                bias_current=1.2, bridge_balance=2.3, capacitance_compensation=3.45)


class TestSweepTableRoundTripEasy(base.TestMapRoundTrip):

    _required_tests = ('test_container', 'test_build', 'test_construct', 'test_roundtrip')

    def setUpContainer(self):
        self.setUpSweepTable()
        return self.sweep_table

    def setUpSweepTable(self):
        self.device = Device(name='device_name')
        self.elec = IntracellularElectrode(name="elec0", slice='tissue slice',
                                           resistance='something measured in ohms',
                                           seal='sealing method', description='a fake electrode object',
                                           location='Springfield Elementary School',
                                           filtering='a meaningless free-form text field',
                                           initial_access_resistance='I guess this changes',
                                           device=self.device)
        self.pcs = PatchClampSeries(name="pcs", data=[1, 2, 3, 4, 5], unit='A',
                                    starting_time=123.6, rate=10e3, electrode=self.elec, gain=0.126,
                                    stimulus_description="gotcha ya!", sweep_number=4711)
        self.sweep_table = SweepTable(name='sweep_table')
        self.sweep_table.add_entry(self.pcs)

    def addContainer(self, nwbfile):
        nwbfile.add_device(self.device)
        nwbfile.add_ic_electrode(self.elec)
        nwbfile.add_acquisition(self.pcs)

    def test_container(self):
        description = 'a file to test writing and reading a %s' % self.container_type
        identifier = 'TEST_%s' % self.container_type
        nwbfile = NWBFile(description, identifier, self.start_time, file_create_date=self.create_date)
        self.addContainer(nwbfile)

        sweep_table = self.getContainer(nwbfile)
        self.assertEqual(len(sweep_table['series'].data), 1)
        self.assertEqual(sweep_table.id[0], 0)
        self.assertEqual(sweep_table['sweep_number'].data[0], 4711)

    def getContainer(self, nwbfile):
        ''' Should take an NWBFile object and return the Container'''
        return nwbfile.sweep_table

    def setUpBuilder(self):
        device = GroupBuilder('device_name',
                              attributes={'neurodata_type': 'Device',
                                          'help': 'A recording device e.g. amplifier',
                                          'namespace': 'core',
                                          })
        datasets = [
            DatasetBuilder('slice', data=u'tissue slice'),
            DatasetBuilder('resistance', data=u'something measured in ohms'),
            DatasetBuilder('seal', data=u'sealing method'),
            DatasetBuilder('description', data=u'a fake electrode object'),
            DatasetBuilder('location', data=u'Springfield Elementary School'),
            DatasetBuilder('filtering', data=u'a meaningless free-form text field'),
            DatasetBuilder('initial_access_resistance', data=u'I guess this changes'),
        ]
        elec = GroupBuilder('elec0',
                            attributes={'help': 'Metadata about an intracellular electrode',
                                        'namespace': 'core',
                                        'neurodata_type': 'IntracellularElectrode',
                                        },
                            datasets={d.name: d for d in datasets},
                            links={
                                'device': LinkBuilder(device, 'device')
                            })
        datasets = [
            DatasetBuilder('gain',
                           data=0.126,
                           attributes={},
                           ),
            DatasetBuilder('data',
                           data=[1, 2, 3, 4, 5],
                           attributes={'conversion': 1.0,
                                       'resolution': 0.0,
                                       'unit': u'A',
                                       }
                           ),
            DatasetBuilder('starting_time',
                           data=123.6,
                           attributes={'rate': 10000.0,
                                       'unit': 'Seconds',
                                       }
                           ),
                ]
        pcs = GroupBuilder('pcs',
                           attributes={'neurodata_type': 'PatchClampSeries',
                                       'namespace': 'core',
                                       'comments': u'no comments',
                                       'help': 'Superclass definition for patch-clamp data',
                                       'description': u'no description',
                                       'stimulus_description': u'gotcha ya!',
                                       'sweep_number': 4711
                                       },
                           links={'electrode': LinkBuilder(elec, 'electrode')},
                           datasets={d.name: d for d in datasets},
                           )

        column_id = DatasetBuilder('id', [0],
                                   attributes={'neurodata_type': 'ElementIdentifiers',
                                               'namespace': 'core',
                                               'help': 'unique identifiers for a list of elements',
                                               }
                                   )

        column_series = DatasetBuilder('series',
                                       attributes={'neurodata_type': 'VectorData',
                                                   'namespace': 'core',
                                                   'help': 'Values for a list of elements',
                                                   'description': u'PatchClampSeries with the same sweep number',
                                                   },
                                       data=[LinkBuilder(pcs)]
                                       )

        column_index = DatasetBuilder('series_index', [1],
                                      attributes={'neurodata_type': 'VectorIndex',
                                                  'namespace': 'core',
                                                  'help': 'indexes into a list of values for a list of elements',
                                                  'target': ReferenceBuilder(column_series),
                                                  },
                                      )

        column_sweep_number = DatasetBuilder('sweep_number', data=[4711],
                                             attributes={'neurodata_type': 'VectorData',
                                                         'namespace': 'core',
                                                         'help': 'Values for a list of elements',
                                                         'description': u'Sweep number of the entries in that row',
                                                         }
                                             )

        columns = [column_id, column_series, column_index, column_sweep_number]
        sweep_table = GroupBuilder('sweep_table', datasets={c.name: c for c in columns},
                                   attributes={'neurodata_type': 'SweepTable',
                                               'namespace': 'core',
                                               'colnames': ('series',
                                                            'sweep_number'),
                                               'help': 'The table which groups different PatchClampSeries together',
                                               'description':
                                               u'A sweep table groups different PatchClampSeries together.',
                                               },
                                   )

        return sweep_table


class TestSweepTableRoundTripComplicated(base.TestMapRoundTrip):

    _required_tests = ('test_container', 'test_build', 'test_construct', 'test_roundtrip')

    def setUpContainer(self):
        self.setUpSweepTable()
        return self.sweep_table

    def setUpSweepTable(self):
        self.device = Device(name='device_name')
        self.elec = IntracellularElectrode(name="elec0", slice='tissue slice',
                                           resistance='something measured in ohms',
                                           seal='sealing method', description='a fake electrode object',
                                           location='Springfield Elementary School',
                                           filtering='a meaningless free-form text field',
                                           initial_access_resistance='I guess this changes',
                                           device=self.device)
        self.pcs1 = PatchClampSeries(name="pcs1", data=[1, 2, 3, 4, 5], unit='A',
                                     starting_time=123.6, rate=10e3, electrode=self.elec, gain=0.126,
                                     stimulus_description="gotcha ya!", sweep_number=4711)
        self.pcs2a = PatchClampSeries(name="pcs2a", data=[1, 2, 3, 4, 5], unit='A',
                                      starting_time=123.6, rate=10e3, electrode=self.elec, gain=0.126,
                                      stimulus_description="gotcha ya!", sweep_number=4712)
        self.pcs2b = PatchClampSeries(name="pcs2b", data=[1, 2, 3, 4, 5], unit='A',
                                      starting_time=123.6, rate=10e3, electrode=self.elec, gain=0.126,
                                      stimulus_description="gotcha ya!", sweep_number=4712)

        self.sweep_table = SweepTable(name='sweep_table')
        self.sweep_table.add_entry(self.pcs1)
        self.sweep_table.add_entry(self.pcs2a)
        self.sweep_table.add_entry(self.pcs2b)

    def addContainer(self, nwbfile):
        ''' Should take an NWBFile object and add the SweepTable container to it '''
        nwbfile.add_device(self.device)
        nwbfile.add_ic_electrode(self.elec)

        nwbfile.add_acquisition(self.pcs1)
        nwbfile.add_stimulus_template(self.pcs2a)
        nwbfile.add_stimulus(self.pcs2b)

    def test_container(self):
        description = 'a file to test writing and reading a %s' % self.container_type
        identifier = 'TEST_%s' % self.container_type
        nwbfile = NWBFile(description, identifier, self.start_time, file_create_date=self.create_date)
        self.addContainer(nwbfile)

        sweep_table = self.getContainer(nwbfile)

        self.assertEqual(len(sweep_table['series'].data), 3)
        self.assertEqual(sweep_table['sweep_number'].data[0], 4711)
        self.assertEqual(sweep_table['sweep_number'].data[1], 4712)
        self.assertEqual(sweep_table['sweep_number'].data[2], 4712)

        series = sweep_table.get_series(4711)
        self.assertEqual(len(series), 1)
        names = [elem.name for elem in series]
        self.assertEqual(names, ["pcs1"])
        sweep_numbers = [elem.sweep_number for elem in series]
        self.assertEqual(sweep_numbers, [4711])

        series = sweep_table.get_series(4712)
        self.assertEqual(len(series), 2)
        names = [elem.name for elem in series]
        self.assertEqual(names, ["pcs2a", "pcs2b"])
        sweep_numbers = [elem.sweep_number for elem in series]
        self.assertEqual(sweep_numbers, [4712, 4712])

    def getContainer(self, nwbfile):
        return nwbfile.sweep_table

    def setUpBuilder(self):
        device = GroupBuilder('device_name',
                              attributes={'neurodata_type': 'Device',
                                          'help': 'A recording device e.g. amplifier',
                                          'namespace': 'core',
                                          })

        datasets = [
            DatasetBuilder('slice', data=u'tissue slice'),
            DatasetBuilder('resistance', data=u'something measured in ohms'),
            DatasetBuilder('seal', data=u'sealing method'),
            DatasetBuilder('description', data=u'a fake electrode object'),
            DatasetBuilder('location', data=u'Springfield Elementary School'),
            DatasetBuilder('filtering', data=u'a meaningless free-form text field'),
            DatasetBuilder('initial_access_resistance', data=u'I guess this changes'),
        ]
        elec = GroupBuilder('elec0',
                            attributes={'help': 'Metadata about an intracellular electrode',
                                        'namespace': 'core',
                                        'neurodata_type': 'IntracellularElectrode',
                                        },
                            datasets={d.name: d for d in datasets},
                            links={
                                'device': LinkBuilder(device, 'device')
                            })

        datasets = [
            DatasetBuilder('gain',
                           data=0.126,
                           attributes={},
                           ),
            DatasetBuilder('data',
                           data=[1, 2, 3, 4, 5],
                           attributes={'conversion': 1.0,
                                       'resolution': 0.0,
                                       'unit': u'A',
                                       }
                           ),
            DatasetBuilder('starting_time',
                           data=123.6,
                           attributes={'rate': 10000.0,
                                       'unit': 'Seconds',
                                       }
                           ),
                ]
        attributes = {'neurodata_type': 'PatchClampSeries',
                      'namespace': 'core',
                      'comments': u'no comments',
                      'help': 'Superclass definition for patch-clamp data',
                      'description': u'no description',
                      'stimulus_description': u'gotcha ya!',
                      }
        attributes['sweep_number'] = 4711
        pcs1 = GroupBuilder('pcs1',
                            attributes=attributes,
                            links={'electrode': LinkBuilder(elec, 'electrode')},
                            datasets={d.name: d for d in datasets},
                            )
        attributes['sweep_number'] = 4712
        pcs2a = GroupBuilder('pcs2a',
                             attributes=attributes,
                             links={'electrode': LinkBuilder(elec, 'electrode')},
                             datasets={d.name: d for d in datasets},
                             )
        pcs2b = GroupBuilder('pcs2b',
                             attributes=attributes,
                             links={'electrode': LinkBuilder(elec, 'electrode')},
                             datasets={d.name: d for d in datasets},
                             )

        column_id = DatasetBuilder('id', [0, 1, 2],
                                   attributes={'neurodata_type': 'ElementIdentifiers',
                                               'namespace': 'core',
                                               'help': 'unique identifiers for a list of elements',
                                               }
                                   )

        column_series = DatasetBuilder('series',
                                       attributes={'neurodata_type': 'VectorData',
                                                   'namespace': 'core',
                                                   'help': 'Values for a list of elements',
                                                   'description': u'PatchClampSeries with the same sweep number',
                                                   },
                                       data=[LinkBuilder(pcs) for pcs in (pcs1, pcs2a, pcs2b)]
                                       )

        column_index = DatasetBuilder('series_index', [1, 2, 3],
                                      attributes={'neurodata_type': 'VectorIndex',
                                                  'namespace': 'core',
                                                  'help': 'indexes into a list of values for a list of elements',
                                                  'target': ReferenceBuilder(column_series),
                                                  },
                                      )

        column_sweep_number = DatasetBuilder('sweep_number', data=[4711, 4712, 4712],
                                             attributes={'neurodata_type': 'VectorData',
                                                         'namespace': 'core',
                                                         'help': 'Values for a list of elements',
                                                         'description': u'Sweep number of the entries in that row',
                                                         }
                                             )

        columns = [column_id, column_series, column_index, column_sweep_number]
        sweep_table = GroupBuilder('sweep_table', datasets={c.name: c for c in columns},
                                   attributes={'neurodata_type': 'SweepTable',
                                               'namespace': 'core',
                                               'colnames': ('series',
                                                            'sweep_number'),
                                               'help': 'The table which groups different PatchClampSeries together',
                                               'description':
                                               u'A sweep table groups different PatchClampSeries together.',
                                               },
                                   )

        return sweep_table
