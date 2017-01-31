import unittest

from pynwb.ecephys import *

class TestElectrodeGroupConstructor(unittest.TestCase):

    def setUp(self):
        #print(ElectrodeGroup.__init__.docval)
        self.name = 'my_group'
        self.coord = (1.1, 2.2, 3.3)
        self.desc = "an example electrode group"
        self.dev = "my favorite device"
        self.loc = "my favorote brain location"
        self.eg = ElectrodeGroup(self.name, 
                                 self.coord,
                                 self.desc,
                                 self.dev,
                                 self.loc)

    def test_impedance(self):
        self.assertEqual(self.eg.impedance, -1)
        
    def test_name(self):
        self.assertEqual(self.eg.name, self.name)

    def test_physical_location(self):
        self.assertTupleEqual(self.eg.physical_location, self.coord)

    def test_description(self):
        self.assertEqual(self.eg.description, self.desc)

    def test_device(self):
        self.assertEqual(self.eg.device, self.dev)

    def test_location(self):
        self.assertEqual(self.eg.location, self.loc)
