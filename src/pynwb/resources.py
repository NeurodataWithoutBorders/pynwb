from hdmf.common import HERD as hdmf_HERD
from . import get_type_map as tm
from hdmf.utils import docval, get_docval


class HERD(hdmf_HERD):
    """
    HDMF External Resources Data Structure.
    A table for mapping user terms (i.e. keys) to resource entities.
    """
    @docval(*get_docval(hdmf_HERD.__init__))
    def __init__(self, **kwargs):
        kwargs['type_map'] = tm()
        super().__init__(**kwargs)
