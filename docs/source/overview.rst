.. _overview:

Overview
===============

PyNWB provides a high-level Python API for reading and writing NWB formatted HDF5 files. This section will provide
a broad overview of the functionality provided for reading and writing neurophysiology data into NWB files.


The NWB format is built around two concepts: *TimeSeries* and *Modules*. :ref:`timeseries_overview` are objects for storing time series
data, and :ref:`modules_overview` are objects for storing and grouping analyses. The following sections describe these classes in further detail.

.. _file_overview:

NWBFile
---------------

NWB files are represented in PyNWB with *NWBFile* objects. :py:class:`~pynwb.file.NWBFile` objects provide functionality for creating :ref:`timeseries_overview` datasets
and :ref:`modules_overview`, as well as functionality for storing experimental metadata and other metadata related to data provenance.

.. _timeseries_overview:

TimeSeries
---------------

TimeSeries objects store time series data. These Python objects correspond to TimeSeries specifications
provided by the NWB format specification. Like the NWB specification, TimeSeries Python objects follow an object-oriented inheritance
pattern. For example, the class :py:class:`~pynwb.base.TimeSeries` serves as the base class for all other TimeSeries types.


The following TimeSeries objects are provided by the API and NWB specification:

* :py:class:`~pynwb.base.TimeSeries` - a general

  * :py:class:`~pynwb.ecephys.ElectricalSeries`

    * :py:class:`~pynwb.ecephys.SpikeEventSeries`

  * :py:class:`~pynwb.misc.AnnotationSeries`
  * :py:class:`~pynwb.misc.AbstractFeatureSeries`
  * :py:class:`~pynwb.image.ImageSeries`

    * :py:class:`~pynwb.image.ImageMaskSeries`
    * :py:class:`~pynwb.image.OpticalSeries`
    * :py:class:`~pynwb.ophys.TwoPhotonSeries`

  * :py:class:`~pynwb.image.IndexSeries`
  * :py:class:`~pynwb.misc.IntervalSeries`
  * :py:class:`~pynwb.ophys.OptogeneticSeries`
  * :py:class:`~pynwb.icephys.PatchClampSeries`

    * :py:class:`~pynwb.icephys.CurrentClampSeries`

      * :py:class:`~pynwb.icephys.IZeroClampSeries`

    * :py:class:`~pynwb.icephys.CurrentClampStimulusSeries`
    * :py:class:`~pynwb.icephys.VoltageClampSeries`
    * :py:class:`~pynwb.icephys.VoltageClampStimulusSeries`

  * :py:class:`~pynwb.ophys.RoiResponseSeries`
  * :py:class:`~pynwb.behavior.SpatialSeries`


.. _modules_overview:

Modules
---------------

Modules are objects that group together common analyses done during processing of data. Module objects are unique collections of
analysis results. To standardize the storage of common analyses, NWB provides the concept of an *Interface*, where the output of
common analyses are represented as objects that extend the :py:class:`~pynwb.base.Interface` class. In most cases, you will not need
to interact with the :py:class:`~pynwb.base.Interface` class directly. More commonly, you will be creating instances of classes that
extend this class. For example, a common analysis step for spike data (represented in NWB as a :py:class:`~pynwb.ecephys.SpikeEventSeries` object)
is spike clustering. In NWB, the result of kind of analysis will be reprsented with a :py:class:`~pynwb.ecephys.Clustering` object.


The following Interface objects are provided by the API and NWB specification:

* :py:class:`~pynwb.ui.iface.Interface`

  * :py:class:`~pynwb.behavior.BehavioralEpochs`
  * :py:class:`~pynwb.behavior.BehavioralEvents`
  * :py:class:`~pynwb.behavior.BehavioralTimeSeries`
  * :py:class:`~pynwb.ecephys.ClusterWaveforms`
  * :py:class:`~pynwb.ecephys.Clustering`
  * :py:class:`~pynwb.behavior.CompassDirection`
  * :py:class:`~pynwb.ophys.DfOverF`
  * :py:class:`~pynwb.ecephys.EventDetection`
  * :py:class:`~pynwb.ecephys.EventWaveform`
  * :py:class:`~pynwb.behavior.EyeTracking`
  * :py:class:`~pynwb.ecephys.FeatureExtraction`
  * :py:class:`~pynwb.ecephys.FilteredEphys`
  * :py:class:`~pynwb.ophys.Fluorescence`
  * :py:class:`~pynwb.ophys.ImageSegmentation`
  * :py:class:`~pynwb.retinotopy.ImagingRetinotopy`
  * :py:class:`~pynwb.ecephys.LFP`
  * :py:class:`~pynwb.behavior.MotionCorrection`
  * :py:class:`~pynwb.behavior.Position`

