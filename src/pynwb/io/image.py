from .. import register_map

from ..image import ImageSeries
from .base import TimeSeriesMap


@register_map(ImageSeries)
class ImageSeriesMap(TimeSeriesMap):

    def __init__(self, spec):
        super(ImageSeriesMap, self).__init__(spec)
        external_file_spec = self.spec.get_dataset('external_file')
        self.map_spec('starting_frame', external_file_spec.get_attribute('starting_frame'))
