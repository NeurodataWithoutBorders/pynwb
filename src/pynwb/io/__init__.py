#from .. import spec, map, h5tools, write, utils
from .tools import spec, map

from pkg_resources import resource_filename
import os
import glob
import ruamel.yaml as yaml

spec_catalog = spec.SpecCatalog()
type_map = map.TypeMap(spec_catalog)

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
            type_map.auto_register(spec_obj)

from . import base, behavior, ecephys, epoch, icephys, image, misc, ogen, ophys, retinotopy
