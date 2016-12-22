from . import spec, map, h5tools, write, utils

#import pkg_resources
#import importlib
#import json
#from .spec import Spec, AttributeSpec, BaseStorageSpec, DatasetSpec, GroupSpec, SpecCatalog
#from .map import TypeMap, Condition, AttrMap

#__all__ = ['Spec',
#         'AttributeSpec',
#         'BaseStorageSpec',
#         'DatasetSpec',
#         'GroupSpec',
#         'TypeMap',
#         'AttrMap',
#         'Condition']


#def __load_spec(spec):
#
#    spec = spec['fs']['core']['schema']
#    
#    def build_group(name, d):
#        required = True
#        myname = name
#        if myname[-1] == '?':
#            required = False
#            myname = myname[:-1]
#        if myname[-1] == '/':
#            myname = myname[:-1]
#        if myname == '*':
#            required = False
#        desc = d.pop('description', None)
#        if 'attributes' in d:
#            attributes = d.pop('attributes', None)
#            nwb_type = None
#            if 'neurodata_type' in attributes:
#                nwb_type = attributes['neurodata_type']['value']
#            spec = GroupSpec(name, required=required, doc=desc, nwb_type=nwb_type)
#            add_attributes(spec, attributes)
#        else:
#            spec = GroupSpec(name, required=required, doc=desc)
#        for key, value in d.items():
#            name = key
#            if isinstance(value, str) or key == 'merge':
#                continue
#            if key.rfind('/') == -1:
#                spec.set_dataset(build_dataset(name, value))
#            else:
#                spec.set_group(build_group(name, value))
#        return spec
#    
#    def build_dataset(name, d):
#        kwargs = remap_keys(name, d)
#        spec = DatasetSpec(kwargs.pop('dtype'), name=name, **kwargs)
#        if 'attributes' in d:
#            add_attributes(spec, d['attributes'])
#        return spec
#    
#    def add_attributes(spec, attributes):
#        for attr_name, attr_spec in attributes.items():
#            spec.set_attribute(build_attribute(attr_name, attr_spec))
#    
#    def build_attribute(name, d):
#        kwargs = remap_keys(name, d)
#        spec = AttributeSpec(name, kwargs.pop('dtype'), **kwargs)
#        return spec
#    
#    def remap_keys(name, d):
#        ret = dict()
#        ret['required'] = True
#        if name == '?':
#            ret['required'] = False
#        ret['const'] = d.get('const', None)
#        ret['dtype'] = d.get('data_type', 'None')
#        
#        ret['default'] = d.get('value', None)
#        ret['doc'] = d.get('description', None)
#        ret['dim'] = d.get('dimensions', None)
#    
#        return ret
#
#    
#    
#    def merge_spec(target, source):
#        for grp_spec in source.groups:
#            target.set_group(grp_spec)
#        for dset_spec in source.datasets:
#            target.set_group(dset_spec)
#        for attr_spec in source.attributes:
#            target.set_attribute(attr_spec)
#    
#    # load File spec
#    # /
#    # /acquisition/
#    # /analysis/
#    # /epochs/
#    # /general/
#    # /general/extracellular_ephys/?
#    # /general/intracellular_ephys/?
#    # /general/optogenetics/?
#    # /general/optophysiology/?
#    # /processing/
#    # /stimulus/
#    root = GroupSpec(nwb_type='NwbFile')
#    acquisition = root.set_group(build_group('acquisition', spec['/acquisition/']))
#    analysis = root.set_group(build_group('analysis', spec['/analysis/']))
#    epochs = root.set_group(build_group('epochs', spec['/epochs/']))
#    processing = root.set_group(build_group('processing', spec['/processing/']))
#    stimulus = root.set_group(build_group('stimulus', spec['/stimulus/']))
#    general = root.set_group(build_group('general', spec['/general/']))
#    extracellular_ephys = general.set_group(build_group('extracellular_ephys?', spec['/general/extracellular_ephys/?']))
#    intracellular_ephys = general.set_group(build_group('intracellular_ephys?', spec['/general/intracellular_ephys/?']))
#    optogenetics = general.set_group(build_group('optogenetics?', spec['/general/optogenetics/?']))
#    optophysiology = general.set_group(build_group('optophysiology?', spec['/general/optophysiology/?']))
#    
#    # load TimeSeries specs
#    ts_types = [
#        "<AbstractFeatureSeries>/",
#        "<AnnotationSeries>/",
#        "<CurrentClampSeries>/",
#        "<CurrentClampStimulusSeries>/",
#        "<ElectricalSeries>/",
#        "<IZeroClampSeries>/",
#        "<ImageMaskSeries>/",
#        "<ImageSeries>/",
#        "<IndexSeries>/",
#        "<IntervalSeries>/",
#        "<OpticalSeries>/",
#        "<OptogeneticSeries>/",
#        "<PatchClampSeries>/",
#        "<RoiResponseSeries>/",
#        "<SpatialSeries>/",
#        "<SpikeEventSeries>/",
#        "<TimeSeries>/",
#        "<TwoPhotonSeries>/",
#        "<VoltageClampSeries>/",
#        "<VoltageClampStimulusSeries>/"
#    ]
#    ts_specs = dict()
#    while ts_types:
#        ts_type = ts_types.pop(0)
#        ts_dict = spec[ts_type]
#        merge = list()
#        all_bases = True
#        for merge_type in ts_dict.pop('merge', list()):
#            tmp = ts_specs.get(merge_type, None)
#            if tmp:
#                merge.append(tmp)
#            else:
#                ts_types.append(ts_type)
#                all_bases = False
#                break
#        if not all_bases:
#            continue
#        
#        ts_spec = build_group('*', ts_dict)
#        for m in merge:
#            merge_spec(m, ts_spec)
#        ts_specs[ts_type] = ts_spec
#
#    print ('created specs for all TimeSeries')
#        
#    # load Module specs
#    iface = build_group('*', spec['<Interface>/'])
#    print ('created specs for <Interface>')
#
#    mod_specs = dict()
#    
#    mod_types = [
#        "BehavioralEpochs/",
#        "BehavioralEvents/",
#        "BehavioralTimeSeries/",
#        "ClusterWaveforms/",
#        "Clustering/",
#        "CompassDirection/",
#        "DfOverF/",
#        "EventDetection/",
#        "EventWaveform/",
#        "EyeTracking/",
#        "FeatureExtraction/",
#        "FilteredEphys/",
#        "Fluorescence/",
#        "ImageSegmentation/",
#        "ImagingRetinotopy/",
#        "LFP/",
#        "MotionCorrection/",
#        "Position/",
#        "PupilTracking/",
#        "UnitTimes/",
#    ]
#    print ('creating specs for Modules')
#    for mod in mod_types:
#        print ('creating spec for %s' % mod)
#        mod_spec = spec[mod]
#        merge = mod_spec.pop('merge')
#        mod_specs[mod] = build_group(mod, mod_spec)
#        print ('merging %s with Interface' % mod)
#        merge_spec(mod_specs[mod], iface)
#    print ('created specs for all Modules')
#    
#    #register with SpecMap
#    SpecCatalog.register_spec('NWB', root)
#    SpecCatalog.register_spec('Interface', iface)
#    for ts_type, ts_spec in ts_specs.items():
#        tmp = ts_type[1:len(ts_type)-2]
#        SpecCatalog.register_spec(tmp, ts_spec)
#    for mod_type, mod_spec in mod_specs.items():
#        tmp = mod_type[1:len(mod_type)-1]
#        SpecCatalog.register_spec(tmp, mod_spec)
#        pass
#
#def __map_types():
#
#    # override default mapping behavior for TimeSeries objects
#    ts_attr_map = AttrMap(SpecCatalog.get_spec('TimeSeries'))
#    data_map = ts_attr_map.get_map('data')
#    ts.map_attr('unit', data_map.get_attribute('unit'))
#    ts.map_attr('resolution', data_map.get_attribute('resolution'))
#    ts.map_attr('conversion', data_map.get_attribute('conversion'))
#
#    timestamps_map = ts_attr_map.get_map('timestamps')
#    ts.map_attr('interval', timestamps_map.get_attribute('interval'))
#    ts.map_attr('timestamps_unit', timestamps_map.get_attribute('unit'))
#
#    starting_times_map = ts_attr_map.get_map('starting_time')
#    ts.map_attr('rate', starting_times_map.get_attribute('rate'))
#    ts.map_attr('rate_unit', ts_attr_map.get_map('starting_time').get_attribute('unit'))
#    TypMap.register_map('TimeSeries', ts_attr_map)
#    
#    for reg_type in SpecCatalog.get_registered_types():
#        existing = TypeMap.get_map(reg_type)
#        if existing:
#            continue
#        TypMap.register_map(reg_type, AttrMap(SpecCatalog.get_spec(reg_type)))

#thing = pkg_resources.resource_stream(__name__, '../data/spec.json')
#thing = pkg_resources.resource_string(__name__, '../data/spec.json')
#thing = str(thing)
#print(type(thing))

#spec_path = pkg_resources.resource_filename(__name__, '../data/spec.json')
#with open(spec_path) as spec_in:
#    __load_spec(json.load(spec_in))
#__map_types()



