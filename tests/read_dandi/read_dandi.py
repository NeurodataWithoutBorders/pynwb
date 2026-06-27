"""Entry point for the DANDI read tests.

Reads NWB files from the DANDI Archive and runs the DANDI streaming HERD tutorial as a smoke test.
Run by the "Run DANDI read tests" GitHub Actions workflow.
"""
import os
import runpy
import shutil

from read_first_nwb_asset import read_first_nwb_asset

# the streaming HERD tutorial, excluded from the offline example tests because it streams from DANDI
STREAMING_EXAMPLE = os.path.join(
    os.path.dirname(__file__), "..", "..", "docs", "gallery", "general", "resources_streaming.py"
)

# files the streaming tutorial writes to the current directory
STREAMING_ARTIFACTS = ("dandiset_resources.zip", "dandiset_resources_updated.zip")
STREAMING_CACHE_DIR = "nwb-cache"


def run_streaming_example():
    """Run the DANDI streaming HERD tutorial and remove the files it generates."""
    try:
        runpy.run_path(STREAMING_EXAMPLE, run_name="__main__")
    finally:
        for name in STREAMING_ARTIFACTS:
            if os.path.exists(name):
                os.remove(name)
        if os.path.isdir(STREAMING_CACHE_DIR):
            shutil.rmtree(STREAMING_CACHE_DIR)


if __name__ == "__main__":
    read_first_nwb_asset()
    run_streaming_example()
