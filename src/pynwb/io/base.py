from .core import NWBContainerMapper
from .. import register_map

from ..base import TimeSeries, ProcessingModule
from hdmf.build import LinkBuilder


@register_map(ProcessingModule)
class ModuleMap(NWBContainerMapper):

    def __init__(self, spec):
        super(ModuleMap, self).__init__(spec)
        containers_spec = self.spec.get_neurodata_type('NWBDataInterface')
        table_spec = self.spec.get_neurodata_type('DynamicTable')
        self.map_spec('data_interfaces', containers_spec)
        self.map_spec('data_interfaces', table_spec)

    @NWBContainerMapper.constructor_arg('name')
    def name(self, builder, manager):
        return builder.name


@register_map(TimeSeries)
class TimeSeriesMap(NWBContainerMapper):

    def __init__(self, spec):
        super(TimeSeriesMap, self).__init__(spec)
        data_spec = self.spec.get_dataset('data')
        self.map_spec('unit', data_spec.get_attribute('unit'))
        self.map_spec('resolution', data_spec.get_attribute('resolution'))
        self.map_spec('conversion', data_spec.get_attribute('conversion'))

        timestamps_spec = self.spec.get_dataset('timestamps')
        self.map_spec('timestamps_unit', timestamps_spec.get_attribute('unit'))
        self.map_spec('interval', timestamps_spec.get_attribute('interval'))

        startingtime_spec = self.spec.get_dataset('starting_time')
        self.map_spec('starting_time_unit', startingtime_spec.get_attribute('unit'))
        self.map_spec('rate', startingtime_spec.get_attribute('rate'))

        # TODO map the sync group to something
        sync_spec = self.spec.get_group('sync')
        self.unmap(sync_spec)

    @NWBContainerMapper.constructor_arg('name')
    def name(self, builder, manager):
        return builder.name

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
            if tstamps_builder.builder.parent is not None:
                target = tstamps_builder.builder
                return manager.construct(target.parent)
            else:
                return tstamps_builder.builder.data
        else:
            return tstamps_builder.data
