import warnings
from collections.abc import Iterable

import numpy as np

from hdmf.utils import (
    docval,
    getargs,
    popargs,
    popargs_to_dict,
    get_docval,
    get_data_shape,
)

from . import register_class, CORE_NAMESPACE
from .base import TimeSeries, Image, Images
from .device import Device


@register_class('ImageSeries', CORE_NAMESPACE)
class ImageSeries(TimeSeries):
    '''
    General image data that is common between acquisition and stimulus time series.
    The image data can be stored in the HDF5 file or it will be stored as an external image file.
    '''

    __nwbfields__ = ('dimension',
                     'external_file',
                     'starting_frame',
                     'format',
                     'device')

    # value used when an ImageSeries is read and missing data
    DEFAULT_DATA = np.ndarray(shape=(0, 0, 0), dtype=np.uint8)
    # TODO: copy new docs from 2.4 schema

    @docval(*get_docval(TimeSeries.__init__, 'name'),  # required
            {'name': 'data', 'type': ('array_data', 'data', TimeSeries), 'shape': ([None] * 3, [None] * 4),
             'doc': ('The data values. Can be 3D or 4D. The first dimension must be time (frame). The second and third '
                     'dimensions represent x and y. The optional fourth dimension represents z. Either data or '
                     'external_file must be specified (not None), but not both. If data is not specified, '
                     'data will be set to an empty 3D array.'),
             'default': None},
            {'name': 'unit', 'type': str,
             'doc': ('The unit of measurement of the image data, e.g., values between 0 and 255. Required when data '
                     'is specified. If unit (and data) are not specified, then unit will be set to "unknown".'),
             'default': None},
            {'name': 'format', 'type': str,
             'doc': 'Format of image. Three types - 1) Image format; tiff, png, jpg, etc. 2) external 3) raw.',
             'default': None},
            {'name': 'external_file', 'type': ('array_data', 'data'),
             'doc': 'Path or URL to one or more external file(s). Field only present if format=external. '
                    'Either external_file or data must be specified (not None), but not both.', 'default': None},
            {'name': 'starting_frame', 'type': Iterable,
             'doc': 'Each entry is a frame number that corresponds to the first frame of each file '
                    'listed in external_file within the full ImageSeries.', 'default': None},
            {'name': 'bits_per_pixel', 'type': int, 'doc': 'DEPRECATED: Number of bits per image pixel',
             'default': None},
            {'name': 'dimension', 'type': Iterable,
             'doc': 'Number of pixels on x, y, (and z) axes.', 'default': None},
            *get_docval(TimeSeries.__init__, 'resolution', 'conversion', 'timestamps', 'starting_time', 'rate',
                        'comments', 'description', 'control', 'control_description', 'offset'),
            {'name': 'device', 'type': Device,
             'doc': 'Device used to capture the images/video.', 'default': None},)
    def __init__(self, **kwargs):
        keys_to_set = ('bits_per_pixel', 'dimension', 'external_file', 'starting_frame', 'format', 'device')
        args_to_set = popargs_to_dict(keys_to_set, kwargs)
        name, data, unit = getargs('name', 'data', 'unit', kwargs)
        if data is not None and unit is None:
            raise ValueError("Must supply 'unit' argument when supplying 'data' to %s '%s'."
                             % (self.__class__.__name__, name))
        if args_to_set['external_file'] is None and data is None:
            raise ValueError("Must supply either external_file or data to %s '%s'."
                             % (self.__class__.__name__, name))

        # data and unit are required in TimeSeries, but allowed to be None here, so handle this specially
        if data is None:
            kwargs['data'] = ImageSeries.DEFAULT_DATA
        if unit is None:
            kwargs['unit'] = ImageSeries.DEFAULT_UNIT

        # If a single external_file is given then set starting_frame  to [0] for backward compatibility
        if (
            args_to_set["external_file"] is not None
            and args_to_set["starting_frame"] is None
        ):
            args_to_set["starting_frame"] = (
                [0] if len(args_to_set["external_file"]) == 1 else None
            )

        super().__init__(**kwargs)

        for key, val in args_to_set.items():
            setattr(self, key, val)

        if self._change_external_file_format():
            warnings.warn(
                "%s '%s': The value for 'format' has been changed to 'external'. "
                "Setting a default value for 'format' is deprecated and will be changed "
                "to raising a ValueError in the next major release."
                % (self.__class__.__name__, self.name),
                DeprecationWarning,
            )

        if not self._check_image_series_dimension():
            warnings.warn(
                "%s '%s': Length of data does not match length of timestamps. Your data may be transposed. "
                "Time should be on the 0th dimension"
                % (self.__class__.__name__, self.name)
            )

        self._error_on_new_warn_on_construct(
            error_msg=self._check_external_file_starting_frame_length()
        )
        self._error_on_new_warn_on_construct(
            error_msg=self._check_external_file_format()
        )
        self._error_on_new_warn_on_construct(error_msg=self._check_external_file_data())

    def _change_external_file_format(self):
        """
        Change the format to 'external' when external_file is specified.
        """
        if (
            get_data_shape(self.data)[0] == 0
            and self.external_file is not None
            and self.format is None
        ):
            self.format = "external"
            return True

        return False

    def _check_time_series_dimension(self):
        """Override _check_time_series_dimension to do nothing.
        The _check_image_series_dimension method will be called instead.
        """
        return True

    def _check_image_series_dimension(self):
        """Check that the 0th dimension of data equals the length of timestamps, when applicable.

        ImageSeries objects can have an external file instead of data stored. The external file cannot be
        queried for the number of frames it contains, so this check will return True when an external file
        is provided. Otherwise, this function calls the parent class' _check_time_series_dimension method.
        """
        if self.external_file is not None:
            return True
        return super()._check_time_series_dimension()

    def _check_external_file_starting_frame_length(self):
        """
        Check that the number of frame indices in 'starting_frame' matches
        the number of files in 'external_file'.
        """
        if self.external_file is None:
            return
        if get_data_shape(self.external_file) == get_data_shape(self.starting_frame):
            return

        return (
            "%s '%s': The number of frame indices in 'starting_frame' should have "
            "the same length as 'external_file'." % (self.__class__.__name__, self.name)
        )

    def _check_external_file_format(self):
        """
        Check that format is 'external' when external_file is specified.
        """
        if self.external_file is None:
            return
        if self.format == "external":
            return

        return "%s '%s': Format must be 'external' when external_file is specified." % (
            self.__class__.__name__,
            self.name,
        )

    def _check_external_file_data(self):
        """
        Check that data is an empty array when external_file is specified.
        """
        if self.external_file is None:
            return
        if get_data_shape(self.data)[0] == 0:
            return

        return (
            "%s '%s': Either external_file or data must be specified (not None), but not both."
            % (self.__class__.__name__, self.name)
        )

    @property
    def bits_per_pixel(self):
        return self.fields.get('bits_per_pixel')

    @bits_per_pixel.setter
    def bits_per_pixel(self, val):
        if val is not None:
            warnings.warn("bits_per_pixel is no longer used", DeprecationWarning)
            self.fields['bits_per_pixel'] = val


@register_class('IndexSeries', CORE_NAMESPACE)
class IndexSeries(TimeSeries):
    '''
    Stores indices to image frames stored in an ImageSeries. The purpose of the IndexSeries is to allow
    a static image stack to be stored somewhere, and the images in the stack to be referenced out-of-order.
    This can be for the display of individual images, or of movie segments (as a movie is simply a series of
    images). The data field stores the index of the frame in the referenced ImageSeries, and the timestamps
    array indicates when that image was displayed.
    '''

    __nwbfields__ = ("indexed_timeseries",)

    # # value used when an ImageSeries is read and missing data
    # DEFAULT_UNIT = 'N/A'

    @docval(
        *get_docval(TimeSeries.__init__, 'name'),  # required
        {
            'name': 'data',
            'type': ('array_data', 'data', TimeSeries),
            'shape': (None,),  # required
            'doc': 'The data values. Must be 1D, where the first dimension must be time (frame)',
        },
        *get_docval(TimeSeries.__init__, 'unit'),  # required
        {
            'name': 'indexed_timeseries', 'type': TimeSeries,  # required
            'doc': 'Link to TimeSeries containing images that are indexed.',
            'default': None,
        },
        {
            'name': 'indexed_images',
            'type': Images,  # required
            'doc': "Link to Images object containing an ordered set of images that are indexed. The Images object must "
                   "contain a 'ordered_images' dataset specifying the order of the images in the Images type.",
            'default': None
        },
        *get_docval(
            TimeSeries.__init__,
            'resolution',
            'conversion',
            'timestamps',
            'starting_time',
            'rate',
            'comments',
            'description',
            'control',
            'control_description',
            'offset',
        ),
    )
    def __init__(self, **kwargs):
        indexed_timeseries, indexed_images = popargs('indexed_timeseries', 'indexed_images', kwargs)
        if kwargs['unit'] and kwargs['unit'] != 'N/A':
            msg = ("The 'unit' field of IndexSeries is fixed to the value 'N/A' starting in NWB 2.5. Passing "
                   "a different value for 'unit' will raise an error in PyNWB 3.0.")
            warnings.warn(msg, PendingDeprecationWarning)
        if not indexed_timeseries and not indexed_images:
            msg = "Either indexed_timeseries or indexed_images must be provided when creating an IndexSeries."
            raise ValueError(msg)
        if indexed_timeseries:
            msg = ("The indexed_timeseries field of IndexSeries is discouraged and will be deprecated in "
                   "a future version of NWB. Use the indexed_images field instead.")
            warnings.warn(msg, PendingDeprecationWarning)
        kwargs['unit'] = 'N/A'  # fixed value starting in NWB 2.5
        super().__init__(**kwargs)
        self.indexed_timeseries = indexed_timeseries
        self.indexed_images = indexed_images
        if kwargs['conversion'] and kwargs['conversion'] != self.DEFAULT_CONVERSION:
            warnings.warn("The conversion attribute is not used by IndexSeries.")
        if kwargs['resolution'] and kwargs['resolution'] != self.DEFAULT_RESOLUTION:
            warnings.warn("The resolution attribute is not used by IndexSeries.")
        if kwargs['offset'] and kwargs['offset'] != self.DEFAULT_OFFSET:
            warnings.warn("The offset attribute is not used by IndexSeries.")


@register_class('ImageMaskSeries', CORE_NAMESPACE)
class ImageMaskSeries(ImageSeries):
    '''
    An alpha mask that is applied to a presented visual stimulus. The data[] array contains an array
    of mask values that are applied to the displayed image. Mask values are stored as RGBA. Mask
    can vary with time. The timestamps array indicates the starting time of a mask, and that mask
    pattern continues until it's explicitly changed.
    '''

    __nwbfields__ = ('masked_imageseries',)

    @docval(*get_docval(ImageSeries.__init__, 'name'),  # required
            {'name': 'masked_imageseries', 'type': ImageSeries,  # required
             'doc': 'Link to ImageSeries that mask is applied to.'},
            *get_docval(ImageSeries.__init__, 'data', 'unit', 'format', 'external_file', 'starting_frame',
                        'bits_per_pixel', 'dimension', 'resolution', 'conversion', 'timestamps', 'starting_time',
                        'rate', 'comments', 'description', 'control', 'control_description', 'offset'),
            {'name': 'device', 'type': Device,
             'doc': ('Device used to capture the mask data. This field will likely not be needed. '
                     'The device used to capture the masked ImageSeries data should be stored in the ImageSeries.'),
             'default': None},)
    def __init__(self, **kwargs):
        masked_imageseries = popargs('masked_imageseries', kwargs)
        super().__init__(**kwargs)
        self.masked_imageseries = masked_imageseries


@register_class('OpticalSeries', CORE_NAMESPACE)
class OpticalSeries(ImageSeries):
    '''
    Image data that is presented or recorded. A stimulus template movie will be stored only as an
    image. When the image is presented as stimulus, additional data is required, such as field of
    view (eg, how much of the visual field the image covers, or how what is the area of the target
    being imaged). If the OpticalSeries represents acquired imaging data, orientation is also
    important.
    '''

    __nwbfields__ = ('distance',
                     'field_of_view',
                     'orientation')

    @docval(*get_docval(ImageSeries.__init__, 'name'),  # required
            {'name': 'distance', 'type': float, 'doc': 'Distance from camera/monitor to target/eye.'},  # required
            {'name': 'field_of_view', 'type': ('array_data', 'data', 'TimeSeries'), 'shape': ((2, ), (3, )),  # required
             'doc': 'Width, height and depth of image, or imaged area (meters).'},
            {'name': 'orientation', 'type': str,  # required
             'doc': 'Description of image relative to some reference frame (e.g., which way is up). '
                    'Must also specify frame of reference.'},
            {'name': 'data', 'type': ('array_data', 'data'), 'shape': ([None] * 3, [None, None, None, 3]),
             'doc': ('Images presented to subject, either grayscale or RGB. May be 3D or 4D. The first dimension must '
                     'be time (frame). The second and third dimensions represent x and y. The optional fourth '
                     'dimension must be length 3 and represents the RGB value for color images. Either data or '
                     'external_file must be specified, but not both.'),
             'default': None},
            *get_docval(ImageSeries.__init__, 'unit', 'format', 'external_file', 'starting_frame', 'bits_per_pixel',
                        'dimension', 'resolution', 'conversion', 'timestamps', 'starting_time', 'rate', 'comments',
                        'description', 'control', 'control_description', 'device', 'offset'))
    def __init__(self, **kwargs):
        distance, field_of_view, orientation = popargs('distance', 'field_of_view', 'orientation', kwargs)
        super().__init__(**kwargs)
        self.distance = distance
        self.field_of_view = field_of_view
        self.orientation = orientation


@register_class('GrayscaleImage', CORE_NAMESPACE)
class GrayscaleImage(Image):

    @docval(*get_docval(Image.__init__, 'name'),
            {'name': 'data', 'type': ('array_data', 'data'),
             'doc': 'Data of grayscale image. Must be 2D where the dimensions represent x and y.',
             'shape': (None, None)},
            *get_docval(Image.__init__, 'resolution', 'description'))
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


@register_class('RGBImage', CORE_NAMESPACE)
class RGBImage(Image):

    @docval(*get_docval(Image.__init__, 'name'),
            {'name': 'data', 'type': ('array_data', 'data'),
             'doc': 'Data of color image. Must be 3D where the first and second dimensions represent x and y. '
                    'The third dimension has length 3 and represents the RGB value.',
             'shape': (None, None, 3)},
            *get_docval(Image.__init__, 'resolution', 'description'))
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


@register_class('RGBAImage', CORE_NAMESPACE)
class RGBAImage(Image):

    @docval(*get_docval(Image.__init__, 'name'),
            {'name': 'data', 'type': ('array_data', 'data'),
             'doc': 'Data of color image with transparency. Must be 3D where the first and second dimensions '
                    'represent x and y. The third dimension has length 4 and represents the RGBA value.',
             'shape': (None, None, 4)},
            *get_docval(Image.__init__, 'resolution', 'description'))
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
