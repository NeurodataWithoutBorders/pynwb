from dateutil.parser import parse as dateutil_parse
from hdmf.build import ObjectMapper
from .. import register_map
from ..file import NWBFile, Subject
from ..core import ScratchData


@register_map(NWBFile)
class NWBFileMap(ObjectMapper):

    def __init__(self, spec):
        super(NWBFileMap, self).__init__(spec)

        acq_spec = self.spec.get_group('acquisition')
        self.unmap(acq_spec)
        self.map_spec('acquisition', acq_spec.get_neurodata_type('NWBDataInterface'))
        self.map_spec('acquisition', acq_spec.get_neurodata_type('DynamicTable'))
        # TODO: note that double mapping "acquisition" means __carg2spec and __attr2spec (both unused)
        # map "acquisition" to the last spec, in this case, DynamicTable

        ana_spec = self.spec.get_group('analysis')
        self.unmap(ana_spec)
        self.map_spec('analysis', ana_spec.get_neurodata_type('NWBContainer'))
        self.map_spec('analysis', ana_spec.get_neurodata_type('DynamicTable'))

        # map constructor arg and property 'stimulus' -> stimulus__presentation
        stimulus_spec = self.spec.get_group('stimulus')
        self.unmap(stimulus_spec)
        self.unmap(stimulus_spec.get_group('presentation'))
        self.unmap(stimulus_spec.get_group('templates'))
        self.map_spec('stimulus', stimulus_spec.get_group('presentation').get_neurodata_type('TimeSeries'))
        self.map_spec('stimulus_template', stimulus_spec.get_group('templates').get_neurodata_type('TimeSeries'))

        intervals_spec = self.spec.get_group('intervals')
        self.unmap(intervals_spec)
        self.map_spec('intervals', intervals_spec.get_neurodata_type('TimeIntervals'))

        epochs_spec = intervals_spec.get_group('epochs')
        self.map_spec('epochs', epochs_spec)

        trials_spec = intervals_spec.get_group('trials')
        self.map_spec('trials', trials_spec)

        invalid_times_spec = intervals_spec.get_group('invalid_times')
        self.map_spec('invalid_times', invalid_times_spec)

        general_spec = self.spec.get_group('general')
        self.unmap(general_spec)

        icephys_spec = general_spec.get_group('intracellular_ephys')
        self.unmap(icephys_spec)
        self.map_spec('icephys_electrodes', icephys_spec.get_neurodata_type('IntracellularElectrode'))
        self.map_spec('sweep_table', icephys_spec.get_neurodata_type('SweepTable'))

        # TODO map the filtering dataset to something or deprecate it
        self.unmap(icephys_spec.get_dataset('filtering'))

        ecephys_spec = general_spec.get_group('extracellular_ephys')
        self.unmap(ecephys_spec)
        self.map_spec('electrodes', ecephys_spec.get_group('electrodes'))
        self.map_spec('electrode_groups', ecephys_spec.get_neurodata_type('ElectrodeGroup'))

        ogen_spec = general_spec.get_group('optogenetics')
        self.unmap(ogen_spec)
        self.map_spec('ogen_sites', ogen_spec.get_neurodata_type('OptogeneticStimulusSite'))

        ophys_spec = general_spec.get_group('optophysiology')
        self.unmap(ophys_spec)
        self.map_spec('imaging_planes', ophys_spec.get_neurodata_type('ImagingPlane'))

        general_datasets = ['data_collection',
                            'experiment_description',
                            'experimenter',
                            'institution',
                            'keywords',
                            'lab',
                            'notes',
                            'pharmacology',
                            'protocol',
                            'related_publications',
                            'session_id',
                            'slices',
                            'source_script',
                            'stimulus',
                            'surgery',
                            'virus']
        for dataset_name in general_datasets:
            self.map_spec(dataset_name, general_spec.get_dataset(dataset_name))

        # note: constructor arg and property 'stimulus' is already mapped above, so use a different name here
        self.map_spec('stimulus_notes', general_spec.get_dataset('stimulus'))
        self.map_spec('source_script_file_name', general_spec.get_dataset('source_script').get_attribute('file_name'))

        self.map_spec('subject', general_spec.get_group('subject'))

        device_spec = general_spec.get_group('devices')
        self.unmap(device_spec)
        self.map_spec('devices', device_spec.get_neurodata_type('Device'))

        self.map_spec('lab_meta_data', general_spec.get_neurodata_type('LabMetaData'))

        proc_spec = self.spec.get_group('processing')
        self.unmap(proc_spec)
        self.map_spec('processing', proc_spec.get_neurodata_type('ProcessingModule'))

        scratch_spec = self.spec.get_group('scratch')
        self.unmap(scratch_spec)
        self.map_spec('scratch_datas', scratch_spec.get_neurodata_type('ScratchData'))
        self.map_spec('scratch_containers', scratch_spec.get_neurodata_type('NWBContainer'))
        self.map_spec('scratch_containers', scratch_spec.get_neurodata_type('DynamicTable'))

    @ObjectMapper.object_attr('scratch_datas')
    def scratch_datas(self, container, manager):
        scratch = container.scratch
        ret = list()
        for s in scratch.values():
            if isinstance(s, ScratchData):
                ret.append(s)
        return ret

    @ObjectMapper.object_attr('scratch_containers')
    def scratch_containers(self, container, manager):
        scratch = container.scratch
        ret = list()
        for s in scratch.values():
            if not isinstance(s, ScratchData):
                ret.append(s)
        return ret

    @ObjectMapper.constructor_arg('scratch')
    def scratch(self, builder, manager):
        scratch = builder.get('scratch')
        ret = list()
        if scratch is not None:
            for g in scratch.groups.values():
                ret.append(manager.construct(g))
            for d in scratch.datasets.values():
                ret.append(manager.construct(d))
        return tuple(ret) if len(ret) > 0 else None

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

    @ObjectMapper.constructor_arg('experimenter')
    def experimenter_carg(self, builder, manager):
        ret = None
        exp_bldr = builder['general'].get('experimenter')
        if exp_bldr is not None:
            if isinstance(exp_bldr.data, str):
                ret = (exp_bldr.data,)
            else:
                ret = tuple(exp_bldr.data)
        return ret

    @ObjectMapper.object_attr('experimenter')
    def experimenter_obj_attr(self, container, manager):
        ret = None
        if isinstance(container.experimenter, str):
            ret = (container.experimenter,)
        return ret

    @ObjectMapper.constructor_arg('related_publications')
    def publications_carg(self, builder, manager):
        ret = None
        pubs_bldr = builder['general'].get('related_publications')
        if pubs_bldr is not None:
            if isinstance(pubs_bldr.data, str):
                ret = (pubs_bldr.data,)
            else:
                ret = tuple(pubs_bldr.data)
        return ret

    @ObjectMapper.object_attr('related_publications')
    def publication_obj_attr(self, container, manager):
        ret = None
        if isinstance(container.related_publications, str):
            ret = (container.related_publications,)
        return ret


@register_map(Subject)
class SubjectMap(ObjectMapper):

    @ObjectMapper.constructor_arg('date_of_birth')
    def dateconversion(self, builder, manager):
        dob_builder = builder.get('date_of_birth')
        if dob_builder is None:
            return
        else:
            datestr = dob_builder.data
            date = dateutil_parse(datestr)
            return date
