from form.build import ObjectMapper
from .. import register_map

from ..ecephys import ElectrodeTable

@register_map(ElectrodeTable)
class ElectrodeTableMap(ObjectMapper):
    def __init__(self, spec):
        super(ElectrodeTableMap, self).__init__(spec)
