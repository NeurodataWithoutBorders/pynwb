from .container import NWBContainer

#@nwbproperties(*__interface_std_fields)
class Interface(NWBContainer):
    """ Interfaces represent particular processing tasks and they publish
        (ie, make available) specific types of data. Each is required
        to supply a minimum of specifically named data, but all can store 
        data beyond this minimum

        Interfaces should be created through Module.create_interface().
        They should not be created directly
    """
    __nwbfields__ = ('help_statement',
                     'neurodata_type',
                     'source',
                     'interface')

    _neurodata_type = "Interface"

    _interface = "Interface"

    _help = None

    def __init__(self, source=None):
        #Arguments:
        #    *name* (text) name of interface (may be class name)
        #    *module* (*Module*) Reference to parent module object that 
        #       interface belongs to
        #    *spec* (dict) dictionary structure defining module specification
        #self.module = module
        #self.name = name
        #self.nwb = module.nwb
        #self.spec = copy.deepcopy(spec)
        ## timeseries that are added to interface directly
        #self.defined_timeseries = {}
        ## timeseries that exist elsewhere and are HDF5-linked
        #self.linked_timeseries = {}
        #if name in module.mod_folder:
        #    self.nwb.fatal_error("Interface %s already exists in module %s" % (name, module.name))
        #self.iface_folder = module.mod_folder.create_group(name)
        #self.serial_num = -1
        #self.finalized = False
        self._source = source
        self._timeseries = dict()

    def full_path(self):
        """ Returns HDF5 path to this interface

            Arguments:
                *none*

            Returns:
                (text) the HDF5 path to the interface
        """
        return "processing/" + self.module.name + "/" + self.name

    def create_timeseries(self, name, ts_type="TimeSeries"):
        ts_class = getattr(nwbts, ts_type, None)
        if not ts_class:
            raise ValueError("%s is an invalid TimeSeries type" % ts_type)
        self.timeseries[name] = ts_class(name)
        return self._timeseries[name]

    def add_timeseries(self, ts, name=None):
        """ Add a previously-defined *TimeSeries* to the interface. It will
            be added as an HDF5 link

            Arguments:
                *ts_name* (text) name of time series as it will appear in
                the interface

                *path* (text) path to the time series

            Returns:
                *nothing*
        """
        if name:
            self._timeseries[name] = ts
        else:
            self._timeseries[ts.name] = ts

    def get_timeseries(self):
        return timeseries

    def set_source(self, src):
        """ Identify source(s) for the data provided in the module.
            This can be one or more other modules, or time series
            in acquisition or stimulus

            Arguments:
                *src* (text) Path to objects providing data that the
                data here is based on

            Returns:
                *nothing*
        """
        self._source = src
