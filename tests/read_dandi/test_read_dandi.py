from dandi.dandiapi import DandiAPIClient
import sys
import traceback

from pynwb import NWBHDF5IO
from pynwb.testing import TestCase


class TestReadNWBDandisets(TestCase):
    """Test reading NWB files from the DANDI Archive using ROS3."""

    def test_read_first_nwb_asset(self):
        """Test reading the first NWB asset from each dandiset that uses NWB."""
        client = DandiAPIClient()
        dandisets = client.get_dandisets()

        failed_reads = dict()
        for i, dandiset in enumerate(dandisets):
            dandiset_metadata = dandiset.get_raw_metadata()

            # skip any dandisets that do not use NWB
            if not any(
                data_standard["identifier"] == "RRID:SCR_015242"  # this is the RRID for NWB
                for data_standard in dandiset_metadata["assetsSummary"].get("dataStandard", [])
            ):
                continue

            dandiset_identifier = dandiset_metadata["identifier"]
            print("--------------")
            print(f"{i}: {dandiset_identifier}")

            # iterate through assets until we get an NWB file (it could be MP4)
            assets = dandiset.get_assets()
            first_asset = next(assets)
            while first_asset.path.split(".")[-1] != "nwb":
                first_asset = next(assets)
            if first_asset.path.split(".")[-1] != "nwb":
                print("No NWB files?!")
                continue

            s3_url = first_asset.get_content_url(follow_redirects=1, strip_query=True)

            try:
                with NWBHDF5IO(path=s3_url, load_namespaces=True, driver="ros3") as io:
                    io.read()
            except Exception as e:
                print(traceback.format_exc())
                failed_reads[dandiset] = e

        if failed_reads:
            print(failed_reads)
            sys.exit(1)
