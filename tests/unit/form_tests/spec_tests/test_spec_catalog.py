import unittest2 as unittest

from pynwb.form.spec import GroupSpec, DatasetSpec, AttributeSpec, SpecCatalog


class SpecCatalogTest(unittest.TestCase):

    def setUp(self):
        self.catalog = SpecCatalog()
        self.attributes = [
            AttributeSpec('attribute1', 'my first attribute', 'text'),
            AttributeSpec('attribute2', 'my second attribute', 'text')
        ]
        self.spec = DatasetSpec('my first dataset',
                                'int',
                                name='dataset1',
                                dims=(None, None),
                                attributes=self.attributes,
                                linkable=False,
                                data_type_def='EphysData')

    def test_register_spec(self):
        self.catalog.register_spec(self.spec, 'test.yaml')
        result = self.catalog.get_spec('EphysData')
        self.assertIs(result, self.spec)

    def test_hierarchy(self):
        spikes_spec = DatasetSpec('my extending dataset', 'int',
                                  data_type_inc='EphysData',
                                  data_type_def='SpikeData')

        lfp_spec = DatasetSpec('my second extending dataset', 'int',
                               data_type_inc='EphysData',
                               data_type_def='LFPData')

        self.catalog.register_spec(self.spec, 'test.yaml')
        self.catalog.register_spec(spikes_spec, 'test.yaml')
        self.catalog.register_spec(lfp_spec, 'test.yaml')

        spike_hierarchy = self.catalog.get_hierarchy('SpikeData')
        lfp_hierarchy = self.catalog.get_hierarchy('LFPData')
        ephys_hierarchy = self.catalog.get_hierarchy('EphysData')
        self.assertTupleEqual(spike_hierarchy, ('SpikeData', 'EphysData'))
        self.assertTupleEqual(lfp_hierarchy, ('LFPData', 'EphysData'))
        self.assertTupleEqual(ephys_hierarchy, ('EphysData',))

    def test_get_spec_source_file(self):
        spikes_spec = GroupSpec('test group',
                                data_type_def='SpikeData')
        source_file_path = '/test/myt/test.yaml'
        self.catalog.auto_register(spikes_spec, source_file_path)
        recorded_source_file_path = self.catalog.get_spec_source_file('SpikeData')
        self.assertEqual(recorded_source_file_path, source_file_path)


if __name__ == '__main__':
    unittest.main()
