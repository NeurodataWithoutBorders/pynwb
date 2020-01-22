import numpy as np

from pynwb.icephys import PatchClampSeries, CurrentClampSeries, IZeroClampSeries, CurrentClampStimulusSeries, \
        VoltageClampSeries, VoltageClampStimulusSeries, IntracellularElectrode
from pynwb.device import Device
from pynwb.testing import TestCase


def GetElectrode():
    device = Device(name='device_name')
    elec = IntracellularElectrode('test_iS',
                                  device,
                                  'description',
                                  'slice',
                                  'seal',
                                  'location',
                                  'resistance',
                                  'filtering',
                                  'initial_access_resistance')
    return elec


class IntracellularElectrodeConstructor(TestCase):

    def test_constructor(self):
        device = Device(name='device_name')
        elec = IntracellularElectrode('test_iS',
                                      device,
                                      'description',
                                      'slice',
                                      'seal',
                                      'location',
                                      'resistance',
                                      'filtering',
                                      'initial_access_resistance')
        self.assertEqual(elec.name, 'test_iS')
        self.assertEqual(elec.device, device)
        self.assertEqual(elec.description, 'description')
        self.assertEqual(elec.slice, 'slice')
        self.assertEqual(elec.seal, 'seal')
        self.assertEqual(elec.location, 'location')
        self.assertEqual(elec.resistance, 'resistance')
        self.assertEqual(elec.filtering, 'filtering')
        self.assertEqual(elec.initial_access_resistance, 'initial_access_resistance')


class PatchClampSeriesConstructor(TestCase):

    def test_default(self):
        electrode_name = GetElectrode()

        pCS = PatchClampSeries('test_pCS', list(), 'unit',
                               electrode_name, 1.0, timestamps=list())
        self.assertEqual(pCS.name, 'test_pCS')
        self.assertEqual(pCS.unit, 'unit')
        self.assertEqual(pCS.electrode, electrode_name)
        self.assertEqual(pCS.gain, 1.0)

    def test_sweepNumber_valid(self):
        electrode_name = GetElectrode()

        pCS = PatchClampSeries('test_pCS', list(), 'unit',
                               electrode_name, 1.0, timestamps=list(), sweep_number=4711)
        self.assertEqual(pCS.name, 'test_pCS')
        self.assertEqual(pCS.unit, 'unit')
        self.assertEqual(pCS.electrode, electrode_name)
        self.assertEqual(pCS.gain, 1.0)
        self.assertEqual(pCS.sweep_number, 4711)

    def test_sweepNumber_valid_np(self):
        electrode_name = GetElectrode()

        pCS = PatchClampSeries('test_pCS', list(), 'unit',
                               electrode_name, 1.0, timestamps=list(), sweep_number=1)
        self.assertEqual(pCS.name, 'test_pCS')
        self.assertEqual(pCS.unit, 'unit')
        self.assertEqual(pCS.electrode, electrode_name)
        self.assertEqual(pCS.gain, 1.0)
        self.assertEqual(pCS.sweep_number, np.uint32(1))

    def test_sweepNumber_large_and_valid(self):
        electrode_name = GetElectrode()

        pCS = PatchClampSeries('test_pCS', list(), 'unit',
                               electrode_name, 1.0, timestamps=list(), sweep_number=np.uint64(2**63-1))
        self.assertEqual(pCS.name, 'test_pCS')
        self.assertEqual(pCS.unit, 'unit')
        self.assertEqual(pCS.electrode, electrode_name)
        self.assertEqual(pCS.gain, 1.0)
        self.assertEqual(pCS.sweep_number, 2**63-1)

    def test_sweepNumber_throws_with_negative(self):
        electrode_name = GetElectrode()

        with self.assertRaises(ValueError):
            PatchClampSeries('test_pCS', list(), 'unit',
                             electrode_name, 1.0, timestamps=list(), sweep_number=-1)

    def test_sweepNumber_throws_with_NaN(self):
        electrode_name = GetElectrode()

        with self.assertRaises(TypeError):
            PatchClampSeries('test_pCS', list(), 'unit',
                             electrode_name, 1.0, timestamps=list(), sweep_number=float('nan'))

    def test_sweepNumber_throws_with_Float(self):
        electrode_name = GetElectrode()

        with self.assertRaises(TypeError):
            PatchClampSeries('test_pCS', list(), 'unit',
                             electrode_name, 1.0, timestamps=list(), sweep_number=1.5)


class CurrentClampSeriesConstructor(TestCase):

    def test_init(self):
        electrode_name = GetElectrode()

        cCS = CurrentClampSeries('test_cCS', list(), electrode_name, 1.0, "stimset", 2.0, 3.0, 4.0, timestamps=list())
        self.assertEqual(cCS.name, 'test_cCS')
        self.assertEqual(cCS.unit, 'volts')
        self.assertEqual(cCS.electrode, electrode_name)
        self.assertEqual(cCS.stimulus_description, "stimset")
        self.assertEqual(cCS.gain, 1.0)
        self.assertEqual(cCS.bias_current, 2.0)
        self.assertEqual(cCS.bridge_balance, 3.0)
        self.assertEqual(cCS.capacitance_compensation, 4.0)


class IZeroClampSeriesConstructor(TestCase):

    def test_init(self):
        electrode_name = GetElectrode()

        iZCS = IZeroClampSeries('test_iZCS', list(), electrode_name, 1.0, timestamps=list())
        self.assertEqual(iZCS.name, 'test_iZCS')
        self.assertEqual(iZCS.unit, 'volts')
        self.assertEqual(iZCS.electrode, electrode_name)
        self.assertEqual(iZCS.gain, 1.0)
        self.assertEqual(iZCS.bias_current, 0.0)
        self.assertEqual(iZCS.bridge_balance, 0.0)
        self.assertEqual(iZCS.capacitance_compensation, 0.0)


class CurrentClampStimulusSeriesConstructor(TestCase):

    def test_init(self):
        electrode_name = GetElectrode()

        cCSS = CurrentClampStimulusSeries('test_cCSS', list(), electrode_name, 1.0, timestamps=list())
        self.assertEqual(cCSS.name, 'test_cCSS')
        self.assertEqual(cCSS.unit, 'amperes')
        self.assertEqual(cCSS.electrode, electrode_name)
        self.assertEqual(cCSS.gain, 1.0)


class VoltageClampSeriesConstructor(TestCase):

    def test_init(self):
        electrode_name = GetElectrode()

        vCS = VoltageClampSeries('test_vCS', list(), electrode_name,
                                 1.0, "stimset", 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, timestamps=list())
        self.assertEqual(vCS.name, 'test_vCS')
        self.assertEqual(vCS.unit, 'amperes')
        self.assertEqual(vCS.electrode, electrode_name)
        self.assertEqual(vCS.stimulus_description, "stimset")
        self.assertEqual(vCS.gain, 1.0)
        self.assertEqual(vCS.capacitance_fast, 2.0)
        self.assertEqual(vCS.capacitance_slow, 3.0)
        self.assertEqual(vCS.resistance_comp_bandwidth, 4.0)
        self.assertEqual(vCS.resistance_comp_correction, 5.0)
        self.assertEqual(vCS.resistance_comp_prediction, 6.0)
        self.assertEqual(vCS.whole_cell_capacitance_comp, 7.0)
        self.assertEqual(vCS.whole_cell_series_resistance_comp, 8.0)


class VoltageClampStimulusSeriesConstructor(TestCase):

    def test_init(self):
        electrode_name = GetElectrode()

        vCSS = VoltageClampStimulusSeries('test_vCSS', list(), electrode_name, 1.0, timestamps=list())
        self.assertEqual(vCSS.name, 'test_vCSS')
        self.assertEqual(vCSS.unit, 'volts')
        self.assertEqual(vCSS.electrode, electrode_name)
