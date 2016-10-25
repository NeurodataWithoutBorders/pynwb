from .container import Container

class ElectrodeGroup(Container):
    def __init__(self, name, coord, desc, dev, loc, parent=None):
        super().__init__(parent)
        self._coord = coord
        self._description = description
        self._device = device
        self._location = location

    @property
    def description(self):
        return self._description

    @description.setter
    def set_description(self, description):
        self._description = description

    @property
    def device(self):
        return self._device

    @device.setter
    def set_device(self, device):
        self._device = device

    @property
    def location(self):
        return self._location

    @location.setter
    def set_location(self, location):
        self._location = location

    @property
    def physical_location(self):
        return self._coord

    def set_physical_location(self, x, y, z):
        self._coord = (x,y,z)

