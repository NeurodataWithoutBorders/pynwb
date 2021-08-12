from pynwb.testing import TestCase
from pynwb.utils import get_dandi_s3_url, get_dandi_asset_id


class TestDandiUtils(TestCase):
    # NOTE these tests require the "requests" package to be installed

    def test_get_dandi_s3_url(self):
        # this is the NWB Test Data dandiset
        dandiset_id = '000126'
        filepath = 'sub-1/sub-1.nwb'
        s3_path = get_dandi_s3_url(dandiset_id, filepath)

        expected = 'https://dandiarchive.s3.amazonaws.com/blobs/11e/c89/11ec8933-1456-4942-922b-94e5878bb991'
        self.assertEqual(s3_path, expected)

    def test_get_dandi_asset_id(self):
        # this is the NWB Test Data dandiset
        dandiset_id = '000126'
        filepath = 'sub-1/sub-1.nwb'
        asset_id = get_dandi_asset_id(dandiset_id, filepath)

        expected = '902af029-f411-40b5-81f1-67930d56ee05'
        self.assertEqual(asset_id, expected)
