from abc import ABCMeta

from pynwb import NWBFile
from pynwb.icephys import (IntracellularElectrode, PatchClampSeries, CurrentClampStimulusSeries,
                           SweepTable, VoltageClampStimulusSeries, CurrentClampSeries,
                           VoltageClampSeries, IZeroClampSeries)
from pynwb.device import Device
from pynwb.testing import TestMapRoundTrip, TestDataInterfaceIO


class TestIntracellularElectrode(TestMapRoundTrip):

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

    def addContainer(self, nwbfile):
        ''' Should take an NWBFile object and add the container to it '''
        nwbfile.add_ic_electrode(self.elec)
        nwbfile.add_device(self.device)

    def getContainer(self, nwbfile):
        ''' Should take an NWBFile object and return the Container'''
        return nwbfile.get_ic_electrode(self.container.name)


class TestPatchClampSeries(TestDataInterfaceIO, metaclass=ABCMeta):

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
        return CurrentClampStimulusSeries(name="ccss", data=[1, 2, 3, 4, 5],
                                          starting_time=123.6, rate=10e3, electrode=self.elec, gain=0.126)


class TestVoltageClampStimulusSeries(TestPatchClampSeries):

    def setUpContainer(self):
        self.setUpElectrode()
        return VoltageClampStimulusSeries(name="vcss", data=[1, 2, 3, 4, 5],
                                          starting_time=123.6, rate=10e3, electrode=self.elec, gain=0.126)


class TestCurrentClampSeries(TestPatchClampSeries):

    def setUpContainer(self):
        self.setUpElectrode()
        return CurrentClampSeries(name="ccs", data=[1, 2, 3, 4, 5],
                                  starting_time=123.6, rate=10e3, electrode=self.elec, gain=0.126,
                                  bias_current=1.2, bridge_balance=2.3, capacitance_compensation=3.45)


class TestVoltageClampSeries(TestPatchClampSeries):

    def setUpContainer(self):
        self.setUpElectrode()
        return VoltageClampSeries(name="vcs", data=[1, 2, 3, 4, 5],
                                  starting_time=123.6, rate=10e3, electrode=self.elec,
                                  gain=0.126, capacitance_fast=1.2, capacitance_slow=2.3,
                                  resistance_comp_bandwidth=3.45, resistance_comp_correction=4.5,
                                  resistance_comp_prediction=5.678, whole_cell_capacitance_comp=6.789,
                                  whole_cell_series_resistance_comp=0.7)


class TestIZeroClampSeries(TestPatchClampSeries):

    def setUpContainer(self):
        self.setUpElectrode()
        return IZeroClampSeries(name="izcs", data=[1, 2, 3, 4, 5],
                                starting_time=123.6, rate=10e3, electrode=self.elec, gain=0.126)


class TestSweepTableRoundTripEasy(TestMapRoundTrip):

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

    def addContainer(self, nwbfile):
        nwbfile.sweep_table = self.sweep_table
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


class TestSweepTableRoundTripComplicated(TestMapRoundTrip):

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

    def addContainer(self, nwbfile):
        ''' Should take an NWBFile object and add the SweepTable container to it '''
        nwbfile.sweep_table = self.sweep_table
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
