from . import build, hdf5

def __get_type_map():
    from ..spec import CATALOG
    return build.map.TypeMap(CATALOG)

type_map = __get_type_map()
