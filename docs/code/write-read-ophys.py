import os
from datetime import datetime

from pynwb import NWBFile, NWBHDF5IO
from pynwb.ophys import TwoPhotonSeries, OpticalChannel, ImageSegmentation, Fluorescence


def main():
    nwb_path = 'ophys_example.nwb'
    # create your NWBFile object
    nwbfile = NWBFile('the PyNWB tutorial', 'my first synthetic recording', 'EXAMPLE_ID', datetime.now(),
                      experimenter='Dr. Bilbo Baggins',
                      lab='Bag End Laboratory',
                      institution='University of Middle Earth at the Shire',
                      experiment_description='I went on an adventure with thirteen dwarves to reclaim vast treasures.',
                      session_id='LONELYMTN')

    # create acquisition metadata
    optical_channel = OpticalChannel('test_optical_channel', 'optical channel source',
                                     'optical channel description', '3.14')
    imaging_plane = nwbfile.create_imaging_plane('test_imaging_plane',
                                                 'ophys integration tests',
                                                 optical_channel,
                                                 'imaging plane description',
                                                 'imaging_device_1',
                                                 '6.28', '2.718', 'GFP', 'somewhere in the brain',
                                                 (1, 2, 1, 2, 3), 4.0, 'manifold unit', 'A frame to refer to')

    # create acquisition data
    image_series = TwoPhotonSeries(name='test_iS', source='a hypothetical source', dimension=[2],
                                   external_file=['images.tiff'], imaging_plane=imaging_plane,
                                   starting_frame=[1, 2, 3], format='tiff', timestamps=list())
    nwbfile.add_acquisition(image_series)

    mod = nwbfile.create_processing_module('img_seg_example', 'ophys demo', 'an example of writing Ca2+ imaging data')
    img_seg = ImageSegmentation('a toy image segmentation container')
    mod.add_data_interface(img_seg)
    ps = img_seg.create_plane_segmentation('integration test PlaneSegmentation', 'plane segmentation description',
                                           imaging_plane, 'test_plane_seg_name', image_series)
    # add two ROIs
    # - first argument is the pixel mask i.e. a list of pixels and their weights
    # - second argument is the image mask
    w, h = 3, 3
    pix_mask1 = [(0, 0, 1.1), (1, 1, 1.2), (2, 2, 1.3)]
    img_mask1 = [[0.0 for x in range(w)] for y in range(h)]
    img_mask1[0][0] = 1.1
    img_mask1[1][1] = 1.2
    img_mask1[2][2] = 1.3
    ps.add_roi(pix_mask1, img_mask1)

    pix_mask2 = [(0, 0, 2.1), (1, 1, 2.2)]
    img_mask2 = [[0.0 for x in range(w)] for y in range(h)]
    img_mask2[0][0] = 2.1
    img_mask2[1][1] = 2.2
    ps.add_roi(pix_mask2, img_mask2)

    # add a Fluorescence container
    fl = Fluorescence('a toy fluorescence container')
    mod.add_data_interface(fl)
    # get an ROI table region i.e. a subset of ROIs to create a RoiResponseSeries from
    rt_region = ps.create_roi_table_region([0], 'the first of two ROIs')
    # make some fake timeseries data
    data = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    timestamps = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    rrs = fl.create_roi_response_series('test_roi_response_series', 'RoiResponseSeries integration test',
                                        data, 'lumens', rt_region, timestamps=timestamps)
    # write data
    with NWBHDF5IO(nwb_path, 'w') as io:
        io.write(nwbfile)

    # read data back in
    io = NWBHDF5IO(nwb_path, 'r')
    nwbfile = io.read()

    # get the processing module
    mod = nwbfile.get_processing_module('img_seg_example')

    # get the PlaneSegmentation from the ImageSegmentation data interface
    ps = mod['ImageSegmentation'].get_plane_segmentation()
    img_mask1 = ps.get_image_mask(0)
    pix_mask1 = ps.get_pixel_mask(0)
    img_mask2 = ps.get_image_mask(1)
    pix_mask2 = ps.get_pixel_mask(1)

    # get the RoiResponseSeries from the Fluorescence data interface
    rrs = mod['Fluorescence'].get_roi_response_series()
    # get the data...
    rrs_data = rrs.data                           # noqa: F841
    rrs_timestamps = rrs.timestamps               # noqa: F841
    # and now do something cool!

    io.close()
    if os.path.exists(nwb_path):
        os.remove(nwb_path)


if __name__ == '__main__':
    main()
