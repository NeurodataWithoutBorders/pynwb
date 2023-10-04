Mock
====

When creating tests within PyNWB and in downstream libraries, it is often necessary to create example instances of
neurodata objects. However, this can be quite laborious for some types. For instance, creating an
:py:class:`~pynwb.ophys.RoiResponseSeries` would require you to make a
:py:class:`~hdmf.common.table.DynamicTableRegion` of a :py:class:`~pynwb.ophys.PlaneSegmentation` table
with the appropriate rows. This object in turn requires input of an :py:class:`~pynwb.ophys.ImageSegmentation` object,
which in turn requires a :py:class:`~pynwb.device.Device` and an :py:class:`~pynwb.ophys.OpticalChannel` object. In
the end, creating a single neurodata object in this case requires the creation of 5 other objects.
:py:mod:`.testing.mock` is a module that creates boilerplate objects with a single line of code that can be used for
testing. In this case, you could simply run

.. code-block:: python

    from pynwb.testing.mock.ophys import mock_RoiResponseSeries

    roi_response_series = mock_RoiResponseSeries()

This acts much like the standard :py:class:`~pynwb.ophys.RoiResponseSeries` class constructor, except that `all` of the fields have
defaults. It auto-magically creates a :py:class:`~hdmf.common.table.DynamicTableRegion` of a
:py:class:`~pynwb.testing.mock.ophys.mock_PlaneSegmentation`, which in turn calls the ``mock`` version of all the other
necessary neurodata types. You can customize any of these fields just as you would normally, overriding these defaults:

.. code-block:: python

    from pynwb.testing.mock.ophys import mock_RoiResponseSeries

    roi_response_series = mock_RoiResponseSeries(data=[[1,2,3], [1,2,3]])


If you want to create objects and automatically add them to an :py:class:`~pynwb.file.NWBFile`, create an
:py:class:`~pynwb.file.NWBFile` and pass it into the mock function:

.. code-block:: python

    from pynwb.testing.mock.file import mock_NWBFile
    from pynwb.testing.mock.ophys import mock_RoiResponseSeries

    nwbfile = mock_NWBFile()
    mock_RoiResponseSeries(nwbfile=nwbfile)

Now this NWBFile contains an :py:class:`~pynwb.ophys.RoiResponseSeries` and all the upstream classes:

.. code-block::

    >>> print(nwbfile)

    root pynwb.file.NWBFile at 0x4335131760
    Fields:
      devices: {
        Device <class 'pynwb.device.Device'>,
        Device2 <class 'pynwb.device.Device'>
      }
      file_create_date: [datetime.datetime(2023, 6, 26, 21, 56, 44, 322249, tzinfo=tzlocal())]
      identifier: 3c13e816-a50f-49a9-85ec-93b9944c3e79
      imaging_planes: {
        ImagingPlane <class 'pynwb.ophys.ImagingPlane'>,
        ImagingPlane2 <class 'pynwb.ophys.ImagingPlane'>
      }
      processing: {
        ophys <class 'pynwb.base.ProcessingModule'>
      }
      session_description: session_description
      session_start_time: 1970-01-01 00:00:00-05:00
      timestamps_reference_time: 1970-01-01 00:00:00-05:00


Name generator
--------------
Two neurodata objects stored in the same location within an NWB file must have unique names. This can cause an error
if you want to create a few neurodata objects with the same default name. To avoid this issue, each mock neurodata
function uses the :py:func:`~pynwb.testing.mock.utils.name_generator` to generate unique names for each neurodata
object. Consecutive neurodata objects of the same type will be named e.g. "TimeSeries", "TimeSeries2", "TimeSeries3",
etc.