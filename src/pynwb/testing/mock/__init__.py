"""
The mock module provides mock instances of common neurodata types which can be used to write
tests for downstream libraries. For instance, to write an RoiResponseSeries, you need a
PlaneSegmentation, which requires an ImagingPlane, which in turn requires an
OpticalChannel and a Device, all of which need to be populated with reasonable mock
data. This library streamlines the process of creating mock objects by generating the
required prerequisites for this object on-the-fly and automatically using reasonable
defaults. Any of these default objects and parameters can be overridden.
"""
