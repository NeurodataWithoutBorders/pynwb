from .base import TimeSeriesMap
from ..image import ImageSeries
from ..tools import register_map


@register_map(ImageSeries)
class ImageSeriesMap(TimeSeriesMap):

    def __init__(self, spec):
        super().__init__(spec)
        external_file_spec = self.spec.get_dataset('external_file')
        self.map_spec('starting_frame', external_file_spec.get_attribute('starting_frame'))
