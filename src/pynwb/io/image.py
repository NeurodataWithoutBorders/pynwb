import numpy as np

from .. import register_map
from ..image import ImageSeries
from .base import TimeSeriesMap
from .utils import NO_OVERRIDE


@register_map(ImageSeries)
class ImageSeriesMap(TimeSeriesMap):

    def __init__(self, spec):
        super().__init__(spec)
        external_file_spec = self.spec.get_dataset('external_file')
        self.map_spec('starting_frame', external_file_spec.get_attribute('starting_frame'))

        # ``ImageSeries.num_samples`` falls back to the inherited ``TimeSeries.num_samples``
        # property, i.e. ``len(data)``, when the user did not supply a value. Writing that derived
        # value would persist a dataset the user never set, so map the write path to the private
        # ``_num_samples``, which holds a value only when ``num_samples`` was explicitly provided.
        # The read path is untouched, so the dataset still maps to the ``num_samples``
        # constructor argument.
        num_samples_spec = self.spec.get_dataset('num_samples')
        self.map_attr('_num_samples', num_samples_spec)

    @TimeSeriesMap.object_attr('_num_samples')
    def num_samples_attr(self, container, manager):
        num_samples = container._num_samples
        if num_samples is None:
            return NO_OVERRIDE
        # the schema dtype of num_samples is uint32. Cast an in-range value so HDMF writes it as
        # uint32 instead of widening a Python int to uint64 and emitting a DtypeConversionWarning.
        # Out-of-range values are passed through so HDMF reports the mismatch as usual.
        if 0 <= num_samples <= np.iinfo(np.uint32).max:
            return np.uint32(num_samples)
        return num_samples
