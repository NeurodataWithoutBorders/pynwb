from pynwb import NWBHDF5IO
from pynwb.base import ProcessingModule, TimeSeries, Image, Images
from pynwb.behavior import SpatialSeries, BehavioralEpochs, BehavioralEvents, BehavioralTimeSeries, PupilTracking, \
                           EyeTracking, CompassDirection, Position
from pynwb.core import NWBContainer, NWBDataInterface, NWBData, ScratchData, Index, VectorData, VectorIndex, \
                       ElementIdentifiers, DynamicTable, DynamicTableRegion
from pynwb.device import Device
from pynwb.ecephys import ElectrodeGroup, ElectricalSeries, SpikeEventSeries, EventDetection, EventWaveform, LFP, \
                          FilteredEphys, FeatureExtraction
from pynwb.epoch import TimeIntervals
from pynwb.file import LabMetaData, Subject, NWBFile
from pynwb.icephys import PatchClampSeries, CurrentClampSeries, IZeroClampSeries, CurrentClampStimulusSeries, \
                          VoltageClampSeries, VoltageClampStimulusSeries, SweepTable
from pynwb.image import ImageSeries, IndexSeries, ImageMaskSeries, OpticalSeries, GrayscaleImage, RGBImage, RGBAImage
from pynwb.misc import AnnotationSeries, AbstractFeatureSeries, IntervalSeries, Units, DecompositionSeries
from pynwb.ogen import OptogeneticStimulusSite, OptogeneticSeries
from pynwb.ophys import OpticalChannel, ImagingPlane, TwoPhotonSeries, CorrectedImageStack, MotionCorrection, \
                        PlaneSegmentation, ImageSegmentation, RoiResponseSeries, DfOverF, Fluorescence
from pynwb.retinotopy import ImagingRetinotopy

from datetime import datetime

nwbfile = NWBFile('sess_desc', 'identifier', datetime.now().astimezone())
