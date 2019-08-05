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
        raw_ts_spec = acq_spec.get_neurodata_type('NWBDataInterface')
        self.map_spec('acquisition', raw_ts_spec)
        self.map_spec('analysis', self.spec.get_group('analysis').get_neurodata_type('NWBContainer'))

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
            'ogen_sites',
            general_spec.get_group('optogenetics').get_neurodata_type('OptogeneticStimulusSite'))
        self.map_spec(
            'imaging_planes',
            general_spec.get_group('optophysiology').get_neurodata_type('ImagingPlane'))

        proc_spec = self.spec.get_group('processing')
        self.unmap(proc_spec)
        self.map_spec('processing', proc_spec.get_neurodata_type('ProcessingModule'))
        # self.unmap(general_spec.get_dataset('stimulus'))
        self.map_spec('stimulus_notes', general_spec.get_dataset('stimulus'))
        self.map_spec('source_script_file_name', general_spec.get_dataset('source_script').get_attribute('file_name'))

        self.map_spec('subject', general_spec.get_group('subject'))
        self.map_spec('devices', general_spec.get_group('devices').get_neurodata_type('Device'))
        self.map_spec('lab_meta_data', general_spec.get_neurodata_type('LabMetaData'))

        scratch_spec = self.spec.get_group('scratch')
        self.unmap(scratch_spec)
        self.map_spec('scratch_datas', scratch_spec.get_neurodata_type('ScratchData'))
        self.map_spec('scratch_containers', scratch_spec.get_neurodata_type('NWBContainer'))

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
                ret = (builder.data,)
            else:
                ret = tuple(exp_bldr.data)
        return ret

    @ObjectMapper.object_attr('experimenter')
    def experimenter_obj_attr(self, container, manager):
        ret = None
        if isinstance(container.experimenter, str):
            ret = (container.experimenter,)
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
