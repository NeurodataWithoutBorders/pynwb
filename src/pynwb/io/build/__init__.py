from .h5tools import GroupBuilder
from .h5tools import DatasetBuilder
from .h5tools import LinkBuilder
from .h5tools import ExternalLinkBuilder
from .h5tools import DataChunkIterator

from .map import ObjectMapper
from .map import BuildManager

def get_type_map():
    from pynwb.spec import CATALOG
    from .map import TypeMap
    return TypeMap(CATALOG)
