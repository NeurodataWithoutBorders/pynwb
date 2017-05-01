from form import ObjectMapper
from . import register_map

@register_map('NWBFile')
class NWBFileMap(ObjectMapper):

    def __init__(self, spec):
        super(NWBFileMap, self).__init__(spec)
        self.map_attr('raw_data', self.spec.get_group('acquisition').get_group('timeseries').get_neurodata_type('TimeSeries'))
        stimulus_spec = self.spec.get_group('stimulus')
        self.map_attr('stimulus', stimulus_spec.get_group('presentation'))
        self.map_attr('stimulus_templates', stimulus_spec.get_group('templates'))
        general_spec = self.spec.get_group('general')
        self.map_attr('ic_electrodes', general_spec.get_group('intracellular_ephys'))
        self.map_attr('ec_electrodes', general_spec.get_group('extracellular_ephys'))
        self.map_attr('optogenetic_sites', general_spec.get_group('optogenetics'))
        self.map_attr('imaging_planes', general_spec.get_group('optophysiology'))
        self.map_attr('modules', self.spec.get_group('processing'))
        self.unmap(general_spec.get_dataset('stimulus'))

    @const_arg('file_name')
    def name(self, h5group):
        return h5group.name
