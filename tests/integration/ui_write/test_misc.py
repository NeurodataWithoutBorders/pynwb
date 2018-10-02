import unittest2 as unittest
from . import base

import numpy as np
from pynwb.form.build import GroupBuilder, DatasetBuilder, ReferenceBuilder

from pynwb.misc import UnitTimes

class TestUnitTimesIO(base.TestDataInterfaceIO):

    def setUpContainer(self):
        ut = UnitTimes('UnitTimes integration test', name='UnitTimesTest')
        ut.add_spike_times(0, [0, 1, 2])
        ut.add_spike_times(1, [3, 4, 5])
        return ut

    def setUpBuilder(self):
        ids_builder = DatasetBuilder('unit_ids', [0, 1],
                                     attributes={'neurodata_type': 'ElementIdentifiers',
                                                 'namespace': 'core',
                                                 'help': 'unique identifiers for a list of elements'})
        st_builder = DatasetBuilder('spike_times', [0, 1, 2, 3, 4, 5],
                                    attributes={'neurodata_type': 'VectorData',
                                                'namespace': 'core',
                                                'help': 'Values for a list of elements'})
        sti_builder = DatasetBuilder('spike_times_index',
                                     [3, 6],
                                     attributes={'neurodata_type': 'VectorIndex',
                                                 'namespace': 'core',
                                                 'target': ReferenceBuilder(st_builder),
                                                 'help': 'indexes into a list of values for a list of elements'})
        return GroupBuilder('UnitTimesTest',
                            attributes={'neurodata_type': 'UnitTimes',
                                        'namespace': 'core',
                                        'help': 'Estimated spike times from a single unit',
                                        'source': 'UnitTimes integration test'},
                            datasets={'unit_ids': ids_builder,
                                      'spike_times': st_builder,
                                      'spike_times_index': sti_builder})

    def test_get_spike_times(self):
        ut = self.roundtripContainer()
        received = ut.get_unit_spike_times(0)
        self.assertTrue(np.array_equal(received, [0, 1, 2]))
        received = ut.get_unit_spike_times(1)
        self.assertTrue(np.array_equal(received, [3, 4, 5]))


