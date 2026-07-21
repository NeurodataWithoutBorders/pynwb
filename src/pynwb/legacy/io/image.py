import numpy as np

from pynwb.image import ImageSeries

from .. import ObjectMapper, register_map
from pynwb.io.utils import NO_OVERRIDE


@register_map(ImageSeries)
class ImageSeriesMap(ObjectMapper):

    @ObjectMapper.constructor_arg('data')
    def carg_data(self, *args):
        builder = args[0]
        if builder.name in ('corrected',):
            return np.array([-1.])
        return NO_OVERRIDE
