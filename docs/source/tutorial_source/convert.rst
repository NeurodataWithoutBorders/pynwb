.. _tutorial_convert:

Convert
=========================

The following are example Jupyter notebooks for converting custom lab data to NWB:

crcns-ret-1: Meister lab retina data
------------------------------------

* **Notebook:** http://nbviewer.jupyter.org/urls/bitbucket.org/lblneuro/pynwb/raw/dev/docs/notebooks/convert-crcns-ret-1-meisterlab-with-custom-extensions-and-external-stimulus.ipynb
* **Example:** This example shows:

    * Use of ``UnitTimes``, ``SpikeUnit``, ``ImageSeries``, ``ElectrodeGroup``, ``EpochTimeSeries``, ``Device``
    * Creation and use of custom namespace and extension to extend ``ImageSeries`` to add custom metadata attributes
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

* **Previous/Alternative Variants:**

    * http://nbviewer.jupyter.org/urls/bitbucket.org/lblneuro/pynwb/raw/dev/docs/notebooks/convert-crcns-ret-1-meisterlab-with-custom-extensions.ipynb :
      This notebook is very similar but instead of storing stimuli in external HDF5 files that are linked to via
      external links we here store all data directly in the NWB file.
    * http://nbviewer.jupyter.org/urls/bitbucket.org/lblneuro/pynwb/raw/dev/docs/notebooks/convert-crcns-ret-1-meisterlab-without-custom-extensions.ipynb :
      This is an older variant of the notebook that shows the convert without the use of custom extensions
      (as well as no external links).


