
        # create your NWBFile object
        nwbfile = NWBFile(...)

        # set up some fake data
        nwbfile.add_acquisition(ImageSeries(name='test_iS', source='a hypothetical source', dimension=[2],
                                external_file=['images.tiff'],
                                starting_frame=[1, 2, 3], format='tiff', timestamps=list()))

        optical_channel = OpticalChannel('test_optical_channel', 'optical channel source',
                                         'optical channel description', '3.14')
        imaging_plane = nwbfile.create_imaging_plane('test_imaging_plane',
                                                     'ophys integration tests',
                                                     optical_channel,
                                                     'imaging plane description',
                                                     'imaging_device_1',
                                                     '6.28', '2.718', 'GFP', 'somewhere in the brain',
                                                     (1, 2, 1, 2, 3), 4.0, 'manifold unit', 'A frame to refer to')

        mod = nwbfile.create_processing_module('img_seg_example', 'a module for demoing ImageSegmentation')
        img_seg = ImageSegmentation('a toy image segmentation container')
        mod.add_data_interface(img_seg)
        pS = img_seg.create_plane_segmentation('integration test PlaneSegmentation', 'plane segmentation description',
                                               imaging_plane, 'test_plane_seg_name', image_series)
        # add two ROIs
        # - first argument is the pixel mask i.e. a list of pixels and their weights
        # - second argument is the image mask
        w, h = 5, 5
        pix_mask1 = [(1, 2, 1.1), (3, 4, 1.2), (5, 6, 1.3)]
        img_mask1 = [[0.0 for x in range(w)] for y in range(h)]
        img_mask1[1][2] = 1.1
        img_mask1[3][4] = 1.2
        img_mask1[5][6] = 1.3
        pS.add_roi(pix_mask1, img_mask1)

        pix_mask2 = [(7, 8, 2.1), (9, 10, 2.2)]
        img_mask2 = [[0.0 for x in range(w)] for y in range(h)]
        img_mask2[7][8] = 2.1
        img_mask2[9][10] = 2.2
        pS.add_roi(pix_mask2, img_mask2)

        # get an ROI table region i.e. a subset of ROIs to create a RoiResponseSeries from
        rt_region = plane_segmentation.create_roi_table_region([0], 'the first of two ROIs')
        # make some fake timeseries data
        data = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        timestamps = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
        # add an ROI response series
        mod.add_data_interface(RoiResponseSeries('test_roi_response_series', 'RoiResponseSeries integration test',
                                                 data, 'lumens', rt_region, timestamps=timestamps))

        with NWBHDF5IO('test.nwb', 'w') as io:
            io.write(nwbfile)

        # read data back in

        with NWBHDF5IO('test.nwb', 'r') as io:
            nwbfile = io.read()

        mod = nwbfile.get_processing_module('img_seg_example')
        pS = mod.get_data_interface('ImageSegmentation')
        img_mask1 = pS.get_image_mask(0)
        pix_mask1 = pS.get_pixel_mask(0)
        img_mask2 = pS.get_image_mask(1)
        pix_mask2 = pS.get_pixel_mask(1)
        rrs = mod.get_data_interface('test_roi_response_series')
        rrs_data = rrs.data
        rrs_timestamps = rrs.timestamps


