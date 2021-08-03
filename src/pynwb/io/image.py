from .. import register_map
from ..image import ImageSeries, ExternalImageSeries
from .base import TimeSeriesMap
from .core import NWBContainerMapper


@register_map(ImageSeries)
class ImageSeriesMap(TimeSeriesMap):

    def __init__(self, spec):
        super().__init__(spec)
        external_file_spec = self.spec.get_dataset('external_file')
        self.map_spec('starting_frame', external_file_spec.get_attribute('starting_frame'))


@register_map(ExternalImageSeries)
class ExternalImageSeriesMap(NWBContainerMapper):

    def __init__(self, spec):
        super().__init__(spec)

        timestamps_spec = self.spec.get_dataset('timestamps')
        self.map_spec('timestamps_unit', timestamps_spec.get_attribute('unit'))
        self.map_spec('interval', timestamps_spec.get_attribute('interval'))

        startingtime_spec = self.spec.get_dataset('starting_time')
        self.map_spec('starting_time_unit', startingtime_spec.get_attribute('unit'))
        self.map_spec('rate', startingtime_spec.get_attribute('rate'))
