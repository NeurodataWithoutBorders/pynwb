from hdmf.common.io.table import DynamicTableMap

from .. import register_map
from pynwb.misc import Units


@register_map(Units)
class UnitsMap(DynamicTableMap):

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
        waveform_columns = ('waveform_mean', 'waveform_sd', 'waveforms')
        stats = [builder[column].attributes.get(attribute) for column in waveform_columns if column in builder]
        if not stats:
            return None
        populated_stats = [stat for stat in stats if stat is not None]
        if len(set(populated_stats)) > 1:
            # throw warning
            pass
        if populated_stats:
            return populated_stats[0]
        return None

    @DynamicTableMap.object_attr("electrodes")
    def electrodes_column(self, container, manager):
        ret = container.get('electrodes')
        if ret is None:
            return ret
        # set the electrode table if it hasn't been set yet
        if ret.target.table is None:
            ret.target.table = container.get_ancestor('NWBFile').electrodes
        return ret
