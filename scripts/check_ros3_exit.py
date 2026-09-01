#!/usr/bin/env python
"""Report whether a process that used the HDF5 ROS3 VFD can exit.

Spawns a child process that opens an object over the ROS3 driver, closes it, and
returns from ``main``. The child prints ``ROS3_READ_OK`` once all HDF5 work has
finished, so anything after that point is process teardown. The parent waits for
the child to exit and reports the outcome.

Exit code 0 means the child exited on its own; exit code 1 means it was still
alive after the timeout, or the read itself failed.

See https://github.com/NeurodataWithoutBorders/pynwb/issues/2228 and
https://github.com/HDFGroup/hdf5/issues/6560.
"""
import argparse
import subprocess
import sys
import time

CHILD = """
import sys
import h5py

url = "https://dandiarchive.s3.amazonaws.com/ros3test.nwb"
with h5py.File(url, mode="r", driver="ros3", aws_region=b"us-east-2") as f:
    n = len(f["acquisition"]["ts_name"]["data"][:])
print("ROS3_READ_OK", n, flush=True)
sys.stdout.flush()
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout", type=float, default=120.0,
                        help="seconds to wait for the child process to exit")
    args = parser.parse_args()

    start = time.monotonic()
    proc = subprocess.Popen([sys.executable, "-c", CHILD])
    try:
        rc = proc.wait(timeout=args.timeout)
    except subprocess.TimeoutExpired:
        elapsed = time.monotonic() - start
        print("HUNG: child process was still alive %.1fs after start" % elapsed, flush=True)
        proc.kill()
        proc.wait()
        return 1

    elapsed = time.monotonic() - start
    if rc != 0:
        print("FAILED: child process exited with code %d after %.1fs" % (rc, elapsed), flush=True)
        return 1

    print("EXITED: child process exited cleanly after %.1fs" % elapsed, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
