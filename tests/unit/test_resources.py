import warnings
from datetime import datetime
from uuid import uuid4
import os

from dateutil import tz

from hdmf import Data

from pynwb.resources import HERD
from pynwb.file import Subject
from pynwb import NWBHDF5IO, NWBFile
from pynwb.testing import TestCase


class TestNWBContainer(TestCase):
    def setUp(self):
        self.path = "resources_file.nwb"
        self.export_path = "export_file.nwb"

    def tearDown(self):
        for path in [self.path, self.export_path]:
            if os.path.isfile(path):
                os.remove(path)

    def test_constructor(self):
        """
        Test constructor
        """
        with warnings.catch_warnings(record=True):
            warnings.filterwarnings(
                "ignore",
                message=r"HERD is experimental .*",
                category=UserWarning,
            )
            er = HERD()
            self.assertIsInstance(er, HERD)

    def test_nwbfile_init_herd(self):
        session_start_time = datetime(2018, 4, 25, 2, 30, 3, tzinfo=tz.gettz("US/Pacific"))
        herd = HERD()
        nwbfile = NWBFile(
            session_description="A Person undergoing brain pokes.",
            identifier=str(uuid4()),
            session_start_time=session_start_time,
            external_resources=herd
        )
        self.assertTrue(isinstance(nwbfile.external_resources, HERD))

    def test_nwbfile_set_herd(self):
        session_start_time = datetime(2018, 4, 25, 2, 30, 3, tzinfo=tz.gettz("US/Pacific"))
        herd = HERD()
        nwbfile = NWBFile(
            session_description="A Person undergoing brain pokes.",
            identifier=str(uuid4()),
            session_start_time=session_start_time,
        )
        nwbfile.external_resources = herd
        self.assertTrue(isinstance(nwbfile.external_resources, HERD))
        self.assertEqual(nwbfile.external_resources.parent, nwbfile)

    def test_resources_roundtrip(self):
        session_start_time = datetime(2018, 4, 25, 2, 30, 3, tzinfo=tz.gettz("US/Pacific"))

        nwbfile = NWBFile(
            session_description="A Person undergoing brain pokes.",
            identifier=str(uuid4()),
            session_start_time=session_start_time,
        )
        subject = Subject(
            subject_id="001",
            age="26",
            description="human 5",
            species='Homo sapiens',
            sex="M",
        )

        nwbfile.subject = subject
        herd = HERD()
        nwbfile.external_resources = herd

        nwbfile.external_resources.add_ref(container=nwbfile.subject,
                                  key=nwbfile.subject.species,
                                  entity_id="NCBI_TAXON:9606",
                                  entity_uri='https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?mode=Info&id=9606')

        with NWBHDF5IO(self.path, "w") as io:
            io.write(nwbfile)

        with NWBHDF5IO(self.path, "r") as io:
            read_nwbfile = io.read()
            breakpoint()
            # self.assertEqual(read_nwbfile.external_resources.keys.data, [('Homo sapiens',)])
            # self.assertEqual(read_nwbfile.external_resources.entities.data, [('NCBI_TAXON:9606',
            # 'https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?mode=Info&id=9606')])
            # self.assertEqual(read_nwbfile.external_resources.objects.data, [(0, col1.object_id, 'VectorData', '', '')])

    def test_link_resources(self):
        """
        Note: Make sure that the internal HERD is not overwritten on export.
        """
        session_start_time = datetime(2018, 4, 25, 2, 30, 3, tzinfo=tz.gettz("US/Pacific"))

        nwbfile = NWBFile(
            session_description="A Person undergoing brain pokes.",
            identifier=str(uuid4()),
            session_start_time=session_start_time,
        )
        subject = Subject(
            subject_id="001",
            age="26",
            description="human 5",
            species='Homo sapiens',
            sex="M",
        )

        nwbfile.subject = subject
        herd = HERD()
        nwbfile.external_resources = herd

        nwbfile.external_resources.add_ref(container=nwbfile.subject,
                                  key=nwbfile.subject.species,
                                  entity_id="NCBI_TAXON:9606",
                                  entity_uri='https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?mode=Info&id=9606')

        with NWBHDF5IO(self.path, "w") as io:
            io.write(nwbfile)

        with NWBHDF5IO(self.read_path, mode='r') as read_io:
            read_nwbfile = read_io.read()
            read_nwbfile.link_resources(HERD())

            self.assertEqual(read_nwbfile.external_resources.keys.data, [])
            self.assertEqual(read_nwbfile.external_resources.entities.data, [])
            self.assertEqual(read_nwbfile.external_resources.objects.data, [])

            with NWBHDF5IO(self.export_path, mode='w') as export_io:
                export_io.export(src_io=read_io, nwbfile=nwbfile)

            with NWBHDF5IO(self.export_path, mode='r') as read_export_io:
                read_export_nwbfile = read_export_io.read()
                self.assertEqual(read_export_nwbfile.external_resources, herd)
