from .. import register_map
from .core import DynamicTableMap

from pynwb.misc import Units


@register_map(Units)
class UnitsMap(DynamicTableMap):

    @DynamicTableMap.object_attr("electrodes")
    def electrodes_column(self, container, manager):
        ret = container.get('electrodes')
        if ret is None:
            return ret
        # set the electrode table if it hasn't been set yet
        if ret.target.table is None:
            ret.target.table = self.get_nwb_file(container).electrodes
        return ret
