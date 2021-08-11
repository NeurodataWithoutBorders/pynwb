from pynwb.testing import TestCase
from pynwb.utils import get_dandi_s3_url, get_dandi_asset_id


class TestDandiUtils(TestCase):

    def test_get_dandi_s3_url(self):
        # ephys, Svoboda Lab (450 kB)
        dandiset_id = '000006'
        filepath = 'sub-anm372795/sub-anm372795_ses-20170718.nwb'
        s3_path = get_dandi_s3_url(dandiset_id, filepath)

        expected = 'https://dandiarchive.s3.amazonaws.com/blobs/43b/f3a/43bf3a81-4a0b-433f-b471-1f10303f9d35'
        self.assertEqual(s3_path, expected)

    def test_get_dandi_asset_id(self):
        # ephys, Svoboda Lab (450 kB)
        dandiset_id = '000006'
        filepath = 'sub-anm372795/sub-anm372795_ses-20170718.nwb'
        asset_id = get_dandi_asset_id(dandiset_id, filepath)

        expected = '755505d0-d8d1-46af-bc3f-4aa494060c1a'
        self.assertEqual(asset_id, expected)
