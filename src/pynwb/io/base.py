from hdmf.build import LinkBuilder

from .core import NWBContainerMapper
from .. import register_map
from ..base import TimeSeries, ProcessingModule


@register_map(ProcessingModule)
class ModuleMap(NWBContainerMapper):

    def __init__(self, spec):
        super().__init__(spec)
        containers_spec = self.spec.get_neurodata_type('NWBDataInterface')
        table_spec = self.spec.get_neurodata_type('DynamicTable')
        self.map_spec('data_interfaces', containers_spec)
        self.map_spec('data_interfaces', table_spec)


@register_map(TimeSeries)
class TimeSeriesMap(NWBContainerMapper):

    def __init__(self, spec):
        super().__init__(spec)
        data_spec = self.spec.get_dataset('data')
        self.map_spec('unit', data_spec.get_attribute('unit'))
        self.map_spec('resolution', data_spec.get_attribute('resolution'))
        self.map_spec('conversion', data_spec.get_attribute('conversion'))
        self.map_spec('offset', data_spec.get_attribute('offset'))
        self.map_spec('continuity', data_spec.get_attribute('continuity'))

        timestamps_spec = self.spec.get_dataset('timestamps')
        self.map_spec('timestamps_unit', timestamps_spec.get_attribute('unit'))
        self.map_spec('interval', timestamps_spec.get_attribute('interval'))

        startingtime_spec = self.spec.get_dataset('starting_time')
        self.map_spec('starting_time_unit', startingtime_spec.get_attribute('unit'))
        self.map_spec('rate', startingtime_spec.get_attribute('rate'))

        # TODO map the sync group to something
        sync_spec = self.spec.get_group('sync')
        self.unmap(sync_spec)

    @NWBContainerMapper.object_attr("timestamps")
    def timestamps_attr(self, container, manager):
        ret = container.fields.get('timestamps')
        if isinstance(ret, TimeSeries):
            owner = ret
            curr = owner.fields.get('timestamps')
            while isinstance(curr, TimeSeries):
                owner = curr
                curr = owner.fields.get('timestamps')
            ts_builder = manager.build(owner)
            tstamps_builder = ts_builder['timestamps']
            ret = LinkBuilder(tstamps_builder, 'timestamps')
        return ret

    @NWBContainerMapper.constructor_arg("timestamps")
    def timestamps_carg(self, builder, manager):
        tstamps_builder = builder.get('timestamps')
        if tstamps_builder is None:
            return None
        if isinstance(tstamps_builder, LinkBuilder):
            # if the parent of our target is available, return the parent object
            # Otherwise, return the dataset in the target builder
            #
            # NOTE: it is not available when data is externally linked
            # and we haven't explicitly read that file
            target = tstamps_builder.builder
            if target.parent is not None:
                return manager.construct(target.parent)
            else:
                return target.data
        else:
            return tstamps_builder.data

    @NWBContainerMapper.object_attr("data")
    def data_attr(self, container, manager):
        ret = container.fields.get('data')
        if isinstance(ret, TimeSeries):
            owner = ret
            curr = owner.fields.get('data')
            while isinstance(curr, TimeSeries):
                owner = curr
                curr = owner.fields.get('data')
            data_builder = manager.build(owner)
            ret = LinkBuilder(data_builder['data'], 'data')
        return ret

    @NWBContainerMapper.constructor_arg("data")
    def data_carg(self, builder, manager):
        # handle case where a TimeSeries is read and missing data
        timeseries_cls = manager.get_cls(builder)
        data_builder = builder.get('data')
        if data_builder is None:
            return timeseries_cls.DEFAULT_DATA
        if isinstance(data_builder, LinkBuilder):
            # NOTE: parent is not available when data is externally linked
            # and we haven't explicitly read that file
            target = data_builder.builder
            if target.parent is not None:
                return manager.construct(target.parent)
            else:
                return target.data
        return data_builder.data

    @NWBContainerMapper.constructor_arg("unit")
    def unit_carg(self, builder, manager):
        # handle case where a TimeSeries is read and missing unit
        timeseries_cls = manager.get_cls(builder)
        data_builder = builder.get('data')
        if data_builder is None:
            return timeseries_cls.DEFAULT_UNIT
        if isinstance(data_builder, LinkBuilder):
            # NOTE: parent is not available when data is externally linked
            # and we haven't explicitly read that file
            target = data_builder.builder
            if target.parent is not None:
                data_builder = manager.construct(target.parent)
            else:
                data_builder = target
        if isinstance(data_builder, TimeSeries):  # Data linked in another timeseries
            unit_value = data_builder.unit
        else:  # DatasetBuilder owned by this timeseries
            unit_value = data_builder.attributes.get('unit')
        if unit_value is None:
            return timeseries_cls.DEFAULT_UNIT
        return unit_value
