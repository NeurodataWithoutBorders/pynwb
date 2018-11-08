from .. import register_map
from .core import DynamicTableMap

from pynwb.misc import Units


@register_map(Units)
class UnitsMap(DynamicTableMap):

    @DynamicTableMap.object_attr("electrode")
    def electrodes_column(self, container, manager):
        ret = container.get('electrode')
        if ret is None:
            return ret
        # set the electrode table if it hasn't been set yet
        if ret.table is None:
            ret.table = self.get_nwb_file(container).electrodes
        return ret
