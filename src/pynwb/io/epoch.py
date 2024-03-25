from hdmf.build import LinkBuilder
from hdmf.common.table import VectorData
from hdmf.common.io.table import DynamicTableMap

from .. import register_map
from pynwb.epoch import TimeIntervals
from pynwb.base import TimeSeriesReferenceVectorData


@register_map(TimeIntervals)
class TimeIntervalsMap(DynamicTableMap):

    @DynamicTableMap.constructor_arg('columns')
    def columns_carg(self, builder, manager):
        # handle the case when a TimeIntervals is read with a non-TimeSeriesReferenceVectorData "timeseries" column
        # this is the case for NWB schema v2.4 and earlier, where the timeseries column was a regular VectorData.
        timeseries_builder = builder.get('timeseries')

        # handle the case when the TimeIntervals has a "timeseries" column that is a link (e.g., it exists in
        # a different file that was shallow copied to this file).
        if isinstance(timeseries_builder, LinkBuilder):
            timeseries_builder = timeseries_builder.builder

        # if we have a timeseries column and the type is VectorData instead of TimeSeriesReferenceVectorData
        if (timeseries_builder is not None and
                timeseries_builder.attributes['neurodata_type'] != 'TimeSeriesReferenceVectorData'):
            # override builder attributes
            timeseries_builder.attributes['neurodata_type'] = 'TimeSeriesReferenceVectorData'
            timeseries_builder.attributes['namespace'] = 'core'
            # construct new columns list
            columns = list()
            for dset_builder in builder.datasets.values():
                dset_obj = manager.construct(dset_builder)  # these have already been constructed
                # go through only the column datasets and replace the 'timeseries' column class in-place.
                if isinstance(dset_obj, VectorData):
                    if dset_obj.name == 'timeseries':
                        # replacing the class in-place is possible because the VectorData and
                        # TimeSeriesReferenceVectorData have the same memory layout and the old and new
                        # schema are compatible (i.e., only the neurodata_type was changed in 2.5)
                        dset_obj.__class__ = TimeSeriesReferenceVectorData
                        # Execute init logic specific for TimeSeriesReferenceVectorData
                        dset_obj._init_internal()
                    columns.append(dset_obj)
            # overwrite the columns constructor argument
            return columns
        # do not override
        return None
