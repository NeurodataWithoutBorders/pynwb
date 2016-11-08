
class ObjectDigester(object):

    @classmethod
    def container_type(cls, container_type):
        if not hasattr(cls, 'operations'):
            setattr(cls, 'operations', dict())
            setattr(cls, 'results', dict())

        def _dec(func):
            cls.operations[container_type] = func
            return func
        return _dec

    def digest(self, item):
        self._builder = GroupBuilder()
        self.__digest_aux(self.transform(item.__class__), item)
        self.rendered[item] = self._builder
        return self._builder

    def __digest_aux(self, value, item):
        if container_cls is object:
            return
        for bs_cls in container_type.__bases__:
            self.__render_aux(bs_cls, item)
        if value in self.operations:
            func = self.operations[value]
            func(item)

class GroupParser(object):

    @classmethod
    def parse(cls, container_class, container_type):
        if not hasattr(cls, 'parsers'):
            setattr(cls, 'parsers', dict())
        if container_class not in cls.parsers:
            cls.parsers[container_class] = dict()
        
        def _dec(func):
            cls.parsers[container_class][container_type] = func
            return func

        return _dec
        


class Hdf5Parser(GroupParser):
    

    @classmethod
    def group_name(cls, container_type):
        cls.__setup_cls()

        def _dec(func):
            cls.group_name_operations[container_type] = func
            return func
        return _dec

    @classmethod
    def attribute_value(cls, attr, value):
        cls.__setup_cls()
        if attr not in cls.attr_value_operations:
            cls.attr_value_operations[attr] = dict()

        def _dec(func):
            cls.attr_value_operations[attr][value] = func
            return func
        return _dec


    def parse_timeseries(self, group):
        # do some stuff, like read ancesty to figure out class, and create
        # object and call setters, etc
        ancestry = group.attr.get('ancestry')
        ts_class_name = ancestry.split(',')[-1]
        ts_mod = None #TODO: add code to retrieve module object
        ts_class = getattr(ts_mod, ts_class_name)
        desc = group.attr.get('description')
        ts = ts_class(group.name, desc)
        # TODO: add code to figure out how to handle links
        # we will need to link to the TimeSeries object that 
        # actually holds the timestamps
        ts.set_data(group['data'])
        ts.set_timestamps(group['timestamps']) 
        
        ts = self.builders['timeseries'][ts_class_name](self, group, ts)
    
    @parse('TimeSeries', 'ElectricalSeries')
    def parse_electricalseries(self, group, ts=None):
        if not ts:
            ts = self.parse_timeseries(group)
        ts.set_electrodes(list(group['electrode_idx']))
        return ts
        
    
    
    def parse_module(group):
        # do some stuff like 
    
        pass

    



class TimeSeriesHdf5Parser(Hdf5Parser):
    pass



@TimeSeriesHdf5Parser.ancestry('TimeSeries')
def __parse_timeseries(dset):
    pass
