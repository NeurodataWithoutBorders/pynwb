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

from . import base as __base
from . import behavior as __behavior
from . import ecephys as __ecephys
from . import epoch as __epoch
from . import icephys as __icephys
from . import image as __image
from . import misc as __misc
from . import ogen as __ogen
from . import ophys as __ophys
from . import retinotopy as __retinotopy
