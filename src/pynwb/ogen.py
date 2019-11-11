from hdmf.utils import docval, popargs, get_docval, call_docval_func

from . import register_class, CORE_NAMESPACE
from .base import TimeSeries
from .core import NWBContainer
from .device import Device


@register_class('OptogeneticStimulusSite', CORE_NAMESPACE)
class OptogeneticStimulusSite(NWBContainer):
    '''
    '''

    __nwbfields__ = ('device',
                     'description',
                     'excitation_lambda',
                     'location')

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this stimulus site'},
            {'name': 'device', 'type': Device, 'doc': 'the device that was used'},
            {'name': 'description', 'type': str, 'doc': 'Description of site.'},
            {'name': 'excitation_lambda', 'type': 'float', 'doc': 'Excitation wavelength in nm.'},
            {'name': 'location', 'type': str, 'doc': 'Location of stimulation site.'})
    def __init__(self, **kwargs):
        device, description, excitation_lambda, location = popargs(
            'device', 'description', 'excitation_lambda', 'location', kwargs)
        call_docval_func(super(OptogeneticStimulusSite, self).__init__, kwargs)
        self.device = device
        self.description = description
        self.excitation_lambda = excitation_lambda
        self.location = location


@register_class('OptogeneticSeries', CORE_NAMESPACE)
class OptogeneticSeries(TimeSeries):
    '''
    Optogenetic stimulus. The data field is in unit of watts.
    '''

    __nwbfields__ = ('site',)

    @docval(*get_docval(TimeSeries.__init__, 'name'),  # required
            {'name': 'data', 'type': ('array_data', 'data', TimeSeries), 'shape': (None, ),  # required
             'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames'},
            {'name': 'site', 'type': OptogeneticStimulusSite,  # required
             'doc': 'The site to which this stimulus was applied.'},
            *get_docval(TimeSeries.__init__, 'resolution', 'conversion', 'timestamps', 'starting_time', 'rate',
                        'comments', 'description', 'control', 'control_description'))
    def __init__(self, **kwargs):
        name, data, site = popargs('name', 'data', 'site', kwargs)
        super(OptogeneticSeries, self).__init__(name, data, 'watts', **kwargs)
        self.site = site
