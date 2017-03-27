from .builders import GroupBuilder
from .builders import DatasetBuilder
from .builders import LinkBuilder
from .builders import ExternalLinkBuilder

from .map import ObjectMapper
from .map import BuildManager

def get_type_map():
    from pynwb.spec import CATALOG
    from .map import TypeMap
    return TypeMap(CATALOG)
