import os
import numpy as np
from dateutil import tz
from datetime import datetime
from uuid import uuid4

from pynwb import NWBHDF5IO, NWBFile,get_loaded_type_config, load_type_config, unload_type_config
from pynwb.file import Subject
from pynwb import unload_type_config, load_type_config
from pynwb.testing import TestCase

try:
    from linkml_runtime.utils.schemaview import SchemaView  # noqa: F401
    REQUIREMENTS_INSTALLED = True
except ImportError:
    REQUIREMENTS_INSTALLED = False


class TestPyNWBTypeConfig(TestCase):
    def setUp(self):
        if not REQUIREMENTS_INSTALLED:
            self.skipTest("optional LinkML module is not installed")
        load_type_config()

    def tearDown(self):
        unload_type_config()

    def test_get_loaded_type_config(self):
        pass

    def test_default_config(self):
        session_start_time = datetime(2018, 4, 25, 2, 30, 3, tzinfo=tz.gettz("US/Pacific"))
        nwbfile = NWBFile(
            session_description="Mouse exploring an open field",  # required
            identifier=str(uuid4()),  # required
            session_start_time=session_start_time,  # required
            session_id="session_1234",  # optional
            experimenter=[
                "Ryan Ly",
            ],  # optional
            lab="Bag End Laboratory",  # optional
            institution="University of My Institution",  # optional
            experiment_description="I went on an adventure to reclaim vast treasures.",  # optional
            related_publications="DOI:10.1016/j.neuron.2016.12.011",  # optional
        )
        subject = Subject(
            subject_id="01",
            age="One shouldn't ask",
            description="A human.",
            species="Homo sapiens",
            sex="M",
        )
        nwbfile.subject = subject
