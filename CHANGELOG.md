# PyNWB Changelog

## PyNWB 2.8.1 (July 3, 2024)

### Documentation and tutorial enhancements
- Simplified the introduction to NWB tutorial. @rly [#1914](https://github.com/NeurodataWithoutBorders/pynwb/pull/1914)
- Simplified the ecephys and ophys tutorials. [#1915](https://github.com/NeurodataWithoutBorders/pynwb/pull/1915)
- Add comments to `src/pynwb/io/file.py` to improve developer documentation. @rly [#1925](https://github.com/NeurodataWithoutBorders/pynwb/pull/1925)

### Bug fixes
- Fixed use of `channel_conversion` in `TimeSeries` `get_data_in_units`. @rohanshah [1923](https://github.com/NeurodataWithoutBorders/pynwb/pull/1923)


## PyNWB 2.8.0 (May 28, 2024)

### Enhancements and minor changes
- Set rate default value inside `mock_ElectricalSeries` to avoid having to set `rate=None` explicitly when passing timestamps. @h-mayorquin [#1894](https://github.com/NeurodataWithoutBorders/pynwb/pull/1894)
- Integrate validation through the `TypeConfigurator`. @mavaylon1 [#1829](https://github.com/NeurodataWithoutBorders/pynwb/pull/1829)
- Exposed `aws_region` to `NWBHDF5IO`. @rly [#1903](https://github.com/NeurodataWithoutBorders/pynwb/pull/1903)

### Bug fixes
- Revert changes in PyNWB 2.7.0 that allow datetimes without a timezone and without a time while issues with DANDI upload of NWB files missing timezone are resolved. @rly [#1908](https://github.com/NeurodataWithoutBorders/pynwb/pull/1908)

## PyNWB 2.7.0 (May 2, 2024)

### Enhancements and minor changes
- Added `bounds` field to `SpatialSeries` to set optional boundary range (min, max) for each dimension of data. @mavaylon1 [#1869](https://github.com/NeurodataWithoutBorders/pynwb/pull/1869/files)
- Added support for NWB schema 2.7.0. See [2.7.0 release notes](https://nwb-schema.readthedocs.io/en/latest/format_release_notes.html) for details
- Deprecated `ImagingRetinotopy` neurodata type. @rly [#1813](https://github.com/NeurodataWithoutBorders/pynwb/pull/1813)
- Modified `OptogeneticSeries` to allow 2D data, primarily in extensions of `OptogeneticSeries`. @rly [#1812](https://github.com/NeurodataWithoutBorders/pynwb/pull/1812)
- Support `stimulus_template` as optional predefined column in `IntracellularStimuliTable`. @stephprince [#1815](https://github.com/NeurodataWithoutBorders/pynwb/pull/1815)
- Support `NWBDataInterface` and `DynamicTable` in `NWBFile.stimulus`. @rly [#1842](https://github.com/NeurodataWithoutBorders/pynwb/pull/1842)
- Added support for python 3.12 and upgraded dependency versions. This also includes infrastructure updates for developers. @mavaylon1 [#1853](https://github.com/NeurodataWithoutBorders/pynwb/pull/1853)
- Added `grid_spacing`, `grid_spacing_unit`, `origin_coords`, `origin_coords_unit` to `ImagingPlane` fields. @h-mayorquin [#1892](https://github.com/NeurodataWithoutBorders/pynwb/pull/1892)
- Added `mock_Units` for generating Units tables. @h-mayorquin [#1875](https://github.com/NeurodataWithoutBorders/pynwb/pull/1875) and [#1883](https://github.com/NeurodataWithoutBorders/pynwb/pull/1883)
- Allow datetimes without a timezone and without a time. @rly [#1886](https://github.com/NeurodataWithoutBorders/pynwb/pull/1886)
- No longer automatically set the timezone to the local timezone when not provided. [#1886](https://github.com/NeurodataWithoutBorders/pynwb/pull/1886)
- Updated testing to not install in editable mode and not run `coverage` by default. [#1897](https://github.com/NeurodataWithoutBorders/pynwb/pull/1897)

### Bug fixes
- Fix bug with reading file with linked `TimeSeriesReferenceVectorData` @rly [#1865](https://github.com/NeurodataWithoutBorders/pynwb/pull/1865)
- Fix bug where extra keyword arguments could not be passed to `NWBFile.add_{x}_column` for use in custom `VectorData` classes. @rly [#1861](https://github.com/NeurodataWithoutBorders/pynwb/pull/1861)

## PyNWB 2.6.0 (February 21, 2024)

### Enhancements and minor changes
- For `NWBHDF5IO()`, change the default of arg `load_namespaces` from `False` to `True`. @bendichter [#1748](https://github.com/NeurodataWithoutBorders/pynwb/pull/1748)
- Add `NWBHDF5IO.can_read()`. @bendichter [#1703](https://github.com/NeurodataWithoutBorders/pynwb/pull/1703)
- Add `pynwb.get_nwbfile_version()`. @bendichter [#1703](https://github.com/NeurodataWithoutBorders/pynwb/pull/1703)
- Fix usage of the `validate` function in the `pynwb.testing.testh5io` classes and cache the spec by default in those classes. @rly [#1782](https://github.com/NeurodataWithoutBorders/pynwb/pull/1782)
- Updated timeseries data checks to warn instead of error when reading invalid files. @stephprince [#1793](https://github.com/NeurodataWithoutBorders/pynwb/pull/1793) and [#1809](https://github.com/NeurodataWithoutBorders/pynwb/pull/1809)
- Expose the offset, conversion and channel conversion parameters in `mock_ElectricalSeries`. @h-mayorquin [#1796](https://github.com/NeurodataWithoutBorders/pynwb/pull/1796)
- Expose `starting_time` in `mock_ElectricalSeries`. @h-mayorquin [#1805](https://github.com/NeurodataWithoutBorders/pynwb/pull/1805)
- Enhance `get_data_in_units()` to work with objects that have a `channel_conversion` attribute like the `ElectricalSeries`. @h-mayorquin [#1806](https://github.com/NeurodataWithoutBorders/pynwb/pull/1806)
- Refactor validation CLI tests to use `{sys.executable} -m coverage` to use the same Python version and run correctly on Debian systems. @yarikoptic [#1811](https://github.com/NeurodataWithoutBorders/pynwb/pull/1811)
- Fixed tests to address newly caught validation errors. @rly [#1839](https://github.com/NeurodataWithoutBorders/pynwb/pull/1839)

### Bug fixes
- Fix bug where namespaces were loaded in "w-" mode. @h-mayorquin [#1795](https://github.com/NeurodataWithoutBorders/pynwb/pull/1795)
- Fix bug where pynwb version was reported as "unknown" to readthedocs @stephprince [#1810](https://github.com/NeurodataWithoutBorders/pynwb/pull/1810)
- Fixed bug to allow linking of `TimeSeries.data` by setting the `data` constructor argument to another `TimeSeries`. @oruebel [#1766](https://github.com/NeurodataWithoutBorders/pynwb/pull/1766)
- Fix recursion error in html representation generation in jupyter notebooks. @stephprince [#1831](https://github.com/NeurodataWithoutBorders/pynwb/pull/1831)

### Documentation and tutorial enhancements
- Add RemFile to streaming tutorial. @bendichter [#1761](https://github.com/NeurodataWithoutBorders/pynwb/pull/1761)
- Fix typos and improve clarify throughout tutorials. @zm711 [#1825](https://github.com/NeurodataWithoutBorders/pynwb/pull/1825)
- Fix internal links in docstrings and tutorials. @stephprince [#1827](https://github.com/NeurodataWithoutBorders/pynwb/pull/1827)
- Add Zarr IO tutorial @bendichter [#1834](https://github.com/NeurodataWithoutBorders/pynwb/pull/1834)

## PyNWB 2.5.0 (August 18, 2023)

### Enhancements and minor changes
- Added `TimeSeries.get_timestamps()`. @bendichter [#1741](https://github.com/NeurodataWithoutBorders/pynwb/pull/1741)
- Added `TimeSeries.get_data_in_units()`. @bendichter [#1745](https://github.com/NeurodataWithoutBorders/pynwb/pull/1745)
- Updated `ExternalResources` name change to `HERD`, along with HDMF 3.9.0 being the new minimum. @mavaylon1 [#1754](https://github.com/NeurodataWithoutBorders/pynwb/pull/1754)

### Documentation and tutorial enhancements
- Updated streaming tutorial to ensure code is run on tests and clarify text. @bendichter [#1760](https://github.com/NeurodataWithoutBorders/pynwb/pull/1760) @oruebel [#1762](https://github.com/NeurodataWithoutBorders/pynwb/pull/1762)
- Fixed minor documentation build warnings and broken links to `basic_trials` tutorial  @oruebel [#1762](https://github.com/NeurodataWithoutBorders/pynwb/pull/1762)

## PyNWB 2.4.1 (July 26, 2023)
- Stop running validation tests as part of integration tests. They cause issues in CI and can be run separately. @rly [#1740](https://github.com/NeurodataWithoutBorders/pynwb/pull/1740)

## PyNWB 2.4.0 (July 23, 2023)

### Enhancements and minor changes
- Added support for `ExternalResources`. @mavaylon1 [#1684](https://github.com/NeurodataWithoutBorders/pynwb/pull/1684)
- Updated links for making a release. @mavaylon1 [#1720](https://github.com/NeurodataWithoutBorders/pynwb/pull/1720)

### Bug fixes
- Fixed sphinx-gallery setting to correctly display index in the docs with sphinx-gallery>=0.11. @oruebel [#1733](https://github.com/NeurodataWithoutBorders/pynwb/pull/1733)

### Documentation and tutorial enhancements
- Added thumbnail for Optogentics tutorial. @oruebel [#1729](https://github.com/NeurodataWithoutBorders/pynwb/pull/1729)
- Updated and fixed errors in tutorials. @bendichter @oruebel

## PyNWB 2.3.3 (June 26, 2023)

### Enhancements and minor changes
- Add testing support for Python 3.11. @rly [#1687](https://github.com/NeurodataWithoutBorders/pynwb/pull/1687)
- Add CI testing of NWB files on DANDI. @rly [#1695](https://github.com/NeurodataWithoutBorders/pynwb/pull/1695)

### Bug fixes
- Remove unused, deprecated `codecov` package from dev installation requirements. @rly
  [#1688](https://github.com/NeurodataWithoutBorders/pynwb/pull/1688)
- Remove references to discontinued `requires.io` service in documentation. @rly
  [#1690](https://github.com/NeurodataWithoutBorders/pynwb/pull/1690)
- Update `requirements-doc.txt` to resolve Python 3.7 incompatibility. @rly
  [#1694](https://github.com/NeurodataWithoutBorders/pynwb/pull/1694)
- Fixed test battery to show and check for warnings appropriately. @rly
  [#1698](https://github.com/NeurodataWithoutBorders/pynwb/pull/1698)

## PyNWB 2.3.2 (April 10, 2023)

### Enhancements and minor changes
- Fixed typos and added codespell GitHub action to check spelling in the future. @yarikoptic [#1648](https://github.com/NeurodataWithoutBorders/pynwb/pull/1648)

### Documentation and tutorial enhancements
- Added `OnePhotonSeries` to [calcium imaging tutorial](https://pynwb.readthedocs.io/en/stable/tutorials/domain/ophys.html#sphx-glr-tutorials-domain-ophys-py). @bendichter [#1658](https://github.com/NeurodataWithoutBorders/pynwb/pull/1658)
- Add tutorial for optogenetics. @bendichter [#1657](https://github.com/NeurodataWithoutBorders/pynwb/pull/1657)
- Update testing of gallery examples and disable testing of the allensdk tutorial.
  [#1680](https://github.com/NeurodataWithoutBorders/pynwb/pull/1680)
- Updated tutorials to follow best practices. @bendichter [#1656](https://github.com/NeurodataWithoutBorders/pynwb/pull/1656)

### Bug fixes
- Fixed bug when initializing ``OnePhotonSeries`` with no value for ``binning``. @bendichter [#1660](https://github.com/NeurodataWithoutBorders/pynwb/pull/1660)
- Fixed bug in ``NWBHDF5IO.nwb_version`` property to support files written by third-party software with a fixed-length ``nwb_version`` attribute. @oruebel [#1669](https://github.com/NeurodataWithoutBorders/pynwb/pull/1669)
- Fixed search bar and missing jquery in ReadTheDocs documentation. @rly [#1671](https://github.com/NeurodataWithoutBorders/pynwb/pull/1671)
- Requires [HDMF 3.5.4](https://github.com/hdmf-dev/hdmf/releases/tag/3.5.4) which includes bug fixes. @rly [#1672](https://github.com/NeurodataWithoutBorders/pynwb/pull/1672)
- Fixed issue with deprecated pkg_resources. @rly [#1678](https://github.com/NeurodataWithoutBorders/pynwb/pull/1678)

## PyNWB 2.3.1 (February 24, 2023)

### Bug fixes
- Fixed an issue where  NWB files with version "2.0b" could not be read.
  @rly [#1651](https://github.com/NeurodataWithoutBorders/pynwb/pull/1651)

## PyNWB 2.3.0 (February 23, 2023)

### Enhancements and minor changes
- Added support for NWB Schema 2.6.0. @mavaylon1 [#1636](https://github.com/NeurodataWithoutBorders/pynwb/pull/1636)
- Added a class and tests for the `OnePhotonSeries` new in NWB v2.6.0. @CodyCBakerPhD [#1593](https://github.com/NeurodataWithoutBorders/pynwb/pull/1593)(see also NWB Schema [#523](https://github.com/NeurodataWithoutBorders/nwb-schema/pull/523)
- `Subject.age` can be input as a `timedelta` type. @bendichter [#1590](https://github.com/NeurodataWithoutBorders/pynwb/pull/1590)
- Added `Subject.age__reference` field. @bendichter ([#1540](https://github.com/NeurodataWithoutBorders/pynwb/pull/1540))
- `IntracellularRecordingsTable.add_recording`: the `electrode` arg is now optional, and is automatically populated from the stimulus or response.
  [#1597](https://github.com/NeurodataWithoutBorders/pynwb/pull/1597)
- Added module `pynwb.testing.mock.icephys` and corresponding tests. @bendichter
  [1595](https://github.com/NeurodataWithoutBorders/pynwb/pull/1595)
- Removed redundant object mapper code. @rly [#1600](https://github.com/NeurodataWithoutBorders/pynwb/pull/1600)
- Fixed pending deprecations and issues in CI. @rly [#1594](https://github.com/NeurodataWithoutBorders/pynwb/pull/1594)
- Added ``NWBHDF5IO.nwb_version`` property to get the NWB version from an NWB HDF5 file @oruebel [#1612](https://github.com/NeurodataWithoutBorders/pynwb/pull/1612)
- Updated ``NWBHDF5IO.read`` to check NWB version before read and raise more informative error if an unsupported version is found @oruebel [#1612](https://github.com/NeurodataWithoutBorders/pynwb/pull/1612)
- Added the `driver` keyword argument to the `pynwb.validate` function as well as the corresponding namespace caching. @CodyCBakerPhD [#1588](https://github.com/NeurodataWithoutBorders/pynwb/pull/1588)
- Updated HDMF requirement to version 3.5.1. [#1611](https://github.com/NeurodataWithoutBorders/pynwb/pull/1611)
- Increased the stacklevel of the warning from `_add_missing_timezone` in `pynwb.file` to make identification of which datetime field is missing a timezone easier. @CodyCBakerPhD [#1641](https://github.com/NeurodataWithoutBorders/pynwb/pull/1641)

### Documentation and tutorial enhancements:
- Adjusted [ecephys tutorial](https://pynwb.readthedocs.io/en/stable/tutorials/domain/ecephys.html) to create fake data with proper dimensions @bendichter [#1581](https://github.com/NeurodataWithoutBorders/pynwb/pull/1581)
- Refactored testing documentation, including addition of section on ``pynwb.testing.mock`` submodule. @bendichter
  [#1583](https://github.com/NeurodataWithoutBorders/pynwb/pull/1583)
- Updated round trip tutorial to the newer ``NWBH5IOMixin`` and ``AcquisitionH5IOMixin`` classes. @bendichter
  [#1586](https://github.com/NeurodataWithoutBorders/pynwb/pull/1586)
- Added more informative error message for common installation error. @bendichter, @rly
  [#1591](https://github.com/NeurodataWithoutBorders/pynwb/pull/1591)
- Updated citation for PyNWB in docs and duecredit to use the eLife NWB paper. @oruebel [#1604](https://github.com/NeurodataWithoutBorders/pynwb/pull/1604)
- Fixed docs build warnings due to use of hardcoded links. @oruebel [#1604](https://github.com/NeurodataWithoutBorders/pynwb/pull/1604)
- Updated the [iterative write tutorial](https://pynwb.readthedocs.io/en/stable/tutorials/advanced_io/iterative_write.html) to reference the new ``GenericDataChunkIterator`` functionality and use the new ``H5DataIO.dataset`` property to simplify the custom I/O section. @oruebel [#1633](https://github.com/NeurodataWithoutBorders/pynwb/pull/1633)
- Updated the [parallel I/O tutorial](https://pynwb.readthedocs.io/en/stable/tutorials/advanced_io/parallelio.html) to use the new ``H5DataIO.dataset`` feature to set up an empty dataset for parallel write. @oruebel [#1633](https://github.com/NeurodataWithoutBorders/pynwb/pull/1633)

### Bug fixes
- Added shape constraint to `PatchClampSeries.data`. @bendichter
  [#1596](https://github.com/NeurodataWithoutBorders/pynwb/pull/1596)
- Updated the [images tutorial](https://pynwb.readthedocs.io/en/stable/tutorials/domain/images.html) to provide example usage of an ``IndexSeries``
  with a reference to ``Images``. @bendichter [#1602](https://github.com/NeurodataWithoutBorders/pynwb/pull/1602)
- Fixed an issue with the `tox` tool when upgrading to tox 4. @rly [#1608](https://github.com/NeurodataWithoutBorders/pynwb/pull/1608)
- Fixed an issue where `Images` were not allowed as stimulus templates. @rly [#1638](https://github.com/NeurodataWithoutBorders/pynwb/pull/1638)

## PyNWB 2.2.0 (October 19, 2022)

### Enhancements and minor changes
- Enhanced `pynwb.validate` API function to accept a list of file paths as well as the ability to operate on cached
  namespaces. Also adjusted the validate CLI to directly use the API function. @CodyCBakerPhD
  [#1511](https://github.com/NeurodataWithoutBorders/pynwb/pull/1511)

### Internal enhancements
- Moved CI to GitHub Actions. @rly [#1560](https://github.com/NeurodataWithoutBorders/pynwb/pull/1560),
  [#1566](https://github.com/NeurodataWithoutBorders/pynwb/pull/1566)

### Bug fixes
- Fixed bug in ``pynwb.testing.mock.file.mock_NWBFile`` to identifier UUID to string. @oruebel
  [#1557](https://github.com/NeurodataWithoutBorders/pynwb/pull/1557)
- Minor fixes to test suite to prevent warnings. @rly
  [#1571](https://github.com/NeurodataWithoutBorders/pynwb/pull/1571)
- Made build wheel python 3 only. @mavaylon1
  [#1572](https://github.com/NeurodataWithoutBorders/pynwb/pull/1572)
- Updated README.rst. @mavaylon1
  [#1573](https://github.com/NeurodataWithoutBorders/pynwb/pull/1573)

## PyNWB 2.1.1 (September 1, 2022)

### Documentation and tutorial enhancements:
- Added support for explicit ordering of sphinx gallery tutorials in the docs. @oruebel
  [#1504](https://github.com/NeurodataWithoutBorders/pynwb/pull/1504), @bdichter
  [#1495](https://github.com/NeurodataWithoutBorders/pynwb/pull/1495)
- Added developer guide on how to create a new tutorial. @oruebel
  [#1504](https://github.com/NeurodataWithoutBorders/pynwb/pull/1504)
- Added images tutorial. @weiglszonja
  [#1470](https://github.com/NeurodataWithoutBorders/pynwb/pull/1470)
- Added example code for fsspec in the streaming tutorial. @bdichter
  [#1499](https://github.com/NeurodataWithoutBorders/pynwb/pull/1499)
- Add voxel_mask tutorial. @codycbakerphd (#1544)

### Enhancements and minor changes
- Updated coverage workflow, report separate unit vs integration coverage. @rly
  [#1509](https://github.com/NeurodataWithoutBorders/pynwb/pull/1509)
- Deleted test files generated from running sphinx gallery examples. @rly
  [#1517](https://github.com/NeurodataWithoutBorders/pynwb/pull/1517)
- Enabled passing an S3File created through s3fs, which provides a method for reading an NWB file directly
  from s3 that is an alternative to ros3. This required relaxing of `NWBHDF5IO` input validation. The `path`
  arg is not needed if `file` is provided. `mode` now has a default value of "r".
  @bendichter
  [#1499](https://github.com/NeurodataWithoutBorders/pynwb/pull/1499)
- Added a method to `NWBMixin` that only raises an error when a check is violated on instance creation,
  otherwise throws a warning when reading from a file. The new checks in `ImageSeries` when `external_file`
  is provided is used with this method to ensure that that files with invalid data can be read, but prohibits
  the user from creating new instances when these checks are violated. @weiglszonja
  [#1516](https://github.com/NeurodataWithoutBorders/pynwb/pull/1516)
- Created a GitHub Actions workflow to generate test files for testing backward compatibility. @rly
  [#1548](https://github.com/NeurodataWithoutBorders/pynwb/pull/1548)
- Updated requirements, including allowing numpy 1.23. @rly
  [#1550](https://github.com/NeurodataWithoutBorders/pynwb/pull/1550)
- Enhanced docs for ``LabMetaData`` to clarify its usage. @oruebel
  [#1546](https://github.com/NeurodataWithoutBorders/pynwb/pull/1546)
- Add testing/mock, which provides mock neurodata objects for testing. @bendichter
  [#1454](https://github.com/NeurodataWithoutBorders/pynwb/pull/1454)

## PyNWB 2.1.0 (July 6, 2022)

### Breaking changes:
- Updated ``TimeIntervals`` to use the new  ``TimeSeriesReferenceVectorData`` type. This does not alter the overall
  structure of ``TimeIntervals`` in a major way aside from changing the value of the ``neurodata_type`` attribute of the
  ``TimeIntervals.timeseries`` column from ``VectorData`` to ``TimeSeriesReferenceVectorData``. This change facilitates
  creating common functionality around ``TimeSeriesReferenceVectorData``. For NWB files with version 2.4.0 and earlier,
  the ``TimeIntervals.timeseries`` column is automatically migrated on read in the ``TimeIntervalsMap``
  object mapper class to use the ``TimeSeriesReferenceVectorData`` container class, so that users are presented a
  consistent API for existing and new files. This change affects all existing ``TimeIntervals`` tables
  e.g., ``NBWFile.epochs``, ``NWBFile.trials``, and ``NWBFile.invalid_times``. While this is technically a breaking
  change, the impact user codes should be minimal as this change primarily adds functionality while the overall
  behavior of the API is largely consistent with existing behavior. @oruebel, @rly (#1390)

### Enhancements and minor changes
- A warning is now raised if `SpatialSeries.data` has more than 3 columns. @bendichter, @rly (#1455, #1480)
- The arguments x, y, z, imp, location, filtering are no longer required in the electrodes table.
  @h-mayorquin, @rly (#1448)
- Added `cell_id` attribute to `IntracellularElectrode`. @bendichter (#1459)
- Added `offset` field to `TimeSeries` and its subtypes. @codycbakerphd (#1424)
- Added support for NWB 2.5.0.
  - Added support for updated ``IndexSeries`` type, new ``order_of_images`` field in ``Images``, and new neurodata_type
    ``ImageReferences``. @rly (#1483)
- Added support for HDMF 3.3.1. This is now the minimum version of HDMF supported. Importantly, HDMF 3.3 introduces
  warnings when the constructor of a class mapped to an HDMF-common data type or an autogenerated data type class
  is passed positional arguments instead of all keyword arguments. @rly (#1484)
- Moved logic that checks the 0th dimension of TimeSeries data equals the length of timestamps to a private method in the
  ``TimeSeries`` class. This is to avoid raising a warning when an ImageSeries is used with external file.
  @weiglszonja (#1486)
- Improved warning text when dimensions are not matched in `TimeSeries`, `ElectricalSeries`, and `RoiResponseSeries`.
  @rly (#1491)

### Documentation and tutorial enhancements:
- Added tutorial on annotating data via ``TimeIntervals``. @oruebel (#1390)
- Added copy button to code blocks. @weiglszonja (#1460)
- Created behavioral tutorial. @weiglszonja (#1464)
- Enhanced display of icephys pandas tutorial by using ``dataframe_image`` to render and display large tables
  as images. @oruebel (#1469)
- Created tutorial about reading and exploring an existing `NWBFile`. @weiglszonja (#1453)
- Added new logo for PyNWB. @oruebel (#1461)
- Minor text fixes. @oruebel @bendichter (#1443, #1462, #1463, #1466, #1472, #1473)

### Bug fixes:
- Fixed input data types to allow only `float` for fields `conversion` and `offset` in definition of
  ``TimeSeries``. @codycbakerphd (#1424)
- Fixed incorrect warning in `RoiResponseSeries.__init__` about mismatch between the second dimension of data and
  the length of rois. @rly (#1491)


## PyNWB 2.0.1 (March 16, 2022)

### Bug fixes:
- Added `environment-ros3.yml` to `MANIFEST.in` for inclusion in source distributions. @rly (#1398)
- Fixed bad error check in ``IntracellularRecordingsTable.add_recording`` when adding ``IZeroClampSeries``.
  @oruebel (#1410)
- Skipped ros3 tests if internet access or the ros3 driver are not available. @oruebel (#1414)
- Fixed CI issues. @rly (#1427)

### Documentation and tutorial enhancements:
- Enhanced ordering of sphinx gallery tutorials to use alphabetic ordering based on tutorial headings. @oruebel (#1399)
- Updated the general tutorial to add documentation about the ``Images`` type. @bendichter (#1353)
- Updated the main index of the documentation to make the documentation easier to navigate. @oruebel (#1402)
- Merged the "NWB File" overview section with the "NWB File Basics" tutorial. @oruebel (#1402)
- Updated and created separated installation instructions for users and developers . @oruebel (#1402)
- Updated the Extracellular electrophysiology tutorial. @bendichter, @weiglszonja (#1391)
- Extended the general tutorial with more data types (e.g., ``Subject``, ``SpatialSeries``, ``Position``).
  @weiglszonja (#1403)
- Improved constructor docstrings for Image types. @weiglszonja (#1418)
- Added documentation for exporting NWB files. @rly (#1417)
- Improved documentation formatting. @bendichter (#1438)
- Minor text fixes. @bendichter (#1437, #1400)

### Minor improvements:
- Improved constructor docstrings for Image types. @weiglszonja (#1418)
- Added checks for data orientation in ``TimeSeries``, ``ElectricalSeries``, and ``RoiResponseSeries`` @bendichter (#1428)
- Added checks for data orientation in ``TimeSeries``, ``ElectricalSeries``, and ``RoiResponseSeries``.
  @bendichter (#1426)
- Enhanced issue template forms on GitHub. @CodyCBakerPHD (#1434)


## PyNWB 2.0.0 (August 13, 2021)

### Breaking changes:
- ``SweepTable`` has been deprecated in favor of the new icephys metadata tables. Use of ``SweepTable``
  is still possible but no longer recommended. @oruebel  (#1349)
- ``TimeSeries.__init__`` now requires the ``data`` argument because the 'data' dataset is required by the schema.
  If a ``TimeSeries`` is read without a value for ``data``, it will be set to a default value. For most
  ``TimeSeries``, this is a 1-dimensional empty array with dtype uint8. For ``ImageSeries`` and
  ``DecompositionSeries``, this is a 3-dimensional empty array with dtype uint8. @rly (#1274)
- ``TimeSeries.__init__`` now requires the ``unit`` argument because the 'unit' attribute is required by the schema.
  If a ``TimeSeries`` is read without a value for ``unit``, it will be set to a default value. For most
  ``TimeSeries``, this is "unknown". For ``IndexSeries``, this is "N/A" according to the NWB 2.4.0 schema. @rly (#1274)

### New features:
- Added new intracellular electrophysiology hierarchical table structure from ndx-icephys-meta to NWB core.
  This includes the new types ``TimeSeriesReferenceVectorData``, ``IntracellularRecordingsTable``,
  ``SimultaneousRecordingsTable``, ``SequentialRecordingsTable``, ``RepetitionsTable`` and
  ``ExperimentalConditionsTable`` as well as corresponding updates to ``NWBFile`` to support interaction
   with the new tables. @oruebel  (#1349)
- Added support for NWB 2.4.0. See [Release Notes](https://nwb-schema.readthedocs.io/en/latest/format_release_notes.html)
  for more details. @oruebel, @rly (#1349)
- Dropped Python 3.6 support, added Python 3.9 support. @rly (#1377)
- Updated requirements to allow compatibility with HDMF 3 and h5py 3. @rly (#1377)
  - When using HDMF 3 and h5py 3, users can now stream NWB files from an S3 bucket.

### Tutorial enhancements:
- Added new tutorial for intracellular electrophysiology to describe the use of the new metadata tables
  and declared the previous tutorial using ``SweepTable`` as deprecated.  @oruebel (#1349)
- Added new tutorial for querying intracellular electrophysiology metadata
  (``docs/gallery/domain/plot_icephys_pandas.py``). @oruebel (#1349, #1383)
- Added thumbnails for tutorials to improve presentation of online docs.  @oruebel (#1349)
- Used `sphinx.ext.extlinks` extension in docs to simplify linking to common targets. @oruebel (#1349)
- Created new section for advanced I/O tutorials and moved parallel I/O tutorial to its own file. @oruebel (#1349)
- Overhauled documentation on extensions. @bendichter, @rly, @oruebel (#1350)
- Updated the optical physiology / Calcium imaging tutorial. @bendichter, @weiglszonja (#1375)
- Added a tutorial on streaming using the ROS3 driver. @rly (#1393)

### Minor new features:
- Added RRID for citing PyNWB to the docs. @oruebel (#1372)
- Updated CI and tests to handle deprecations in libraries. @rly (#1377)
- Added test utilities for icephys (``pynwb.testing.icephys_testutils``) to ease creation of test data
  for tests and tutorials. @oruebel (#1349, #1383)
- Added on-push and nightly tests of streaming using the ROS3 driver. @rly (#1393)
  - These tests make use of a new dandiset for testing the API: https://gui.dandiarchive.org/#/dandiset/000126
- Improve documentation and test for ``CorrectedImageStack``, ``MotionCorrection``. @rly, @bendichter (#1306, #1374)

### Bug fixes:
- Updated behavior of ``make clean`` command for docs to ensure tutorial files are cleaned up.  @oruebel (#1349)
- Enforced electrode ID uniqueness during insertion into table. @CodyCBakerPhD (#1344)
- Fixed integration tests with invalid test data that will be caught by future hdmf validator version.
  @dsleiter, @rly (#1366, #1376)
- Fixed build warnings in docs. @oruebel (#1380)
- Fix intersphinx links in docs for numpy. @oruebel (#1386)
- Previously, the ``data`` argument was required in ``OpticalSeries.__init__`` even though ``external_file`` could
  be provided in place of ``data``. ``OpticalSeries.__init__`` now makes ``data`` optional. However, this has the
  side effect of moving the position of ``data`` to later in the argument list, which may break code that relies
  on positional arguments for ``OpticalSeries.__init__``. @rly (#1274)
- Fixed `setup.py` not being able to import `versioneer` when installing in an embedded Python environment. @ikhramts
  (#1395)
- Removed broken option to validate against a given namespace file and updated associated documentation. @rly (#1397)

## PyNWB 1.5.1 (May 24, 2021)

### Bug fixes:
- Raise minimum version of pandas from 0.23 to 1.0.5 to be compatible with numpy 1.20, and raise minimum version of
  HDMF to use the corresponding change in HDMF. @rly (#1363)
- Update documentation and update structure of requirements files. @rly (#1363)

## PyNWB 1.5.0 (May 17, 2021)

### New features:
- `NWBFile.add_scratch(...)` and `ScratchData.__init__(...)` now accept scalar data in addition to the currently
  accepted types. @rly (#1309)
- Support `pathlib.Path` paths when opening files with `NWBHDF5IO`. @dsleiter (#1314)
- Use HDMF 2.5.1. See the [HDMF release notes](https://github.com/hdmf-dev/hdmf/releases/tag/2.5.1) for details.
- Support `driver='ros3'` in `NWBHDF5IO` for streaming NWB files directly from s3. @bendichter (#1331)
- Update documentation, CI GitHub processes. @oruebel @yarikoptic, @bendichter, @TomDonoghue, @rly
  (#1311, #1336, #1351, #1352, #1345, #1340, #1327)
- Set default `neurodata_type_inc` for `NWBGroupSpec`, `NWBDatasetSpec`. @rly (#1295)
- Block usage of h5py 3+ for now. h5py>=2.9, <3 is supported. (#1355)
- Fix incompatibility issue with downstream github-release tool used to deploy releases to GitHub. @rly (#1245)
- Fix issue with Sphinx gallery. @rly
- Add citation information to documentation and support for duecredit tool. @rly
- Remove use of ColoredTestRunner for more readable verbose test output. @rly
- Add support for nwb-schema 2.3.0. @rly (#1245, #1330)
  - Add optional `waveforms` column to the `Units` table.
  - Add optional `strain` field to `Subject`.
  - Add to `DecompositionSeries` an optional `DynamicTableRegion` called `source_channels`.
  - Add to `ImageSeries` an optional link to `Device`.
  - Add optional `continuity` field to `TimeSeries`.
  - Add optional `filtering` attribute to `ElectricalSeries`.
  - Clarify documentation for electrode impedance and filtering.
  - Set the `stimulus_description` for `IZeroCurrentClamp` to have the fixed value "N/A".
  - See https://nwb-schema.readthedocs.io/en/latest/format_release_notes.html for full schema release notes.
- Add support for HDMF 2.5.5 and upgrade HDMF requirement from 2.1.0 to 2.5.5. @rly @ajtritt
  (#1325, #1355, #1360, #1245, #1287). This includes several relevant features and bug fixes, including:
  - Fix issue where dependencies of included types were not being loaded in namespaces / extensions.
  - Add `HDF5IO.get_namespaces(path=path, file=file)` method which returns a dict of namespace name mapped to the
    namespace version (the largest one if there are multiple) for each namespace cached in the given HDF5 file.
  - Add methods for automatic creation of `MultiContainerInterface` classes.
  - Add ability to specify a custom class for new columns to a `DynamicTable` that are not `VectorData`,
    `DynamicTableRegion`, or `VocabData` using `DynamicTable.__columns__` or `DynamicTable.add_column(...)`.
  - Add support for creating and specifying multi-index columns in a `DynamicTable` using `add_column(...)`.
  - Add capability to add a row to a column after IO.
  - Add method `AbstractContainer.get_fields_conf`.
  - Add functionality for storing external resource references.
  - Add method `hdmf.utils.get_docval_macro` to get a tuple of the current values for a docval_macro, e.g., 'array_data'
    and 'scalar_data'.
  - `DynamicTable` can be automatically generated using `get_class`. Now the HDMF API can read files with extensions
    that contain a DynamicTable without needing to import the extension first.
  - Add `EnumData` type for storing data that comes from a fixed set of values.
  - Add `AlignedDynamicTable` type which defines a DynamicTable that supports storing a collection of subtables.
  - Allow `np.bool_` as a valid `bool` dtype when validating.
  - See https://github.com/hdmf-dev/hdmf/releases for full HDMF release notes.

## PyNWB 1.4.0 (August 12, 2020)

Users can now add/remove containers from a written NWB file and export the modified NWBFile to a new file path.
@rly (#1280)
- See https://pynwb.readthedocs.io/en/stable/tutorials/general/add-remove-containers.html for examples and more
  information.

### Compatibility warnings:
- PyNWB no longer works with HDMF version < 2.1.0. If you have pinned HDMF version < 2 in your package but allow PyNWB
version 1.4.0, please beware that `pip` may install PyNWB version 1.4.0 with an incompatible version of HDMF
(version < 2).
- Use of HDMF 2.1.0 fixes `__getitem__`-based access of `MultiContainerInterface` types, e.g,,
`fluorescence['roi_response_series_name']`, where previously if the `MultiContainerInterface` contained only one item,
then any key could be used within the square brackets to access the contained `Container`, even if the key did not
match the name of the contained `Container`. This update patches this bug such that the key used within the square
brackets *must* match the name of the contained `Container` or else an error will be raised.

### Internal improvements:
- Update requirements to use HDMF 2.1.0. @rly (#1256)
- Start FAQ section in documentation. @rly (#1249)
- Improve deprecation warnings. @rly (#1261)
- Update CI to test Python 3.8, update requirements. @rly (#1267, #1275)
- Make use of `MultiContainerInterface` and `LabelledDict` that have been moved to HDMF. @bendichter @rly (#1260)

### Bug fixes:
- For `ImageSeries`, add check if `external_file` is provided without `starting_frame` in `__init__`. @rly (#1264)
- Improve docstrings for `TimeSeries.data` and for the electrode table. @rly (#1271, #1272)
- Fix Azure Pipelines configuration. @rly (#1281)

## PyNWB 1.3.3 (June 26, 2020)

### Internal improvements:
- Update requirements to use HDMF 1.6.4. @rly (#1256)

### Bug fixes:
- Fix writing optional args to electrodes table. @rly (#1246)
- Fix missing method UnitsMap.get_nwb_file. @rly (#1227)

## PyNWB 1.3.2 (June 1, 2020)

### Bug fixes:
- Add support for nwb-schema 2.2.5. @rly (#1243)
  - This schema version fixes incorrect dims and shape for `ImagingPlane.origin_coords` and `ImagingPlane.grid_spacing`,
   and fixes incorrect dims for `TwoPhotonSeries.field_of_view`.

## PyNWB 1.3.1 (May 28, 2020)

### Bug fixes:
- Fix bugged `Device` constructor. @rly (#1209)
- Fix link to code of conduct page in docs. @rly (#1229)
- Fix docs for `get_type_map`. @oruebel (#1233)
- Pass file object to parent when loading namespaces. @NileGraddis (#1242)

### Internal improvements:
- Update CI to use supported MacOS version. @rly (#1211)
- Clean up tests to remove conversion warnings and use keyword args. @rly (#1202)
- Fix flake8 errors. @rly (#1235)
- Add changelog. @rly (#1215)
- Update release process with notes about coordinating with nwb-schema. @rly (#1214)
- Inform which unit value is actually overwritten. @yarikoptic (#1219)
- Do not print out logging.DEBUG statements to stdout for test.py. @rly (#1240)
- Add support for nwb-schema 2.2.4. @rly (#1213)
  - Make `ImagingPlane.imaging_rate` optional. This moves the `imaging_rate` argument down the list of constructor arguments for `ImagingPlane.__init__`. This will break existing code that calls the constructor of `ImagingPlane` with at least 6 positional arguments, such that one positional argument matches `imaging_rate`.

## PyNWB 1.3.0 (Mar. 4, 2020)

### New features:
- Add support for nwb-schema 2.2.2. @rly (#1146)
  - This is a large change. See the PR and [schema release notes](http://nwb-schema.readthedocs.io/en/latest/format_release_notes.html#march-2-2020) for more information.
- Validate against most specific namespace. @t-b, @rly (#1094)
- Replace 'ic_electrode' with 'icephys_electrode' in `NWBFile`. @oruebel (#1200)
- Integrate minor enhancements and bug fixes introduced in HDMF 1.6.0 and 1.6.1, including improved handling of namespaces that lack a version key,

### Internal improvements:
- Add nightly testing of validation CLI. @t-b, @rly (#1164, #1195, #1197)
- Treat ipython notebooks as binary in git. @t-b (#1168)
- Use proper file removal in tests. @t-b (#1165)
- Use hdmf-docutils instead of nwb-docutils for documentation. @jcfr (#1176)
- Run minimum requirements testing n Python 3.6. @rly (#1194)

### Bug fixes:
- Fix API documentation. @bendichter (#1159)
- Fix unit testing output. @rly (#1158)
- Fix copying files with Subject. @rly (#1171)
- Add "unit" attribute back as an optional attribute in icephys classes. @rly (#1188)
- Fix reported development status in `setup.py`. @rly (#1201)

## PyNWB 1.2.1 (Jan. 22, 2020)

### Bug fixes:
- Fix ReadTheDocs build. @rly (#1155)
- Update manifest to fix conda build. @rly (#1156)

## PyNWB 1.2.0 (Jan. 21, 2020)

### Minor enhancements:
- Add new logo to docs. @rly (#1096)
- Add warning when referencing electrode table before it exists. @ajtritt (#1098)
- Refactor internal calls to docval. @rly (#1104)
- Enhance icephys example and documentation. @t-b (#1081)
- Add multi index and time bounds to get_unit_spikes. @bendichter (#1001)
- Improve ophys docstrings. @bendichter (#1126)
- Improve icephys docstrings for gain. @bendichter (#1129)
- Update legal information. @rly (#1131)
- Add support for device description and manufacturer. @rly (#1135)
- Update dependencies and remove explicit six, unittest2 dependency. @rly (#1136, #1138, #1142, #1137, #1154)
- Add object ID tutorial. @rly (#1140)
- Update CI. @rly (#1141)
- Catch critical warnings and throw errors in unit tests. @rly (#1112)
- Create and use testing module, remove builder tests, clean up test code. @rly (#1117)
- Add and test minimum requirements for PyNWB. @rly (#1148)
- Improve docs for get_class. @bendichter (#1149)

### Bug fixes:
- Fix versioneer reporting version. @rly (#1100)
- Fix `DynamicTable` import after move to hdmf.common. @bendichter (#1103)
- Fix handling of unmapped attributes. @rly (#1105)
- Update tests and documentation to reflect new selection behavior of `DynamicTable`. @oruebel (#1106)
- Fix reference images not being mapped in PlaneSegmentation. @rly (#1109)
- Fix legacy import of `ObjectMapper`. @rly (#1124)
- Fix extensions documentation typo: 'str' -> 'text'. @bendichter (#1132)
- Revert "PatchClampSeries: Force sweep_number to uint64". @t-b (#1123)
- Fix sphinx code to use latest sphinx. @rly (#1139)

## PyNWB 1.1.2 (Oct. 15, 2019)

### Minor features:
- Use latest HDMF 1.3.3. #1093 (@rly)
- Expose HDMF export_spec utility function for use by extensions. #1092 (@rly)

### Bug fixes:
- Fix bug in writing SpikeEventSeries data or timestamps datasets with a DataChunkIterator. #1089 (@bendichter)

## PyNWB 1.1.1 (Oct. 7, 2019)

PyNWB 1.1.0 does not work with HDMF>=1.3. This release will work with HDMF>=1.3.2.

### Minor improvements:
- Support newly added channel-specific conversion factor for ElectricalSeries #1072 (@bendichter)
- Move generic types out of PyNWB into hdmf-common. #1061 (@ajtritt)
- Update documentation to reflect the above changes. #1078 (@rly)
- Add new case to the iterative write tutorial. #1029 (@oruebel)
- Improve CI. #1079 (@rly)
- Pin the current latest version of HDMF to requirements for setup.py. #1083 (@rly)

## PyNWB 1.1.0 (Sep. 17, 2019)

### New features:
- Add object ID to all neurodata types #991 (@ajtritt, @rly)
- Add NWBFile shallow copy method #994 (@ajtritt, @rly)
- Drop official Python 2.7 support #1028 (@rly)
- Add scratch space #1027 #1038 (@ajtritt, @rly)
- Support multiple experimenters #988 #1035 (@ajtritt, @rly)
- Support multiple related publications #1047 (@rly)
- Update schema to 2.1.0 (see release notes in https://nwb-schema.readthedocs.io/en/latest/format_release_notes.html) (@rly, @bendichter, @ajtritt, @oruebel, @t-b)

### Minor enhancements:
- Add iterative write check for TimeSeries timestamps #1012 (@bendichter, @oruebel)
- Add functions to convert between pixel mask and image mask for ophys data #766 (@mamelara)
- Add cortical surface extension example #1040 (@bendichter)
- Match API with schema defaults #1033 (@rly)
- Core schema is now a git submodule #1045 (@ajtritt)
- Implement better support for floating point data for Python 3.5 on Windows #1043 (@rly)
- Enhance iterative write tutorial #1029 (@oruebel)
- Allow empty data in DynamicTable with non-empty VectorIndex #887 (@ajtritt)
- Allow OpticalSeries constructor argument 'field_of_view' to be H5Dataset #1063 (@bendichter)
- Clarify documentation for deprecated ImageSeries constructor arg 'bits_per_pixel' #1065 (@rly)
- Adjust code to explicitly map properties after changes made in HDMF 1.2 #1048 #1069 (@rly)
- Improvements to CI, documentation, and GitHub repo structure #1055 (@rly)

## PyNWB 1.0.3 (Jul. 18, 2019)

### New/modified functionality:
- Add MPI functionality to NWBHDF5IO (@bendichter)
- Add option to exclude columns from DynamicTable.to_dataframe() (@NileGraddis)
- Remove ability to add DecompositionSeries to LFP (@bendichter)
- Remove num_samples from TimeSeries (@NileGraddis)
- Automatically detect ragged arrays in from_dataframe (@bendichter)
- Cache the spec by default on write (@rly)
- Improve printing of NWB objects (@rly)
- Change ProcessingModule.add_data_interface() to .add(), ProcessingModule.get_data_interface() to .get(), NWBFile.modules to NWBFile.processing (@bendichter)
- Remove unused SpecFile type (@oruebel)
- Add ability to validate files against the cached spec (@t-b)
- Make CurrentClampSeries/VoltageClampSeries parameters optional (@t-b)
- Update documentation (@t-b, @rly)
- Update copyright/license
- Improve tests and CI
- Update requirements
- See also HDMF changes https://github.com/hdmf-dev/hdmf/releases/tag/1.0.4

### Bug fixes:
- Fix dynamictableregion iteration failure after roundtrip (@NileGraddis)
- Fix from_dataframe for children of DynamicTable (@bendichter)
- Fix for modular (cross-file) storage of timeseries timestamps (@NileGraddis)
- Fix bug on loading lists of strings from hdmf 1.0.4 (@rly)
- Fix IO for intervals (@bendichter)
- Fix round trip for Subject.date_of_birth (@bendichter)

### Schema changes:
- DecompositionSeries "source_timeseries" link is no longer required (@bendichter)
- Reorder keys (@rly)
- Remove NWBFile "specifications" group (@oruebel)
- CorrectedImageStack and ImagingRetinotopy inherits from NWBDataInterface instead of NWBContainer (@rly)
- Fix typo in unit of resistance_comp_prediction/correction (@t-b)
- Add option for third dimension for Units "waveforms" dataset to represent different electrodes (@bendichter)
- Update NWBFile.nwb_version to 2.0.2

## PyNWB 1.0.2 (Apr. 19, 2019)
