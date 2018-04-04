import unittest
import shutil
import os

from pynwb.docutils.sg_prototype import build


class DocUtils(unittest.TestCase):

    def setUp(self):

        TGT_DIR_SUFFIX = os.path.abspath('_html_sg-prototype_TEST')
        TGT_DIR = os.path.abspath(os.path.join(__file__, TGT_DIR_SUFFIX))

        self.test_dir = TGT_DIR

    def test_sg_build(self):

        build(None, tgt_dir=self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)
