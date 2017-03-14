import unittest

from pynwb.ecephys import ElectricalSeries, SpikeEventSeries, ElectrodeGroup, EventDetection, EventWaveform, Clustering, ClusterWaveform, LFP, FilteredEphys, FeatureExtraction

class ElectricalSeriesConstructor(unittest.TestCase):
    def test_init(self):
        eS = ElectricalSeries('test_eS', 'a hypothetical source', list(), list(), timestamps=list())
        self.assertEqual(eS.name, 'test_eS')
        self.assertEqual(eS.source, 'a hypothetical source')

class SpikeEventSeriesConstructor(unittest.TestCase):
    def test_init(self):
        sES = SpikeEventSeries('test_sES', 'a hypothetical source', list(), list(), timestamps=list())
        self.assertEqual(sES.name, 'test_sES')
        self.assertEqual(sES.source, 'a hypothetical source')

class ElectrodeGroupConstructor(unittest.TestCase):
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

class EventDetectionConstructor(unittest.TestCase):
    def test_init(self):
        pass

class EventWaveformConstructor(unittest.TestCase):
    def test_init(self):
        pass

class ClusteringConstructor(unittest.TestCase):
    def test_init(self):
        pass

class ClusterWaveformConstructor(unittest.TestCase):
    def test_init(self):
        pass

class LFPConstructor(unittest.TestCase):
    def test_init(self):
        pass

class FilteredEphysConstructor(unittest.TestCase):
    def test_init(self):
        pass

class FeatureExtractionConstructor(unittest.TestCase):
    def test_init(self):
        pass

