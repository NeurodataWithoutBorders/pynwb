from pkg_resources import resource_string as _resource_string
from pickle import loads as _loads
from .core import get_timeseries, TimeSeriesValidator

# load the pickled schema, and create TimeSeries validator objects
# to be used for validating HDF5 files during read/write operations
with _resource_stream(__name__, 'schema.pkl') as schema_stream:
    from sys import module
    schema = _loads(schema_stream)
    this_module = module[__name__]
    for spec in get_timeseries(schema):
        validator = TimeSeriesValidator(spec['name'], spec['groups'], pec['datasets'], spec['attributes'])
        setattr(this_module, spec['name'], validator)


