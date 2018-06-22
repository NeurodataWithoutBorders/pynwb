from pynwb.form.build import GroupBuilder, DatasetBuilder

from pynwb.core import DynamicTable

from . import base


class TestDynamicTableIO(base.TestMapRoundTrip):

    def setUpContainer(self):
        return DynamicTable('trials', 'DynamicTable integration test')

    def setUpBuilder(self):
        return GroupBuilder('trials',
                            attributes={
                                 'help': 'A column-centric table',
                                 'namespace': 'core',
                                 'neurodata_type': 'DynamicTable',
                                 'source': 'DynamicTable integration test',
                            })
