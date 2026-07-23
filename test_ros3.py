#!/usr/bin/env python
"""Run test.py and recover from the HDF5 ros3 shutdown deadlock on Windows.

See https://github.com/NeurodataWithoutBorders/pynwb/issues/2228
"""
import os
import subprocess
import sys
import tempfile
import time

RESULT_GRACE = 30       # seconds to allow a clean exit after test.py reports its result
STARTUP_TIMEOUT = 1800  # fail if test.py never reports a result


def _read_exitcode(path):
    try:
        with open(path) as f:
            content = f.read().strip()
    except OSError:
        return None
    if not content:
        return None
    try:
        return int(content)
    except ValueError:
        return None


def main():
    fd, result_path = tempfile.mkstemp(prefix="pynwb_exitcode_")
    os.close(fd)
    env = dict(os.environ, PYNWB_EXITCODE_FILE=result_path)
    cmd = [sys.executable, os.path.join(os.path.dirname(__file__), "test.py")] + sys.argv[1:]
    proc = subprocess.Popen(cmd, env=env)

    start = time.monotonic()
    reported = None
    reported_at = None
    try:
        while True:
            rc = proc.poll()
            if rc is not None:
                return rc

            if reported_at is None:
                reported = _read_exitcode(result_path)
                if reported is not None:
                    reported_at = time.monotonic()

            if reported_at is not None and time.monotonic() - reported_at > RESULT_GRACE:
                print("test.py reported exit code %d but did not exit within %ds; terminating it"
                      % (reported, RESULT_GRACE), flush=True)
                proc.kill()
                proc.wait()
                return reported

            if reported_at is None and time.monotonic() - start > STARTUP_TIMEOUT:
                print("test.py did not report an exit code within %ds; terminating it"
                      % STARTUP_TIMEOUT, flush=True)
                proc.kill()
                proc.wait()
                return 1

            time.sleep(1)
    finally:
        try:
            os.remove(result_path)
        except OSError:
            pass


if __name__ == "__main__":
    sys.exit(main())
