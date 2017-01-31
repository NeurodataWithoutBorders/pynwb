from .base import TimeSeries
from .core import docval, getargs, NWBContainer
from .image import ImageSeries

class OptogeneticSeries(ImageSeries):
    pass

class OptogeneticSite(NWBContainer):
    # see /general/optogenetics/<site_X> spec
    pass
