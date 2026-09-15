from .. import register_map

from pynwb.icephys import SweepTable, VoltageClampSeries
from hdmf.common.io.table import DynamicTableMap
from .base import TimeSeriesMap


@register_map(SweepTable)
class SweepTableMap(DynamicTableMap):
    pass


@register_map(VoltageClampSeries)
class VoltageClampSeriesMap(TimeSeriesMap):

    def __init__(self, spec):
        super(VoltageClampSeriesMap, self).__init__(spec)

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
