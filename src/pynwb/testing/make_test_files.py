from pynwb import NWBFile, NWBHDF5IO, validate, __version__
from datetime import datetime

# pynwb 1.0.2 should be installed with hdmf 1.0.3
# pynwb 1.0.3 should be installed with hdmf 1.0.5
# pynwb 1.1.0 should be installed with hdmf 1.2.0
# pynwb 1.1.1+ should be installed with an appopriate version of hdmf


def _write(test_name, nwbfile):
    filename = 'tests/back_compat/%s_%s.nwb' % (__version__, test_name)

    with NWBHDF5IO(filename, 'w') as io:
        io.write(nwbfile)

    with NWBHDF5IO(filename, 'r') as io:
        validate(io)
        nwbfile = io.read()


def make_nwbfile():
    nwbfile = NWBFile(session_description='ADDME',
                      identifier='ADDME',
                      session_start_time=datetime.now().astimezone())
    test_name = 'nwbfile'
    _write(test_name, nwbfile)


def make_nwbfile_str_experimenter():
    nwbfile = NWBFile(session_description='ADDME',
                      identifier='ADDME',
                      session_start_time=datetime.now().astimezone(),
                      experimenter='one experimenter')
    test_name = 'str_experimenter'
    _write(test_name, nwbfile)


def make_nwbfile_str_pub():
    nwbfile = NWBFile(session_description='ADDME',
                      identifier='ADDME',
                      session_start_time=datetime.now().astimezone(),
                      related_publications='one publication')
    test_name = 'str_pub'
    _write(test_name, nwbfile)


if __name__ == '__main__':
    make_nwbfile()
    make_nwbfile_str_experimenter()
    make_nwbfile_str_pub()
