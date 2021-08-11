from pynwb import NWBHDF5IO
from pynwb.testing import TestCase
import requests


def _search_dandi_assets(url, filepath):
    response = requests.request("GET", url, headers={"Accept": "application/json"}).json()

    for asset in response["results"]:
        if filepath == asset["path"]:
            return asset["asset_id"]

    if response.get("next", None):
        return _search_dandi_assets(response["next"], filepath)

    return None


def get_dandi_asset_id(dandiset_id, filepath):
    url = f"https://api.dandiarchive.org/api/dandisets/{dandiset_id}/versions/draft/assets/"
    asset_id = _search_dandi_assets(url, filepath)
    if asset_id is None:
        raise ValueError(f'path {filepath} not found in dandiset {dandiset_id}.')
    return asset_id


def get_dandi_s3_url(dandiset_id, filepath):
    """Get the s3 location for any NWB file on DANDI"""

    asset_id = get_dandi_asset_id(dandiset_id, filepath)
    url = f"https://api.dandiarchive.org/api/dandisets/{dandiset_id}/versions/draft/assets/{asset_id}/download/"

    s3_url = requests.request(url=url, method='head').url
    if '?' in s3_url:
        return s3_url[:s3_url.index('?')]
    return s3_url


class TestRos3Streaming(TestCase):
    # requires h5py to be built with the ROS3 driver: conda install -c conda-forge h5py
    # also requires requests package to be installed

    def test_read(self):
        # ephys, Svoboda Lab (450 kB)
        dandiset_id = '000006'
        filepath = 'sub-anm372795/sub-anm372795_ses-20170718.nwb'
        s3_path = get_dandi_s3_url(dandiset_id, filepath)

        with NWBHDF5IO(s3_path, mode='r', load_namespaces=True, driver='ros3') as io:
            nwbfile = io.read()
            test_data = nwbfile.acquisition['lick_times'].time_series['lick_left_times'].data[:]
            self.assertEqual(len(test_data), 1046)
