.. _overview:

===============
Overview
===============

PyNWB provides a high-level Python API for reading and writing NWB formatted HDF5 files. This section will provide
a broad overview of the functionality provided for reading and writing neurophysiology into NWB files. 

The NWB format is built around two concepts: *TimeSeries* and *Modules*. TimeSeries are objects for storing time series
data, and Modules are objects for storing and grouping analyses. The following sections describe these classes in further detail.

---------------
TimeSeries
---------------

TimeSeries objects store time series data. These Python objects correspond to TimeSeries specifications
provided by the NWB format specification. Like the NWB specification, TimeSeries Python objects follow an object-oriented inheritance
pattern. For example, the class :py:class:`~pynwb.ui.timeseries.TimeSeries` serves as the base class for all other TimeSeries types.


The following TimeSeries objects are provided by the API and NWB specification:

* :py:class:`~pynwb.ui.timeseries.TimeSeries` - a general 

  * :py:class:`~pynwb.ui.timeseries.ElectricalSeries`

    * :py:class:`~pynwb.ui.timeseries.SpikeEventSeries`

  * :py:class:`~pynwb.ui.timeseries.AnnotationSeries`
  * :py:class:`~pynwb.ui.timeseries.AbstractFeatureSeries`
  * :py:class:`~pynwb.ui.timeseries.ImageSeries`

    * :py:class:`~pynwb.ui.timeseries.ImageMaskSeries`
    * :py:class:`~pynwb.ui.timeseries.OpticalSeries`
    * :py:class:`~pynwb.ui.timeseries.TwoPhotonSeries`

  * :py:class:`~pynwb.ui.timeseries.IndexSeries`
  * :py:class:`~pynwb.ui.timeseries.IntervalSeries`
  * :py:class:`~pynwb.ui.timeseries.OptogeneticSeries`
  * :py:class:`~pynwb.ui.timeseries.PatchClampSeries`

    * :py:class:`~pynwb.ui.timeseries.CurrentClampSeries`

      * :py:class:`~pynwb.ui.timeseries.IZeroClampSeries`

    * :py:class:`~pynwb.ui.timeseries.CurrentClampStimulusSeries`
    * :py:class:`~pynwb.ui.timeseries.VoltageClampSeries`
    * :py:class:`~pynwb.ui.timeseries.VoltageClampStimulusSeries`

  * :py:class:`~pynwb.ui.timeseries.RoiResponseSeries`
  * :py:class:`~pynwb.ui.timeseries.SpatialSeries`

---------------
Modules
---------------

Modules are objects that group together common analyses done during processing of data. Module objects are unique collections of 
analysis results. To standardize the storage of common analyses, NWB provides the concept of an *Interface*, where the output of 
common analyses are represented as objects that extend the :py:class:`~pynwb.ui.iface.Interface` class. In most cases, you will not need
to interact with the :py:class:`~pynwb.ui.iface.Interface` class directly. More commonly, you will be creating instances of classes that
extend this class. For example, a common analysis step for spike data (represented in NWB as a :py:class:`~pynwb.ui.timeseries.SpikeEventSeries` object)
is spike clustering. In NWB, the result of kind of analysis will be reprsented with a :py:class:`~pynwb.ui.module.Clustering` object.


The following Interface objects are provided by the API and NWB specification:

* :py:class:`~pynwb.ui.iface.Interface`

  * :py:class:`~pynwb.ui.module.BehavioralEpochs`
  * :py:class:`~pynwb.ui.module.BehavioralEvents`
  * :py:class:`~pynwb.ui.module.BehavioralTimeSeries`
  * :py:class:`~pynwb.ui.module.ClusterWaveforms`
  * :py:class:`~pynwb.ui.module.Clustering`
  * :py:class:`~pynwb.ui.module.CompassDirection`
  * :py:class:`~pynwb.ui.module.DfOverF`
  * :py:class:`~pynwb.ui.module.EventDetection`
  * :py:class:`~pynwb.ui.module.EventWaveform`
  * :py:class:`~pynwb.ui.module.EyeTracking`
  * :py:class:`~pynwb.ui.module.FeatureExtraction`
  * :py:class:`~pynwb.ui.module.FilteredEphys`
  * :py:class:`~pynwb.ui.module.Fluorescence`
  * :py:class:`~pynwb.ui.module.ImageSegmentation`
  * :py:class:`~pynwb.ui.module.ImagingRetinotopy`
  * :py:class:`~pynwb.ui.module.LFP`
  * :py:class:`~pynwb.ui.module.MotionCorrection`
  * :py:class:`~pynwb.ui.module.Position`

