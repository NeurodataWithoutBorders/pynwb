from dateutil.parser import parse as dateutil_parse
from ..form.build import ObjectMapper
from .. import register_map
from ..file import NWBFile


@register_map(NWBFile)
class NWBFileMap(ObjectMapper):

    def __init__(self, spec):
        super(NWBFileMap, self).__init__(spec)
        raw_ts_spec = self.spec.get_group('acquisition').get_neurodata_type('NWBDataInterface')
        self.map_spec('acquisition', raw_ts_spec)

        stimulus_spec = self.spec.get_group('stimulus')
        self.unmap(stimulus_spec)
        self.map_spec('stimulus', stimulus_spec.get_group('presentation').get_neurodata_type('TimeSeries'))
        self.map_spec('stimulus_template', stimulus_spec.get_group('templates').get_neurodata_type('TimeSeries'))

        intervals_spec = self.spec.get_group('intervals')
        epochs_spec = intervals_spec.get_group('epochs')
        self.map_spec('epochs', epochs_spec)
        trials_spec = intervals_spec.get_group('trials')
        self.map_spec('trials', trials_spec)
        self.map_spec('intervals', intervals_spec.get_neurodata_type('TimeIntervals'))

        general_spec = self.spec.get_group('general')
        icephys_spec = general_spec.get_group('intracellular_ephys')
        self.map_spec('ic_electrodes', icephys_spec.get_neurodata_type('IntracellularElectrode'))
        ecephys_spec = general_spec.get_group('extracellular_ephys')
        self.map_spec('sweep_table', icephys_spec.get_neurodata_type('SweepTable'))
        self.map_spec('electrodes', ecephys_spec.get_group('electrodes'))
        self.map_spec('electrode_groups', ecephys_spec.get_neurodata_type('ElectrodeGroup'))
        self.map_spec(
            'optogenetic_sites',
            general_spec.get_group('optogenetics').get_neurodata_type('OptogeneticStimulusSite'))
        self.map_spec(
            'imaging_planes',
            general_spec.get_group('optophysiology').get_neurodata_type('ImagingPlane'))

        self.map_spec(
            'modules',
            self.spec.get_group('processing').get_neurodata_type('ProcessingModule'))
        # self.unmap(general_spec.get_dataset('stimulus'))
        self.map_spec('stimulus_notes', general_spec.get_dataset('stimulus'))
        self.map_spec('source_script_file_name', general_spec.get_dataset('source_script').get_attribute('file_name'))

        self.map_spec('subject', general_spec.get_group('subject'))
        self.map_spec('devices', general_spec.get_group('devices').get_neurodata_type('Device'))

    @ObjectMapper.constructor_arg('session_start_time')
    def dateconversion(self, builder, manager):
        datestr = builder.get('session_start_time').data
        date = dateutil_parse(datestr)
        return date

    @ObjectMapper.constructor_arg('timestamps_reference_time')
    def dateconversion_trt(self, builder, manager):
        datestr = builder.get('timestamps_reference_time').data
        date = dateutil_parse(datestr)
        return date

    @ObjectMapper.constructor_arg('file_create_date')
    def dateconversion_list(self, builder, manager):
        datestr = builder.get('file_create_date').data
        dates = list(map(dateutil_parse, datestr))
        return dates

    @ObjectMapper.constructor_arg('file_name')
    def name(self, builder, manager):
        return builder.name
