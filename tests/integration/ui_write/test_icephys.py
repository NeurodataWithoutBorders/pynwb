from pynwb.icephys import (IntracellularElectrode, PatchClampSeries, CurrentClampStimulusSeries,
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

    def setUpContainer(self):

        # will be overwritten in addContainer
        return None

    def addContainer(self, nwbfile):
        device = Device(name='device_name')
        nwbfile.add_device(device)
        elec = IntracellularElectrode(name="elec0", slice='tissue slice',
                                      resistance='something measured in ohms',
                                      seal='sealing method', description='a fake electrode object',
                                      location='Springfield Elementary School',
                                      filtering='a meaningless free-form text field',
                                      initial_access_resistance='I guess this changes',
                                      device=device)
        nwbfile.add_ic_electrode(elec)
        pcs = PatchClampSeries(name="pcs", data=[1, 2, 3, 4, 5], unit='A',
                               starting_time=123.6, rate=10e3, electrode=elec, gain=0.126,
                               stimulus_description="gotcha ya!", sweep_number=4711)
        nwbfile.add_acquisition(pcs)
        self.container = nwbfile.sweep_table

        self.assertEqual(len(self.container['series'].data), 1)
        self.assertEqual(self.container.id[0], 0)
        self.assertEqual(self.container['sweep_number'].data[0], 4711)

    def getContainer(self, nwbfile):
        return nwbfile.sweep_table


class TestSweepTableRoundTripComplicated(base.TestMapRoundTrip):

    def setUpContainer(self):
        # will be overwritten in addContainer
        return None

    def addContainer(self, nwbfile):
        device = Device(name='device_name')
        nwbfile.add_device(device)
        elec = IntracellularElectrode(name="elec0", slice='tissue slice',
                                      resistance='something measured in ohms',
                                      seal='sealing method', description='a fake electrode object',
                                      location='Springfield Elementary School',
                                      filtering='a meaningless free-form text field',
                                      initial_access_resistance='I guess this changes',
                                      device=device)
        nwbfile.add_ic_electrode(elec)

        self.pcs1 = PatchClampSeries(name="pcs1", data=[1, 2, 3, 4, 5], unit='A',
                                     starting_time=123.6, rate=10e3, electrode=elec, gain=0.126,
                                     stimulus_description="gotcha ya!", sweep_number=4711)
        nwbfile.add_acquisition(self.pcs1)

        self.pcs2a = PatchClampSeries(name="pcs2a", data=[1, 2, 3, 4, 5], unit='A',
                                      starting_time=123.6, rate=10e3, electrode=elec, gain=0.126,
                                      stimulus_description="gotcha ya!", sweep_number=4712)
        nwbfile.add_stimulus_template(self.pcs2a)

        self.pcs2b = PatchClampSeries(name="pcs2b", data=[1, 2, 3, 4, 5], unit='A',
                                      starting_time=123.6, rate=10e3, electrode=elec, gain=0.126,
                                      stimulus_description="gotcha ya!", sweep_number=4712)
        nwbfile.add_stimulus(self.pcs2b)

        self.container = nwbfile.sweep_table

        self.assertEqual(len(self.container['series'].data), 3)
        self.assertEqual(self.container['sweep_number'].data[0], 4711)
        self.assertEqual(self.container['sweep_number'].data[1], 4712)
        self.assertEqual(self.container['sweep_number'].data[2], 4712)

        series = self.container.get_series(4711)
        self.assertEqual(len(series), 1)
        names = [elem.name for elem in series]
        self.assertEqual(names, ["pcs1"])
        sweep_numbers = [elem.sweep_number for elem in series]
        self.assertEqual(sweep_numbers, [4711])

        series = self.container.get_series(4712)
        self.assertEqual(len(series), 2)
        names = [elem.name for elem in series]
        self.assertEqual(names, ["pcs2a", "pcs2b"])
        sweep_numbers = [elem.sweep_number for elem in series]
        self.assertEqual(sweep_numbers, [4712, 4712])

    def getContainer(self, nwbfile):
        return nwbfile.sweep_table
