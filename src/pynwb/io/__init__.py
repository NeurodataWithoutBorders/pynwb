from . import build, hdf5
from .io import NWBReader, NWBWriter, NWBIO

def __get_type_map():
    from pynwb.core import NWBContainer
    ret = build.get_type_map()
    ret.neurodata_type(NWBContainer)(build.ObjectMapper)
    return ret

TYPE_MAP = __get_type_map()

def BuildManager(type_map=TYPE_MAP):
    return build.BuildManager(type_map)
