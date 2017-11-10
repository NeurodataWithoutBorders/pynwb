from pynwb.behavior import BehavioralTimeSeries, PupilTracking
from pynwb.image import IndexSeries

from .. import ObjectMapper, register_map


@register_map(BehavioralTimeSeries)
class BehavioralTimeSeriesMap(ObjectMapper):

    @ObjectMapper.constructor_arg('time_series')
    def carg_time_series(self, *args):

        builder = args[0]
        manager = args[1]

        subspecs = self.hack_get_subspec_values(builder, self.spec, manager)
        for subspec, value in subspecs.items():
            const_arg = self.get_const_arg(subspec)
            if const_arg == 'time_series':
                for x in value:
                    if not isinstance(x, IndexSeries):
                        return x


@register_map(PupilTracking)
class PupilTrackingMap(ObjectMapper):

    @ObjectMapper.constructor_arg('time_series')
    def carg_time_series(self, *args):

        builder = args[0]
        manager = args[1]

        subspecs = self.hack_get_subspec_values(builder, self.spec, manager)
        for subspec, value in subspecs.items():
            const_arg = self.get_const_arg(subspec)
            if const_arg == 'time_series':
                for x in value:
                    if not isinstance(x, IndexSeries):
                        return x
