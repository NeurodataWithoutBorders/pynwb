import numpy as np

from pynwb import NWBFile
from pynwb.icephys import (IntracellularElectrode, PatchClampSeries, CurrentClampStimulusSeries,
                           SweepTable, VoltageClampStimulusSeries, CurrentClampSeries,
                           VoltageClampSeries, IZeroClampSeries)
from pynwb.device import Device
from pynwb.testing import NWBH5IOMixin, AcquisitionH5IOMixin, TestCase


class TestIntracellularElectrode(NWBH5IOMixin, TestCase):

    def setUpContainer(self):
        """ Return the test IntracellularElectrode to read/write """
        self.device = Device(name='device_name')
        elec = IntracellularElectrode(name="elec0",
                                      slice='tissue slice',
                                      resistance='something measured in ohms',
                                      seal='sealing method',
                                      description='a fake electrode object',
                                      location='Springfield Elementary School',
                                      filtering='a meaningless free-form text field',
                                      initial_access_resistance='I guess this changes',
                                      device=self.device)
        return elec

    def addContainer(self, nwbfile):
        """ Add the test IntracellularElectrode and Device to the given NWBFile """
        nwbfile.add_icephys_electrode(self.container)
        nwbfile.add_device(self.device)

    def getContainer(self, nwbfile):
        """ Return the test IntracellularElectrode from the given NWBFile """
        return nwbfile.get_icephys_electrode(self.container.name)


class TestPatchClampSeries(AcquisitionH5IOMixin, TestCase):

    def setUpElectrode(self):
        """ Set up the test IntracellularElectrode """
        self.device = Device(name='device_name')
        self.elec = IntracellularElectrode(name="elec0", slice='tissue slice',
                                           resistance='something measured in ohms',
                                           seal='sealing method', description='a fake electrode object',
                                           location='Springfield Elementary School',
                                           filtering='a meaningless free-form text field',
                                           initial_access_resistance='I guess this changes',
                                           device=self.device)

    def setUpContainer(self):
        """ Return the test PatchClampSeries to read/write """
        self.setUpElectrode()
        return PatchClampSeries(name="pcs", data=[1, 2, 3, 4, 5], unit='A',
                                starting_time=123.6, rate=10e3, electrode=self.elec, gain=0.126,
                                stimulus_description="gotcha ya!", sweep_number=np.uint(4711))

    def addContainer(self, nwbfile):
        """
        Add the test PatchClampSeries as an acquisition and IntracellularElectrode and Device to the given NWBFile
        """
        nwbfile.add_icephys_electrode(self.elec)
        nwbfile.add_device(self.device)
        super().addContainer(nwbfile)


class TestCurrentClampStimulusSeries(TestPatchClampSeries):

    def setUpContainer(self):
        """ Return the test CurrentClampStimulusSeries to read/write """
        self.setUpElectrode()
        return CurrentClampStimulusSeries(name="ccss", data=[1, 2, 3, 4, 5],
                                          starting_time=123.6, rate=10e3, electrode=self.elec, gain=0.126)


class TestVoltageClampStimulusSeries(TestPatchClampSeries):

    def setUpContainer(self):
        """ Return the test VoltageClampStimulusSeries to read/write """
        self.setUpElectrode()
        return VoltageClampStimulusSeries(name="vcss", data=[1, 2, 3, 4, 5],
                                          starting_time=123.6, rate=10e3, electrode=self.elec, gain=0.126)


class TestCurrentClampSeries(TestPatchClampSeries):

    def setUpContainer(self):
        """ Return the test CurrentClampSeries to read/write """
        self.setUpElectrode()
        return CurrentClampSeries(name="ccs", data=[1, 2, 3, 4, 5],
                                  starting_time=123.6, rate=10e3, electrode=self.elec, gain=0.126,
                                  bias_current=1.2, bridge_balance=2.3, capacitance_compensation=3.45)


class TestVoltageClampSeries(TestPatchClampSeries):

    def setUpContainer(self):
        """ Return the test VoltageClampSeries to read/write """
        self.setUpElectrode()
        return VoltageClampSeries(name="vcs", data=[1, 2, 3, 4, 5],
                                  starting_time=123.6, rate=10e3, electrode=self.elec,
                                  gain=0.126, capacitance_fast=1.2, capacitance_slow=2.3,
                                  resistance_comp_bandwidth=3.45, resistance_comp_correction=4.5,
                                  resistance_comp_prediction=5.678, whole_cell_capacitance_comp=6.789,
                                  whole_cell_series_resistance_comp=0.7)


class TestIZeroClampSeries(TestPatchClampSeries):

    def setUpContainer(self):
        """ Return the test IZeroClampSeries to read/write """
        self.setUpElectrode()
        return IZeroClampSeries(name="izcs", data=[1, 2, 3, 4, 5],
                                starting_time=123.6, rate=10e3, electrode=self.elec, gain=0.126)


class TestSweepTableRoundTripEasy(NWBH5IOMixin, TestCase):

    def setUpContainer(self):
        """ Return the test SweepTable to read/write """
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
                                    stimulus_description="gotcha ya!", sweep_number=np.uint(4711))
        return SweepTable(name='sweep_table')

    def addContainer(self, nwbfile):
        """
        Add the test SweepTable, PatchClampSeries, IntracellularElectrode, and Device to the given NWBFile
        """
        nwbfile.sweep_table = self.container
        nwbfile.add_device(self.device)
        nwbfile.add_icephys_electrode(self.elec)
        nwbfile.add_acquisition(self.pcs)

    def getContainer(self, nwbfile):
        """ Return the test SweepTable from the given NWBFile """
        return nwbfile.sweep_table

    def test_container(self):
        """ Test properties of the SweepTable read from file """
        description = 'a file to test writing and reading a %s' % self.container_type
        identifier = 'TEST_%s' % self.container_type
        nwbfile = NWBFile(description, identifier, self.start_time, file_create_date=self.create_date)
        self.addContainer(nwbfile)

        sweep_table = self.getContainer(nwbfile)
        self.assertEqual(len(sweep_table['series'].data), 1)
        self.assertEqual(sweep_table.id[0], 0)
        self.assertEqual(sweep_table['sweep_number'].data[0], 4711)


class TestSweepTableRoundTripComplicated(NWBH5IOMixin, TestCase):

    def setUpContainer(self):
        """ Return the test SweepTable to read/write """
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
                                     stimulus_description="gotcha ya!", sweep_number=np.uint(4711))
        self.pcs2a = PatchClampSeries(name="pcs2a", data=[1, 2, 3, 4, 5], unit='A',
                                      starting_time=123.6, rate=10e3, electrode=self.elec, gain=0.126,
                                      stimulus_description="gotcha ya!", sweep_number=np.uint(4712))
        self.pcs2b = PatchClampSeries(name="pcs2b", data=[1, 2, 3, 4, 5], unit='A',
                                      starting_time=123.6, rate=10e3, electrode=self.elec, gain=0.126,
                                      stimulus_description="gotcha ya!", sweep_number=np.uint(4712))

        return SweepTable(name='sweep_table')

    def addContainer(self, nwbfile):
        """
        Add the test SweepTable, PatchClampSeries, IntracellularElectrode, and Device to the given NWBFile
        """
        nwbfile.sweep_table = self.container
        nwbfile.add_device(self.device)
        nwbfile.add_icephys_electrode(self.elec)

        nwbfile.add_acquisition(self.pcs1)
        nwbfile.add_stimulus_template(self.pcs2a)
        nwbfile.add_stimulus(self.pcs2b)

    def getContainer(self, nwbfile):
        """ Return the test SweepTable from the given NWBFile """
        return nwbfile.sweep_table

    def test_container(self):
        """ Test properties of the SweepTable read from file """
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
