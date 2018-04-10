import unittest2 as unittest

import numpy as np

from pynwb.form.build import GroupBuilder, DatasetBuilder, LinkBuilder, RegionBuilder, ReferenceBuilder

from pynwb.icephys import *  # noqa: F403
from pynwb.misc import UnitTimes

from . import base


class TestIntracellularElectrode(base.TestMapRoundTrip):

    def setUpContainer(self):
        elec = IntracellularElectrode(name="elec0", source='', slice='', resistance='', seal='', description='',
                                      location='', filtering='', initial_access_resistance='', device='')
        return elec

    def addContainer(self, nwbfile):
        ''' Should take an NWBFile object and add the container to it '''
        nwbfile.add_ic_electrode(self.container)

    def getContainer(self, nwbfile):
        ''' Should take an NWBFile object and return the Container'''
        return nwbfile.get_ic_electrode(self.container.name)


class TestPCS(base.TestDataInterfaceIO):

    def setUpElectrode(self):
        self.elec = IntracellularElectrode(name="elec0", source='', slice='', resistance='', seal='', description='',
                                      location='', filtering='', initial_access_resistance='', device='')

    def addContainer(self, nwbfile):
        ''' Should take an NWBFile object and add the container to it '''
        nwbfile.add_ic_electrode(self.elec)
        super(TestPCS, self).addContainer(nwbfile)


class TestCCSS(TestPCS):

    def setUpContainer(self):
        self.setUpElectrode()
        ccss = CurrentClampStimulusSeries(name="ccss", source="command", data=[1, 2, 3, 4, 5], unit='A',
                                          starting_time=123.6, rate=10e3, electrode=self.elec, gain=0.126)
        return ccss
