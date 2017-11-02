import numpy as np
from .. import ObjectMapper
from pynwb.legacy import register_map
from pynwb.image import ImageSeries

@register_map(ImageSeries)
class ImageSeriesMap(ObjectMapper):

    @ObjectMapper.constructor_arg('data')
    def carg_data(self, *args):
        builder = args[0]
        if builder.name in ('corrected',):
            return np.array([-1.])