.. _tutorial_convert:

Convert
=========================

The following are example Jupyter notebooks for converting custom lab data to NWB:

crcns-ret-1: Meister lab retina data
------------------------------------

* **Notebook:** http://tinyurl.com/ybxyqup2
* **Example:** This example shows:

    * Use of ``UnitTimes``, ``SpikeUnit``, ``ImageSeries``, ``ElectrodeGroup``, ``EpochTimeSeries``, ``Device``
    * Creation and use of custom namespace and extension to extend ``ImageSeries`` to custom add metadata attributes
    * Create external link for ``ImageSeries.data``
    * Read of crcns-ret-1 dataset
    * Convert of the data to NWB
    * Comparison of H5Gate and PyNWB

* **Data:** Convert single-unit neural responses recorded from
  isolated retina from lab mice (Mus Musculus) using
  a 61-electrode array in response to various visual
  stimuli.  Recordings were done by Yifeng Zhang in
  Markus Meister's lab at Harvard University in 2008.
  Further description of the data are available here:
  http://crcns.org/data-sets/retina/ret-1/about-ret-1

* **Variants:**

    * ... This notebook is very similar but instead of storing stimuli in external HDF5 file linked to via
      external links we here store all data directly in the NWB file. In addition, the following notebook
      shows a variant of the example without the use of extensions (as well as no external links).


