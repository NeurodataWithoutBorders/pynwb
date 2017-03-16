from . import spec, map, h5tools, write, utils

from pkg_resources import resource_filename
import os
import glob
import ruamel.yaml as yaml
#import importlib
#from .spec import Spec, AttributeSpec, BaseStorageSpec, DatasetSpec, GroupSpec, SpecCatalog
#from .map import TypeMap, Condition, AttrMap


__data_dir_path = resource_filename(__name__, '../data')
__type_name_map_path = resource_filename(__name__, '../type_name_map.yaml')
__type_name_map = dict()
if os.path.exists(__type_name_map_path):
    with open(__type_name_map_path, 'r') as stream:
        __type_name_map = yaml.safe_load(stream)

for path in glob.glob('%s/*.{yaml,json}' % __data_dir_path):
    with open(path, 'r') as stream:
        for obj in yaml.safe_load(stream):
            spec_obj = spec.GroupSpec.build_spec(obj)
            spec.SpecCatalog.auto_register(spec_obj)

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

#with open(spec_path) as spec_in:
#    __load_spec(json.load(spec_in))
#__map_types()



