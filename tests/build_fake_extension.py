from pynwb.spec import NWBNamespaceBuilder, NWBGroupSpec, NWBAttributeSpec

ns_builder = NWBNamespaceBuilder('Extension for us in my Lab', "mylab")


ext1 = NWBGroupSpec('A custom ElectricalSeries for my lab',
                    attributes=[NWBAttributeSpec('trode_id', 'the tetrode id', 'int')],
                    neurodata_type_inc='ElectricalSeries',
                    neurodata_type_def='TetrodeSeries')


ext_source = 'fake_extension.yaml'
ns_builder.add_spec(ext_source, ext1)

ns_path = 'fake_namespace.yaml'
ns_builder.export(ns_path)
