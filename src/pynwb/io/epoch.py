# from .. import register_map
#
# from pynwb.base import TimeSeriesReference, TimeSeriesReferenceVectorData
# from pynwb.epoch import TimeIntervals
# from hdmf.build import GroupBuilder, DatasetBuilder, BuildManager
# from hdmf.build.manager import Proxy
# from hdmf.common import VectorData, VectorIndex
# from hdmf.common.io.table import DynamicTableMap
# from hdmf.container import AbstractContainer
# from hdmf.utils import call_docval_func, docval
#

# @register_map(TimeIntervals)
# class TimeIntervalsMap(DynamicTableMap):

    # TODO both approaches (override construct, or define columns_carg) work independently (comment one out and use
    # the other) but the first approach is hacky since it overrides construct() which is not meant to be public
    # and the second approach does not set the object ID of the new TimeSeriesReferenceVectorData to be the same
    # as the VectorData on disk. TODO update HDMF construct() to allow alteration of the builder, like a prebuild hook.

    # # override construct() to change the neurodata_type of the 'timeseries' column from VectorData to
    # # TimeSeriesReferenceVectorData - TODO make this not hacky
    # @docval({'name': 'builder', 'type': (DatasetBuilder, GroupBuilder),
    #          'doc': 'the builder to construct the AbstractContainer from'},
    #         {'name': 'manager', 'type': BuildManager, 'doc': 'the BuildManager for this build'},
    #         {'name': 'parent', 'type': (Proxy, AbstractContainer),
    #          'doc': 'the parent AbstractContainer/Proxy for the AbstractContainer being built', 'default': None})
    # def construct(self, **kwargs):
    #     builder = kwargs['builder']
    #     timeseries_builder = builder.get('timeseries')
    #     if timeseries_builder.attributes['neurodata_type'] != 'TimeSeriesReferenceVectorData':
    #         # override builder attributes
    #         timeseries_builder.attributes['neurodata_type'] = 'TimeSeriesReferenceVectorData'
    #         timeseries_builder.attributes['namespace'] = 'core'
    #     obj = call_docval_func(super().construct, kwargs)
    #     return obj

    # @DynamicTableMap.constructor_arg('columns')
    # def columns_carg(self, builder, manager):
    #     # handle case when a TimeIntervals is read with a non-TimeSeriesReferenceVectorData "timeseries" column
    #     # these data are read completely here (not lazily)
    #     timeseries_builder = builder.get('timeseries')
    #     if timeseries_builder.attributes['neurodata_type'] != 'TimeSeriesReferenceVectorData':
    #         # override builder attributes
    #         timeseries_builder.attributes['neurodata_type'] = 'TimeSeriesReferenceVectorData'
    #         timeseries_builder.attributes['namespace'] = 'core'
    #         # construct new columns list
    #         columns = list()
    #         for dset_builder in builder.datasets.values():
    #             dset_obj = manager.construct(dset_builder)
    #             # go through only the column datasets and replace the 'timeseries_index' and 'timeseries' columns
    #             # without changing the order
    #             if isinstance(dset_obj, VectorData):
    #                 if dset_obj.name == 'timeseries':
    #                     pass
    #                 elif dset_obj.name == 'timeseries_index':
    #                     # TODO do we need to update children?
    #                     new_ts_column = TimeSeriesReferenceVectorData(
    #                         name='timeseries',
    #                         description='index into a TimeSeries object',
    #                     )  # TODO match object ID??
    #                     new_ts_index_column = VectorIndex(
    #                         name='timeseries_index',
    #                         data=list(),
    #                         target=new_ts_column
    #                     )  # TODO match object ID??
    #                     for row in dset_obj:
    #                         new_row = list()
    #                         for tup in row:
    #                             new_row.append(TimeSeriesReference(*tup))
    #                         new_ts_index_column.add_vector(new_row)
    #
    #                     columns.append(new_ts_index_column)
    #                     columns.append(new_ts_column)
    #                 else:
    #                     columns.append(dset_obj)
    #
    #         return columns
    #
    #     return None  # do not override
