from hdmf.common.io.table import DynamicTableMap
from hdmf.common.io.alignedtable import AlignedDynamicTableMap

from .. import register_map
from .base import TimeSeriesMap
from pynwb.icephys import VoltageClampSeries, IntracellularRecordingsTable


@register_map(VoltageClampSeries)
class VoltageClampSeriesMap(TimeSeriesMap):

    def __init__(self, spec):
        super().__init__(spec)

        fields_with_unit = ('capacitance_fast',
                            'capacitance_slow',
                            'resistance_comp_bandwidth',
                            'resistance_comp_correction',
                            'resistance_comp_prediction',
                            'whole_cell_capacitance_comp',
                            'whole_cell_series_resistance_comp')
        for field in fields_with_unit:
            field_spec = self.spec.get_dataset(field)
            self.map_spec('%s__unit' % field, field_spec.get_attribute('unit'))


@register_map(IntracellularRecordingsTable)
class IntracellularRecordingsTableMap(AlignedDynamicTableMap):
    """
    Customize the mapping for AlignedDynamicTable
    """
    def __init__(self, spec):
        super().__init__(spec)

    @DynamicTableMap.object_attr('electrodes')
    def electrodes(self, container, manager):
        return container.category_tables.get('electrodes', None)

    @DynamicTableMap.object_attr('stimuli')
    def stimuli(self, container, manager):
        return container.category_tables.get('stimuli', None)

    @DynamicTableMap.object_attr('responses')
    def responses(self, container, manager):
        return container.category_tables.get('responses', None)
