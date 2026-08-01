import warnings

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
        """Get the value of an attribute shared by the waveform columns of a Units table.

        The `Units` container holds one `waveform_rate` and one `waveform_unit` for the whole table, while the
        file stores a `sampling_rate` and `unit` attribute on each waveform column. When the columns disagree,
        the value of the first populated column is used and a warning is raised.
        """
        waveform_columns = ('waveform_mean', 'waveform_sd', 'waveforms')
        stats = {column: builder[column].attributes.get(attribute)
                 for column in waveform_columns if column in builder}
        populated_stats = {column: value for column, value in stats.items() if value is not None}
        if not populated_stats:
            return None
        first_column, first_value = next(iter(populated_stats.items()))
        if len(set(populated_stats.values())) > 1:
            warnings.warn(
                f"The '{attribute}' attribute differs across the waveform columns of Units "
                f"'{builder.name}': {populated_stats}. Using the value of '{first_column}'.",
                UserWarning,
                stacklevel=2
            )
        return first_value

    @DynamicTableMap.object_attr("electrodes")
    def electrodes_column(self, container, manager):
        ret = container.get('electrodes')
        if ret is None:
            return ret
        # set the electrode table if it hasn't been set yet
        if ret.target.table is None:
            ret.target.table = container.get_ancestor('NWBFile').electrodes
        return ret
