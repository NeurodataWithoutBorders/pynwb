import pkg_resources
import importlib
import json
from . import spec
from .spec import Spec, AttributeSpec, AttributableSpec, DatasetSpec, GroupSpec, SpecCatalog
from .map import TypeMap, Condition, AttrMap

__all__ ['Spec',
         'AttributeSpec',
         'AttributableSpec',
         'DatasetSpec',
         'GroupSpec',
         'TypeMap',
         'AttrMap',
         'Condition']


def __load_spec(spec):

    spec = spec['fs']['core']['schema']
    
    def build_group(name, d):
        required = True
        myname = name
        if myname[-1] == '?':
            required = False
            myname = myname[:-1]
        if myname[-1] == '/':
            myname = myname[:-1]
        if myname == '*':
            required = False
        desc = d.pop('description', None)
        attributes = d.pop('attributes', None)
        nwb_type = None
        if 'neurodata_type' in attributes:
            nwb_type = value['neurodata_type']['value']
        spec = GroupSpec(name, required=required, doc=desc, nwb_type=nwb_type)
        add_attributes(spec, attributes)
        for key, value in d.items():
            name = key
            if key.rfind('/') == -1:
                spec.set_dataset(build_dataset(name, value))
            else:
                spec.set_group(build_group(name, value))
        return spec
    
    def build_dataset(name, d):
        kwargs = remap_keys(name, d)
        spec = DatasetSpec(name, kwargs.pop('dtype'), **kwargs)
        if 'attributes' in d:
            add_attributes(spec, d['attributes'])
        return spec
    
    def add_attributes(spec, attributes):
        for attr_name, attr_spec in attributes:
            spec.add_attribute(build_attribute(attr_name, attr_spec))
    
    def build_attribute(name, d):
        kwargs = remap_keys(name, d)
        spec = AttributeSpec(name, kwargs.pop('dtype'), **kwargs)
        return spec
    
    def remap_keys(name, d):
        ret = dict()
        ret['required'] = True
        if name == '?':
            ret['required'] = False
            name.
        ret['const'] = d.get('const', None)
        ret['dtype'] = d.get('data_type', None)
        ret['default'] = d.get('value', None)
        ret['doc'] = d.get('description', None)
        ret['dim'] = d.get('dimensions', None)
    
        return ret
    
    def merge_spec(target, source):
        for grp_spec in source.groups:
            target.add_group(grp_spec)
        for dset_spec in source.datasets:
            target.add_group(dset_spec)
        for attr_spec in source.attributes:
            target.add_attribute(attr_spec)
    
    # load File spec
    root = GroupSpec(nwb_type='NwbFile')
    acquisition = root.set_group(build_group('acquisition', spec['/acquisition/']))
    analysis = root.set_group(build_group('analysis', spec['/analysis/']))
    epochs = root.set_group(build_group('epochs', spec['/epochs/']))
    processing = root.set_group(build_group('processing', spec['/processing/']))
    stimulus = root.set_group(build_group('stimulus', spec['/stimulus/']))
    general = root.add_group('general', build_group('general', spec['/general/']))
    extracellular_ephys = general.set_group(build_group('extracellular_ephys?', spec['/extracellular_ephys/?']))
    intracellular_ephys = general.set_group(build_group('intracellular_ephys?', spec['/intracellular_ephys/?']))
    optogenetics = general.set_group(build_group('optogenetics?', spec['/optogenetics/?']))
    optophysiology = general.set_group(build_group('optophysiology?', spec['/optophysiology/?']))
    
    # load TimeSeries specs
    ts_specs = dict()
    ts_types = ts_types.strip().split('\n')
    while ts_types:
        ts_type = ts_types.pop(0)
        ts_dict = spec[ts_type]
        merge = list()
        if 'merge' in ts_dict:
            for merge_type in ts_dict['merge']:
                tmp = ts_specs.get(merge_type, None)
                if tmp:
                    merge.append(tmp)
                else:
                    ts_types.append(ts_type)
                    continue
            
        ts_spec = build_group('*', ts_dict)
        for m in merge:
            merge_spec(m, ts_spec)
        
    # load Module specs
    iface = build_group('*', spec['<Interface>/'])
    mod_specs = dict()
    
    mod_types = mod_types.strip().split('\n')
    for mod in mod_types:
        mod_specs[mod] = build_group(mod, spec[mod])
        merge_spec(mod_specs[mod], iface)
    
    #register with SpecMap
    SpecCatalog.register_spec('NWB', root)
    SpecCatalog.register_spec('Interface', iface)
    for ts_type, ts_spec in ts_specs.items():
        tmp = ts_type[1:len(ts_type)-2]
        SpecCatalog.register_spec(tmp, ts_spec)
    for mod_type, mod_spec in mod_specs.items():
        tmp = mod_type[1:len(mod_type)-1]
        SpecCatalog.register_spec(tmp, mod_spec)
        pass

def __map_types():

    # override default mapping behavior for TimeSeries objects
    ts_attr_map = AttrMap(SpecCatalog.get_spec('TimeSeries'))
    data_map = ts_attr_map.get_map('data')
    ts.map_attr('unit', data_map.get_attribute('unit'))
    ts.map_attr('resolution', data_map.get_attribute('resolution'))
    ts.map_attr('conversion', data_map.get_attribute('conversion'))

    timestamps_map = ts_attr_map.get_map('timestamps')
    ts.map_attr('interval', timestamps_map.get_attribute('interval'))
    ts.map_attr('timestamps_unit', timestamps_map.get_attribute('unit'))

    starting_times_map = ts_attr_map.get_map('starting_time')
    ts.map_attr('rate', starting_times_map.get_attribute('rate'))
    ts.map_attr('rate_unit', ts_attr_map.get_map('starting_time').get_attribute('unit'))
    TypMap.register_map('TimeSeries', ts_attr_map)
    
    for reg_type in SpecCatalog.get_registered_types():
        existing = TypeMap.get_map(reg_type)
        if existing:
            continue
        TypMap.register_map(reg_type, AttrMap(SpecCatalog.get_spec(reg_type))

__load_spec(json.load(pkg_resources.resource_stream(__name__, 'spec.json')))
__map_types()



