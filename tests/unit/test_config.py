from dateutil import tz
from datetime import datetime
from uuid import uuid4
import os

from hdmf.term_set import TermSetWrapper

from pynwb import NWBFile, get_loaded_type_config, load_type_config, unload_type_config
from pynwb.file import Subject
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
        CUR_DIR = os.path.dirname(os.path.realpath(__file__))    
        path_to_config = os.path.join(CUR_DIR, 'test_config/test_nwb_config.yaml')
        load_type_config(config_path=path_to_config)

    def tearDown(self):
        unload_type_config()

    def test_get_loaded_type_config(self):
        config = get_loaded_type_config()
        self.assertEqual(config,
        {'namespaces': {'core': {'version': '2.7.0-alpha',
        'data_types': {'Subject': {'species': {'termset': 'nwb_subject_termset.yaml'}}}}}})

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

        self.assertIsInstance(nwbfile.subject.species, TermSetWrapper)
