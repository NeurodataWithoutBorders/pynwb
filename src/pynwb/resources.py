from hdmf.common import ExternalResources as hdmf_ExternalResources
from . import get_type_map as tm
from hdmf.utils import docval, get_docval


class ExternalResources(hdmf_ExternalResources):
    @docval(*get_docval(hdmf_ExternalResources.__init__))
    def __init__(self, **kwargs):
        kwargs['type_map'] = tm()
        super().__init__(**kwargs)
