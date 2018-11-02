from pynwb.icephys import IntracellularElectrode, CurrentClampStimulusSeries
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


class TestCurrentClampStimulusSeries(TestPatchClampSeries):

    def setUpContainer(self):
        self.setUpElectrode()
        return CurrentClampStimulusSeries(name="ccss", data=[1, 2, 3, 4, 5], unit='A',
                                          starting_time=123.6, rate=10e3, electrode=self.elec, gain=0.126)
