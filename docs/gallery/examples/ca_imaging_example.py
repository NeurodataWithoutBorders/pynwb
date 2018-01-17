'''
Writing Calcium Imaging Data
============================

This tutorial will explain how to save calcium imaging data to NWB files using PyNWB

First import the necessary types
'''
from pynwb.ophys import TwoPhotonSeries, RoiResponseSeries, DfOverF, Fluorescence, PlaneSegmentation, \
    ImageSegmentation, OpticalChannel, ImagingPlane, ROI
from pynwb.image import ImageSeries

#####################
# And then set up some fake data
w, h = 5, 5
img_mask = [[0 for x in range(w)] for y in range(h)]
w, h = 5, 2
pix_mask = [[0 for x in range(w)] for y in range(h)]
pix_mask_weight = [0 for x in range(w)]

#####################
# Define the ImageSeries
iSS = ImageSeries(
    name='test_iS', source='a hypothetical source', data=list(), unit='unit', external_file=['external_file'],
    starting_frame=[1, 2, 3], format='tiff', timestamps=list())

#####################
# Define some metadata on the imaging plane
oc = OpticalChannel('test_optical_channel', 'test_source', 'description', 'emission_lambda')
ip = ImagingPlane(
    'test_imaging_plane', 'test_source', oc, 'description', 'device', 'excitation_lambda',
    'imaging_rate', 'indicator', 'location', (1, 2, 1, 2, 3), 4.0, 'unit', 'reference_frame')

#####################
# Now define the ROIs produced from image segmentation
roi1 = ROI('roi1', 'test source', 'roi description1', pix_mask, pix_mask_weight, img_mask, iSS)
roi2 = ROI('roi2', 'test source', 'roi description2', pix_mask, pix_mask_weight, img_mask, iSS)
roi_list = (roi1, roi2)
ps = PlaneSegmentation('name', 'test source', 'description', roi_list, ip, iSS)

#####################
# Create data representing the ImageSegmentation results
iS = ImageSegmentation('test source', ps, name='test_iS')

#####################
# Now create our ROI dF/F data
rrs = RoiResponseSeries('test_ts', 'a hypothetical source', list(), 'unit', ['name1'], iS, timestamps=list())
dof = DfOverF('test_dof', rrs)

#####################
# Create the NWBFile object

NA = 'THIS FIELD INTENTIONALLY LEFT BLANK'

import datetime as dt
from pynwb import NWBFile
nwb = NWBFile(
    source = NA,
    session_description = NA,
    identifier = NA,
    session_start_time = dt.datetime.now(),
)

#####################
# create a processing module to put it all in
ophys_module = nwb.create_processing_module(
    name="ophys",
    description="calcium responses",
    source="Allen Brain Observatory: Visual Behavior",
)

#####################
# only add the top level container?
ophys_module.add_container(dof)

#####################
# now write the file
from pynwb import NWBHDF5IO as HDF5IO
io = HDF5IO('ophys_badfile.nwb',mode='w')
io.write(nwb)
io.close()

#####################
# and try to read it back out
reader = HDF5IO('ophys_badfile.nwb',mode='r')
read_data = reader.read()
