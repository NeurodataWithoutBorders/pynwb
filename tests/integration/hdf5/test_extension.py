from hdmf.build import BuildManager
from hdmf.common import VectorData
from hdmf.utils import docval, get_docval, popargs

from pynwb import NWBFile
from pynwb.spec import NWBDatasetSpec, NWBAttributeSpec
from pynwb.testing import NWBH5IOFlexMixin, TestCase

from ..helpers.utils import create_test_extension


class TestDynamicTableCustomColumnWithArgs(NWBH5IOFlexMixin, TestCase):

    class SubVectorData(VectorData):
        __fields__ = ('extra_kwarg', )

        @docval(
            *get_docval(VectorData.__init__, "name", "description", "data"),
            {'name': 'extra_kwarg', 'type': 'str', 'doc': 'An extra kwarg.'},
        )
        def __init__(self, **kwargs):
            extra_kwarg = popargs('extra_kwarg', kwargs)
            super().__init__(**kwargs)
            self.extra_kwarg = extra_kwarg

    def setUp(self):
        """Set up an extension with a custom VectorData column."""

        spec = NWBDatasetSpec(
            neurodata_type_def='SubVectorData',
            neurodata_type_inc='VectorData',
            doc='A custom VectorData column.',
            dtype='text',
            shape=(None,),
            attributes=[
                NWBAttributeSpec(
                    name="extra_kwarg",
                    doc='An extra kwarg.',
                    dtype='text'
                ),
            ],
        )

        self.type_map = create_test_extension([spec], {"SubVectorData": self.SubVectorData})
        self.manager = BuildManager(self.type_map)
        super().setUp()

    def get_manager(self):
        return self.manager

    def getContainerType(self):
        return "TrialsWithCustomColumnsWithArgs"

    def addContainer(self):
        """ Add the test DynamicTable to the given NWBFile """
        self.nwbfile.add_trial_column(
            name="test",
            description="test",
            col_cls=self.SubVectorData,
            extra_kwarg="test_extra_kwarg"
        )
        self.nwbfile.add_trial(start_time=1.0, stop_time=2.0, test="test_data")

    def getContainer(self, nwbfile: NWBFile):
        return nwbfile.trials["test"]

    def test_roundtrip(self):
        super().test_roundtrip()
        assert isinstance(self.read_container, self.SubVectorData)
        assert self.read_container.extra_kwarg == "test_extra_kwarg"

    def test_roundtrip_export(self):
        super().test_roundtrip_export()
        assert isinstance(self.read_container, self.SubVectorData)
        assert self.read_container.extra_kwarg == "test_extra_kwarg"
