import unittest

from pynwb.icephys import PatchClampSeries, CurrentClampSeries, IZeroClampSeries, CurrentClampStimulusSeries, \
        VoltageClampSeries, VoltageClampStimulusSeries, IntracellularElectrode
from pynwb.device import Device


def GetElectrode():
        device = Device(name='device_name', source='device_source')
        elec = IntracellularElectrode('test_iS',
                                      device,
                                      'a test source',
                                      'slice',
                                      'seal',
                                      'description',
                                      'location',
                                      'resistance',
                                      'filtering',
                                      'initial_access_resistance')
        return elec


class IntracellularElectrodeConstructor(unittest.TestCase):

    def GetElectrode(self):
        device = Device(name='device_name', source='device_source')
        elec = IntracellularElectrode('slice', 'seal', 'description', 'location', 'resistance',
                                      'filtering', 'initial_access_resistance',
                                      device)
        self.assertEqual(elec.slice, 'slice')
        self.assertEqual(elec.seal, 'seal')
        self.assertEqual(elec.description, 'description')
        self.assertEqual(elec.location, 'location')
        self.assertEqual(elec.resistance, 'resistance')
        self.assertEqual(elec.filtering, 'filtering')
        self.assertEqual(elec.initial_access_resistance, 'initial_access_resistance')
        self.assertEqual(elec.device, device)


class PatchClampSeriesConstructor(unittest.TestCase):

    def test_init(self):
        electrode_name = GetElectrode()

        pCS = PatchClampSeries('test_pCS', 'a hypothetical source', list(), 'unit',
                               electrode_name, 1.0, timestamps=list())
        self.assertEqual(pCS.name, 'test_pCS')
        self.assertEqual(pCS.source, 'a hypothetical source')
        self.assertEqual(pCS.unit, 'unit')
        self.assertEqual(pCS.electrode, electrode_name)
        self.assertEqual(pCS.gain, 1.0)


class CurrentClampSeriesConstructor(unittest.TestCase):

    def test_init(self):
        electrode_name = GetElectrode()

        cCS = CurrentClampSeries('test_cCS', 'a hypothetical source', list(), 'unit',
                                 electrode_name, 1.0, 2.0, 3.0, 4.0, timestamps=list())
        self.assertEqual(cCS.name, 'test_cCS')
        self.assertEqual(cCS.source, 'a hypothetical source')
        self.assertEqual(cCS.unit, 'unit')
        self.assertEqual(cCS.electrode, electrode_name)
        self.assertEqual(cCS.gain, 1.0)
        self.assertEqual(cCS.bias_current, 2.0)
        self.assertEqual(cCS.bridge_balance, 3.0)
        self.assertEqual(cCS.capacitance_compensation, 4.0)


class IZeroClampSeriesConstructor(unittest.TestCase):

    def test_init(self):
        electrode_name = GetElectrode()

        iZCS = IZeroClampSeries('test_iZCS', 'a hypothetical source', list(),
                                'unit', electrode_name, 1.0, timestamps=list())
        self.assertEqual(iZCS.name, 'test_iZCS')
        self.assertEqual(iZCS.source, 'a hypothetical source')
        self.assertEqual(iZCS.unit, 'unit')
        self.assertEqual(iZCS.electrode, electrode_name)
        self.assertEqual(iZCS.gain, 1.0)
        self.assertEqual(iZCS.bias_current, 0.0)
        self.assertEqual(iZCS.bridge_balance, 0.0)
        self.assertEqual(iZCS.capacitance_compensation, 0.0)


class CurrentClampStimulusSeriesConstructor(unittest.TestCase):

    def test_init(self):
        electrode_name = GetElectrode()

        cCSS = CurrentClampStimulusSeries('test_cCSS', 'a hypothetical source', list(),
                                          'unit', electrode_name, 1.0, timestamps=list())
        self.assertEqual(cCSS.name, 'test_cCSS')
        self.assertEqual(cCSS.source, 'a hypothetical source')
        self.assertEqual(cCSS.unit, 'unit')
        self.assertEqual(cCSS.electrode, electrode_name)
        self.assertEqual(cCSS.gain, 1.0)


class VoltageClampSeriesConstructor(unittest.TestCase):

    def test_init(self):
        electrode_name = GetElectrode()

        vCS = VoltageClampSeries('test_vCS', 'a hypothetical source', list(), 'unit', electrode_name,
                                 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, timestamps=list())
        self.assertEqual(vCS.name, 'test_vCS')
        self.assertEqual(vCS.source, 'a hypothetical source')
        self.assertEqual(vCS.unit, 'unit')
        self.assertEqual(vCS.electrode, electrode_name)
        self.assertEqual(vCS.gain, 1.0)
        self.assertEqual(vCS.capacitance_fast, 2.0)
        self.assertEqual(vCS.capacitance_slow, 3.0)
        self.assertEqual(vCS.resistance_comp_bandwidth, 4.0)
        self.assertEqual(vCS.resistance_comp_correction, 5.0)
        self.assertEqual(vCS.resistance_comp_prediction, 6.0)
        self.assertEqual(vCS.whole_cell_capacitance_comp, 7.0)
        self.assertEqual(vCS.whole_cell_series_resistance_comp, 8.0)


class VoltageClampStimulusSeriesConstructor(unittest.TestCase):

    def test_init(self):
        electrode_name = GetElectrode()

        vCSS = VoltageClampStimulusSeries('test_vCSS', 'a hypothetical source', list(),
                                          'unit', electrode_name, 1.0, timestamps=list())
        self.assertEqual(vCSS.name, 'test_vCSS')
        self.assertEqual(vCSS.source, 'a hypothetical source')
        self.assertEqual(vCSS.unit, 'unit')
        self.assertEqual(vCSS.electrode, electrode_name)


if __name__ == '__main__':
    unittest.main()
