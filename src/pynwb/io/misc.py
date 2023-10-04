from hdmf.common.io.table import DynamicTableMap

from .. import register_map
from pynwb.misc import Units


@register_map(Units)
class UnitsMap(DynamicTableMap):

    def __init__(self, spec):
        super().__init__(spec)

    @DynamicTableMap.constructor_arg('resolution')
    def resolution_carg(self, builder, manager):
        if 'spike_times' in builder:
            return builder['spike_times'].attributes.get('resolution')
        return None

    @DynamicTableMap.constructor_arg('waveform_rate')
    def waveform_rate_carg(self, builder, manager):
        return self._get_waveform_stat(builder, 'sampling_rate')

    @DynamicTableMap.constructor_arg('waveform_unit')
    def waveform_unit_carg(self, builder, manager):
        return self._get_waveform_stat(builder, 'unit')

    def _get_waveform_stat(self, builder, attribute):
        if 'waveform_mean' not in builder and 'waveform_sd' not in builder:
            return None
        mean_stat = None
        sd_stat = None
        if 'waveform_mean' in builder:
            mean_stat = builder['waveform_mean'].attributes.get(attribute)
        if 'waveform_sd' in builder:
            sd_stat = builder['waveform_sd'].attributes.get(attribute)
        if mean_stat is not None and sd_stat is not None:
            if mean_stat != sd_stat:
                # throw warning
                pass
        return mean_stat

    @DynamicTableMap.object_attr("electrodes")
    def electrodes_column(self, container, manager):
        ret = container.get('electrodes')
        if ret is None:
            return ret
        # set the electrode table if it hasn't been set yet
        if ret.target.table is None:
            ret.target.table = container.get_ancestor('NWBFile').electrodes
        return ret
