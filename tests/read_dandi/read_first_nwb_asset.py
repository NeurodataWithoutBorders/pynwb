"""Test reading NWB files from the DANDI Archive using fsspec."""
from dandi.dandiapi import DandiAPIClient
import fsspec
import h5py
import random
import sys
import traceback

from pynwb import NWBHDF5IO


# NOTE: do not name the function with "test_" prefix, otherwise pytest
# will try to run it as a test

# TODO read dandisets systematically, not randomly
# see https://github.com/NeurodataWithoutBorders/pynwb/issues/1804

def read_first_nwb_asset():
    """Test reading the first NWB asset from a random selection of 2 dandisets that uses NWB."""
    num_dandisets_to_read = 2
    client = DandiAPIClient()
    dandisets = list(client.get_dandisets())
    random.shuffle(dandisets)
    dandisets_to_read = dandisets[:num_dandisets_to_read]
    print("Reading NWB files from the following dandisets:")
    print([d.get_raw_metadata()["identifier"] for d in dandisets_to_read])

    fs = fsspec.filesystem("http")

    failed_reads = dict()
    for i, dandiset in enumerate(dandisets_to_read):
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
            with fs.open(s3_url, "rb") as f:
                with h5py.File(f) as file:
                    with NWBHDF5IO(file=file) as io:
                        io.read()
        except Exception as e:
            print(traceback.format_exc())
            failed_reads[dandiset] = e

    if failed_reads:
        print(failed_reads)
        sys.exit(1)


if __name__ == "__main__":
    read_first_nwb_asset()
