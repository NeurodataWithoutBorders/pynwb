import os
import tempfile
from datetime import datetime
from uuid import uuid4

import numpy as np
from dateutil import tz

from pynwb import NWBHDF5IO, NWBFile
from pynwb.file import Subject
from pynwb.resources import HERD
from pynwb.testing import TestCase


class TestNWBContainer(TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmpdir.name, "resources_file.nwb")
        self.export_path = os.path.join(self.tmpdir.name, "export_file.nwb")

    def tearDown(self):
        self.tmpdir.cleanup()

    def _create_nwbfile_with_herd(self):
        """Create an NWBFile with a Subject and HERD containing a species annotation."""
        session_start_time = datetime(2018, 4, 25, 2, 30, 3, tzinfo=tz.gettz("US/Pacific"))
        nwbfile = NWBFile(
            session_description="ECoG recording during audio speech perception task",
            identifier=str(uuid4()),
            session_start_time=session_start_time,
        )
        subject = Subject(
            subject_id="001",
            age="P26Y",
            description="human subject",
            species="Homo sapiens",
            sex="M",
        )
        nwbfile.subject = subject
        herd = HERD()
        nwbfile.external_resources = herd
        nwbfile.external_resources.add_ref(
            container=nwbfile.subject,
            key=nwbfile.subject.species,
            entity_id="NCBI_TAXON:9606",
            entity_uri="https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?mode=Info&id=9606",
        )
        return nwbfile, subject

    def test_constructor(self):
        """
        Test constructor
        """
        er = HERD()
        self.assertIsInstance(er, HERD)

    def test_nwbfile_init_herd(self):
        session_start_time = datetime(2018, 4, 25, 2, 30, 3, tzinfo=tz.gettz("US/Pacific"))
        herd = HERD()
        nwbfile = NWBFile(
            session_description="ECoG recording during audio speech perception task",
            identifier=str(uuid4()),
            session_start_time=session_start_time,
            external_resources=herd,
        )
        self.assertIsInstance(nwbfile.external_resources, HERD)

    def test_nwbfile_set_herd(self):
        session_start_time = datetime(2018, 4, 25, 2, 30, 3, tzinfo=tz.gettz("US/Pacific"))
        herd = HERD()
        nwbfile = NWBFile(
            session_description="ECoG recording during audio speech perception task",
            identifier=str(uuid4()),
            session_start_time=session_start_time,
        )
        nwbfile.external_resources = herd
        self.assertIsInstance(nwbfile.external_resources, HERD)
        self.assertEqual(nwbfile.external_resources.parent, nwbfile)

    def test_resources_roundtrip(self):
        nwbfile, subject = self._create_nwbfile_with_herd()

        with NWBHDF5IO(self.path, "w") as io:
            io.write(nwbfile)

        with NWBHDF5IO(self.path, "r") as io:
            read_nwbfile = io.read()
            self.assertEqual(
                read_nwbfile.external_resources.keys[:],
                np.array(
                    [("Homo sapiens",)],
                    dtype=[("key", "O")],
                ),
            )
            self.assertEqual(
                read_nwbfile.external_resources.entities[:],
                np.array(
                    [
                        (
                            "NCBI_TAXON:9606",
                            "https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?mode=Info&id=9606",
                        )
                    ],
                    dtype=[("entity_id", "O"), ("entity_uri", "O")],
                ),
            )
            self.assertEqual(
                read_nwbfile.external_resources.objects[:],
                np.array(
                    [(0, subject.object_id, "Subject", "", "")],
                    dtype=[
                        ("files_idx", "<u4"),
                        ("object_id", "O"),
                        ("object_type", "O"),
                        ("relative_path", "O"),
                        ("field", "O"),
                    ],
                ),
            )

    def test_get_external_resources(self):
        """Test get_external_resources returns the correct HERD based on the linked parameter."""
        nwbfile, subject = self._create_nwbfile_with_herd()
        original_herd = nwbfile.external_resources

        linked_herd = HERD()
        nwbfile.link_resources(linked_herd)

        self.assertIs(nwbfile.get_external_resources(linked=False), original_herd)
        self.assertIs(nwbfile.get_external_resources(linked=True), linked_herd)
        # attribute returns the original, not the linked one
        self.assertIs(nwbfile.external_resources, original_herd)

    def test_get_external_resources_creates_herd(self):
        """get_external_resources creates and attaches a HERD when the file does not have one."""
        session_start_time = datetime(2018, 4, 25, 2, 30, 3, tzinfo=tz.gettz("US/Pacific"))
        nwbfile = NWBFile(
            session_description="ECoG recording during audio speech perception task",
            identifier=str(uuid4()),
            session_start_time=session_start_time,
        )
        self.assertIsNone(nwbfile.external_resources)

        herd = nwbfile.get_external_resources()
        self.assertIsInstance(herd, HERD)
        self.assertIs(nwbfile.external_resources, herd)
        self.assertEqual(herd.parent, nwbfile)

        # calling again returns the same HERD rather than creating a new one
        self.assertIs(nwbfile.get_external_resources(), herd)

    def test_link_resources(self):
        """Make sure that the original HERD is not overwritten on export."""
        nwbfile, subject = self._create_nwbfile_with_herd()

        with NWBHDF5IO(self.path, "w") as io:
            io.write(nwbfile)

        with NWBHDF5IO(self.path, mode="r") as read_io:
            read_nwbfile = read_io.read()
            read_nwbfile.link_resources(HERD())

            linked = read_nwbfile.get_external_resources(linked=True)
            self.assertEqual(linked.keys.data, [])
            self.assertEqual(linked.entities.data, [])
            self.assertEqual(linked.objects.data, [])

            with NWBHDF5IO(self.export_path, mode="w") as export_io:
                export_io.export(src_io=read_io, nwbfile=read_nwbfile)

            with NWBHDF5IO(self.export_path, mode="r") as read_export_io:
                read_export_nwbfile = read_export_io.read()
                self.assertEqual(
                    read_export_nwbfile.external_resources.keys[:],
                    np.array(
                        [("Homo sapiens",)],
                        dtype=[("key", "O")],
                    ),
                )
                self.assertEqual(
                    read_export_nwbfile.external_resources.entities[:],
                    np.array(
                        [
                            (
                                "NCBI_TAXON:9606",
                                "https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?mode=Info&id=9606",
                            )
                        ],
                        dtype=[("entity_id", "O"), ("entity_uri", "O")],
                    ),
                )
                self.assertEqual(
                    read_export_nwbfile.external_resources.objects[:],
                    np.array(
                        [(0, subject.object_id, "Subject", "", "")],
                        dtype=[
                            ("files_idx", "<u4"),
                            ("object_id", "O"),
                            ("object_type", "O"),
                            ("relative_path", "O"),
                            ("field", "O"),
                        ],
                    ),
                )
