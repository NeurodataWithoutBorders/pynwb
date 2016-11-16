from .core import Container, properties, docval, getargs




__std_fields = ('name',
                'description',
                'device',
                'location',
                'physical_location',
                'impedance')
@properties(*__std_fields)
class ElectrodeGroup(Container):

    @docval(*Container.__init__.docval['args'],
            {'name': 'name', 'type': (str, int), 'doc': 'the name of this electrode'},
            {'name': 'coord', 'type': tuple, 'doc': 'the x,y,z coordinates of this electrode'},
            {'name': 'desc', 'type': str, 'doc': 'a description for this electrode'},
            {'name': 'dev', 'type': str, 'doc': 'the device this electrode was recorded from on'},
            {'name': 'loc', 'type': str, 'doc': 'a description of the location of this electrode'},
            {'name': 'imp', 'type': float, 'doc': 'the impedance of this electrode', 'default': -1})
    def __init__(self, **kwargs):
        name, coord, desc, dev, loc, imp, parent = getargs("name", "coord", "desc", "dev", "loc", "imp", "parent", **kwargs)
        super(ElectrodeGroup, self).__init__(parent=parent)
        self._name = name
        self._physical_location = coord
        self._description = desc
        self._device = dev
        self._location = loc
        self._impedance = imp
