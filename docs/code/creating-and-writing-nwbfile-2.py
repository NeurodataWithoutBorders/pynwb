
def main():
    import os.path

    # example: start
    from datetime import datetime

    from pynwb import NWBFile, TimeSeries, get_manager
    from pynwb.form.backends.hdf5 import HDF5IO

    start_time = datetime(1970, 1, 1, 12, 0, 0)
    create_date = datetime(2017, 4, 15, 12, 0, 0)

    nwbfile = NWBFile('the PyNWB tutorial', 'a test NWB File', 'TEST123', start_time,
                      file_create_date=create_date)

    ts = TimeSeries('test_timeseries', 'example_source', list(range(100, 200, 10)), 'SIunit',
                    timestamps=list(range(10)),
                    resolution=0.1)

    nwbfile.add_acquisition(ts)

    io = HDF5IO("example.h5", manager=get_manager(), mode='w')
    io.write(nwbfile)
    io.close()
    # example: end

    os.remove("example.h5")


if __name__ == "__main__":
    main()
