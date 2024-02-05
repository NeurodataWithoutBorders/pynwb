from hdmf.utils import docval, popargs, get_docval, popargs_to_dict

from . import register_class, CORE_NAMESPACE
from .base import TimeSeries
from .core import NWBContainer
from .device import Device


@register_class('OptogeneticStimulusSite', CORE_NAMESPACE)
class OptogeneticStimulusSite(NWBContainer):
    """Optogenetic stimulus site."""

    __nwbfields__ = ('device',
                     'description',
                     'excitation_lambda',
                     'location')

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this stimulus site.'},
            {'name': 'device', 'type': Device, 'doc': 'The device that was used.'},
            {'name': 'description', 'type': str, 'doc': 'Description of site.'},
            {'name': 'excitation_lambda', 'type': float, 'doc': 'Excitation wavelength in nm.'},
            {'name': 'location', 'type': str, 'doc': 'Location of stimulation site.'})
    def __init__(self, **kwargs):
        args_to_set = popargs_to_dict(('device', 'description', 'excitation_lambda', 'location'), kwargs)
        super().__init__(**kwargs)

        for key, val in args_to_set.items():
            setattr(self, key, val)


@register_class('OptogeneticSeries', CORE_NAMESPACE)
class OptogeneticSeries(TimeSeries):
    '''
    Optogenetic stimulus. The data field is in unit of watts.
    '''

    __nwbfields__ = ('site',)

    @docval(*get_docval(TimeSeries.__init__, 'name'),  # required
            {'name': 'data', 'type': ('array_data', 'data', TimeSeries),  # required
             'shape': [(None, ), (None, None)],
             'doc': 'The data values over time.'},
            {'name': 'site', 'type': OptogeneticStimulusSite,  # required
             'doc': 'The site to which this stimulus was applied.'},
            *get_docval(TimeSeries.__init__, 'resolution', 'conversion', 'timestamps', 'starting_time', 'rate',
                        'comments', 'description', 'control', 'control_description', 'offset'))
    def __init__(self, **kwargs):
        site = popargs('site', kwargs)
        kwargs['unit'] = 'watts'
        super().__init__(**kwargs)
        self.site = site
