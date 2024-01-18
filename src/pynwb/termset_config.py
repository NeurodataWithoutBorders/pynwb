from hdmf.term_set import TermSetConfigurator as hdmf_TermSetConfigurator
from hdmf.utils import docval


class NWBTermSetConfigurator(hdmf_TermSetConfigurator):
    """

    """
    @docval({'name': 'path', 'type': str, 'doc': 'Path to the configuartion file.',
             'default': 'src/pynwb/config/nwb_config.yaml'})
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
