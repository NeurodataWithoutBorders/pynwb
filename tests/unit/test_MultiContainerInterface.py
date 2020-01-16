from hdmf.utils import docval, get_docval
from pynwb.file import MultiContainerInterface, NWBDataInterface
from pynwb.testing import TestCase


class Node(NWBDataInterface):

    __nwbfields__ = ('name',)

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this node'})
    def __init__(self, **kwargs):
        super(Node, self).__init__(name=kwargs['name'])


class Edge(NWBDataInterface):

    __nwbfields__ = ('name',)

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this edge'})
    def __init__(self, **kwargs):
        super(Edge, self).__init__(name=kwargs['name'])


class Graph(MultiContainerInterface):
    """A multicontainer of nodes and undirected edges."""

    __nwbfields__ = ('name', 'edges', 'nodes')

    __clsconf__ = [
        {
            'attr': 'nodes',
            'type': Node,
            'add': 'add_node',
            'get': 'get_node'
        },
        {
            'attr': 'edges',
            'type': Edge,
            'add': 'add_edge',
            'get': 'get_edge'
        }
    ]


class MCITests(TestCase):

    def test_constructor(self):
        dv = get_docval(Graph.__init__)
        self.assertEqual(dv[0]['name'], 'nodes')
        self.assertEqual(dv[1]['name'], 'edges')
        self.assertTupleEqual(dv[0]['type'], (list, tuple, dict, Node))
        self.assertTupleEqual(dv[1]['type'], (list, tuple, dict, Edge))
