from hdmf.common import HERD as hdmf_HERD
from . import get_type_map as tm
from hdmf.utils import docval, get_docval, AllowPositional

__all__ = ['HERD']

class HERD(hdmf_HERD):
    """
    HDMF External Resources Data Structure.
    A table for mapping user terms (i.e. keys) to resource entities.
    """
    @docval(*get_docval(hdmf_HERD.__init__),
            allow_positional=AllowPositional.WARNING,)
    def __init__(self, **kwargs):
        kwargs['type_map'] = tm()
        super().__init__(**kwargs)
