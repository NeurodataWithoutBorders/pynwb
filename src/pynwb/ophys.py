from collections import Iterable
import numpy as np

from form.utils import docval, popargs

from .base import Interface, TimeSeries, _default_resolution, _default_conversion
from .image import ImageSeries
from .core import NWBContainer

@register_class('TwoPhotonSeries', CORE_NAMESPACE)
class TwoPhotonSeries(ImageSeries):
    """
    A special case of optical imaging.
    """

    __nwbfields__ = ('field_of_view',
                     'imaging_plane',
                     'pmt_gain',
                     'scan_line_rate')

    _ancestry = "TimeSeries,ImageSeries,TwoPhotonSeries"
    _help = "Image stack recorded from 2-photon microscope."

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset'},
            {'name': 'source', 'type': str, 'doc': ('Name of TimeSeries or Modules that serve as the source for the data '
                                                   'contained here. It can also be the name of a device, for stimulus or '
                                                   'acquisition data')},
            {'name': 'data', 'type': (list, np.ndarray, TimeSeries), 'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames'},
            {'name': 'unit', 'type': str, 'doc': 'The base unit of measurement (should be SI unit)'},

            {'name': 'field_of_view', 'type': (list, np.ndarray, 'TimeSeries'), 'doc': 'Width, height and depth of image, or imaged area (meters).'},
            {'name': 'imaging_plane', 'type': ImagingPlane, 'doc': 'Imaging plane class/pointer.'},
            {'name': 'pmt_gain', 'type': float, 'doc': 'Photomultiplier gain.'},
            {'name': 'scan_line_rate', 'type': float, 'doc': 'Lines imaged per second. This is also stored in /general/optophysiology but is kept here as it is useful information for analysis, and so good to be stored w/ the actual data.'},

            {'name': 'external_file', 'type': Iterable, 'doc': 'Path or URL to one or more external file(s). Field only present if format=external. Either external_file or data must be specified, but not both.'},
            {'name': 'starting_frame', 'type': Iterable, 'doc': 'Each entry is the frame number in the corresponding external_file variable. This serves as an index to what frames each file contains.'},
            {'name': 'format', 'type': str, 'doc': 'Format of image. Three types: 1) Image format; tiff, png, jpg, etc. 2) external 3) raw.'},
            {'name': 'bits_per_pixel', 'type': float, 'doc': 'Number of bit per image pixel', 'default': np.nan},
            {'name': 'dimension', 'type': Iterable, 'doc': 'Number of pixels on x, y, (and z) axes.', 'default': [np.nan]},

            {'name': 'resolution', 'type': float, 'doc': 'The smallest meaningful difference (in specified unit) between values in data', 'default': _default_resolution},
            {'name': 'conversion', 'type': float, 'doc': 'Scalar to multiply each element by to conver to volts', 'default': _default_conversion},

            {'name': 'timestamps', 'type': (list, np.ndarray, TimeSeries), 'doc': 'Timestamps for samples stored in data', 'default': None},
            {'name': 'starting_time', 'type': float, 'doc': 'The timestamp of the first sample', 'default': None},
            {'name': 'rate', 'type': float, 'doc': 'Sampling rate in Hz', 'default': None},

            {'name': 'comments', 'type': str, 'doc': 'Human-readable comments about this TimeSeries dataset', 'default':None},
            {'name': 'description', 'type': str, 'doc': 'Description of this TimeSeries dataset', 'default':None},
            {'name': 'control', 'type': Iterable, 'doc': 'Numerical labels that apply to each element in data', 'default': None},
            {'name': 'control_description', 'type': Iterable, 'doc': 'Description of each control value', 'default': None},
            {'name': 'parent', 'type': 'NWBContainer', 'doc': 'The parent NWBContainer for this NWBContainer', 'default': None},
    )
    def __init__(self, **kwargs):
        name, source, data, unit, external_file, starting_frame, format = popargs('name', 'source', 'data', 'unit', 'external_file', 'starting_frame', 'format', kwargs)
        field_of_view, imaging_plane, pmt_gain, scan_line_rate = popargs('field_of_view', 'imaging_plane', 'pmt_gain', 'scan_line_rate', kwargs)
        super(TwoPhotonSeries, self).__init__(name, source, data, unit, external_file, starting_frame, format, **kwargs)
        self.field_of_view = field_of_view
        self.imaging_plane = imaging_plane
        self.pmt_gain = pmt_gain
        self.scan_line_rate = scan_line_rate

@register_class('RoiResponseSeries', CORE_NAMESPACE)
class RoiResponseSeries(TimeSeries):
    '''
    ROI responses over an imaging plane. Each row in data[] should correspond to the signal from one ROI.
    '''

    __nwbfields__ = ('roi_names',
                     'segmenttation_interface')

    _ancestry = "TimeSeries,ImageSeries,ImageMaskSeries"
    _help = "ROI responses over an imaging plane. Each row in data[] should correspond to the signal from one no ROI."

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset'},
            {'name': 'source', 'type': str, 'doc': ('Name of TimeSeries or Modules that serve as the source for the data '
                                                   'contained here. It can also be the name of a device, for stimulus or '
                                                   'acquisition data')},
            {'name': 'data', 'type': (list, np.ndarray, TimeSeries), 'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames'},
            {'name': 'unit', 'type': str, 'doc': 'The base unit of measurement (should be SI unit)'},

            {'name': 'roi_names', 'type': Iterable, 'doc': 'List of ROIs represented, one name for each row of data[].'},
            {'name': 'segmenttation_interface', 'type': ImageSegmentation, 'doc': 'Link to ImageSegmentation.'},

            {'name': 'resolution', 'type': float, 'doc': 'The smallest meaningful difference (in specified unit) between values in data', 'default': _default_resolution},
            {'name': 'conversion', 'type': float, 'doc': 'Scalar to multiply each element by to conver to volts', 'default': _default_conversion},

            {'name': 'timestamps', 'type': (list, np.ndarray, TimeSeries), 'doc': 'Timestamps for samples stored in data', 'default': None},
            {'name': 'starting_time', 'type': float, 'doc': 'The timestamp of the first sample', 'default': None},
            {'name': 'rate', 'type': float, 'doc': 'Sampling rate in Hz', 'default': None},

            {'name': 'comments', 'type': str, 'doc': 'Human-readable comments about this TimeSeries dataset', 'default':None},
            {'name': 'description', 'type': str, 'doc': 'Description of this TimeSeries dataset', 'default':None},
            {'name': 'control', 'type': Iterable, 'doc': 'Numerical labels that apply to each element in data', 'default': None},
            {'name': 'control_description', 'type': Iterable, 'doc': 'Description of each control value', 'default': None},
            {'name': 'parent', 'type': 'NWBContainer', 'doc': 'The parent NWBContainer for this NWBContainer', 'default': None},
    )
    def __init__(self, **kwargs):
        name, source, data, unit = popargs('name', 'source', 'data', 'unit', kwargs)
        roi_names, segmenttation_interface = popargs('roi_names', 'segmenttation_interface', kwargs)
        super(RoiResponseSeries, self).__init__(name, source, data, unit, **kwargs)
        self.roi_names = roi_names
        self.segmenttation_interface = segmenttation_interface

@register_class('DfOverF', CORE_NAMESPACE)
class DfOverF(Interface):
    """
    dF/F information about a region of interest (ROI). Storage hierarchy of dF/F should be the same
    as for segmentation (ie, same names for ROIs and for image planes).
    """

    __nwbfields__ = ('roi_response_series',)

    _help = "Df/f over time of one or more ROIs. TimeSeries names should correspond to imaging plane names"

    @docval({'name': 'source', 'type': str, 'doc': 'The source of the data represented in this Module Interface.'},
            {'name': 'roi_response_series', 'type': RoiResponseSeries, 'doc': 'RoiResponseSeries or any subtype.'})
    def __init__(self, **kwargs):
        source, roi_response_series = popargs('source', 'roi_response_series', kwargs)
        super(DfOverF, self).__init__(source, **kwargs)
        self.roi_response_series = roi_response_series

@register_class('Fluorescence', CORE_NAMESPACE)
class Fluorescence(Interface):
    """
    Fluorescence information about a region of interest (ROI). Storage hierarchy of fluorescence
    should be the same as for segmentation (ie, same names for ROIs and for image planes).
    """

    __nwbfields__ = ('roi_response_series',)

    _help = "Fluorescence over time of one or more ROIs. TimeSeries names should correspond to imaging plane names."

    @docval({'name': 'source', 'type': str, 'doc': 'the source of the data represented in this Module Interface'},
            {'name': 'roi_response_series', 'type': RoiResponseSeries, 'doc': 'RoiResponseSeries or any subtype.'})
    def __init__(self, **kwargs):
        source, roi_response_series = popargs('source', 'roi_response_series', kwargs)
        super(Fluorescence, self).__init__(source, **kwargs)
        self.roi_response_series = roi_response_series

