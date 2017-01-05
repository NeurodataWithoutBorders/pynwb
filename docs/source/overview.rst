.. _overview:

===============
Overview
===============

PyNWB provides a high-level Python API for reading and writing NWB formatted HDF5 files. This section will provide
a broad overview of the functionality provided for reading and writing neurophysiology into NWB files. 

The majority of data stored in NWB will done with :py:class:`~pynwb.ui.timeseries.TimeSeries` and :py:class:`~pynwb.ui.modules.Module`
Python objects. The following sections describe these classes in further detail.

---------------
TimeSeries
---------------

TimeSeries objects store time series data. These Python objects correspond to TimeSeries specifications
provided by the NWB format specification. Like the NWB specification, TimeSeries Python objects follow a an object-oriented inheritance
pattern. For example, the class :py:class:`~pynwb.ui.timeseries.TimeSeries` serves as the base class for all other TimeSeries types. 



The following TimeSeries objects are provided by the API and NWB specification:

#. :py:class:`~pynwb.ui.timeseries.TimeSeries`
#. :py:class:`~pynwb.ui.timeseries.ElectricalSeries`
#. :py:class:`~pynwb.ui.timeseries.SpikeEventSeries`
#. :py:class:`~pynwb.ui.timeseries.AnnotationSeries`
#. :py:class:`~pynwb.ui.timeseries.AbstractFeatureSeries`
#. :py:class:`~pynwb.ui.timeseries.ImageSeries`
#. :py:class:`~pynwb.ui.timeseries.ImageMaskSeries`
#. :py:class:`~pynwb.ui.timeseries.OpticalSeries`
#. :py:class:`~pynwb.ui.timeseries.TwoPhotonSeries`
#. :py:class:`~pynwb.ui.timeseries.IndexSeries`
#. :py:class:`~pynwb.ui.timeseries.IntervalSeries`
#. :py:class:`~pynwb.ui.timeseries.OptogeneticSeries`
#. :py:class:`~pynwb.ui.timeseries.PatchClampSeries`
#. :py:class:`~pynwb.ui.timeseries.CurrentClampSeries`
#. :py:class:`~pynwb.ui.timeseries.IZeroClampSeries`
#. :py:class:`~pynwb.ui.timeseries.CurrentClampStimulusSeries`
#. :py:class:`~pynwb.ui.timeseries.VoltageClampSeries`
#. :py:class:`~pynwb.ui.timeseries.VoltageClampStimulusSeries`
#. :py:class:`~pynwb.ui.timeseries.RoiResponseSeries`
#. :py:class:`~pynwb.ui.timeseries.SpatialSeries`

---------------
Modules
---------------
