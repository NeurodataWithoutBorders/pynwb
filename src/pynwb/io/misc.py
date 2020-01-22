from .. import register_map
from hdmf.common.io.table import DynamicTableMap

from pynwb.misc import Units


@register_map(Units)
class UnitsMap(DynamicTableMap):

    def __init__(self, spec):
        super().__init__(spec)

        waveform_mean_spec = self.spec.get_dataset('waveform_mean')
        self.map_spec('waveform_mean_rate', waveform_mean_spec.get_attribute('sampling_rate'))
        self.map_spec('waveform_mean_unit', waveform_mean_spec.get_attribute('unit'))

        waveform_sd_spec = self.spec.get_dataset('waveform_sd')
        self.map_spec('waveform_sd_rate', waveform_sd_spec.get_attribute('sampling_rate'))
        self.map_spec('waveform_sd_unit', waveform_sd_spec.get_attribute('unit'))

    @DynamicTableMap.object_attr("electrodes")
    def electrodes_column(self, container, manager):
        ret = container.get('electrodes')
        if ret is None:
            return ret
        # set the electrode table if it hasn't been set yet
        if ret.target.table is None:
            ret.target.table = self.get_nwb_file(container).electrodes
        return ret
