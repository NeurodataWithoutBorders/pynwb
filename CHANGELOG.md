# PyNWB Changelog

## PyNWB 4.2.0 (September 2, 2026)

### Changed
- The array-valued fields `TimeSeries.control` and `control_description`, `ImageSeries.dimension` and `starting_frame`, `TwoPhotonSeries.field_of_view`, `AbstractFeatureSeries.features` and `feature_units`, `Clustering.peak_over_rms`, and `ClusterWaveforms.waveform_mean` and `waveform_sd` accept zarr arrays. They no longer accept non-array iterables such as `str`, `set`, `range`, and generators. @rly [#2235](https://github.com/NeurodataWithoutBorders/pynwb/pull/2235)
- `TimeSeries.get_timestamps` raises a `ValueError` when timestamps must be generated but the number of samples in the data cannot be determined. @rly [#2235](https://github.com/NeurodataWithoutBorders/pynwb/pull/2235)
- Added support for NWB Schema 2.11.0
  - The `unit` attribute of `Units.waveform_mean`, `Units.waveform_sd`, and `Units.waveforms` now has a default value of `"volts"` instead of a fixed value of `"volts"`.
  - `Units.waveform_mean`, `Units.waveform_sd`, and `Units.waveforms` have a new optional `time_before_peak_in_ms` attribute, exposed as the `waveform_time_before_peak_in_ms` argument and field of `Units`. It holds the time, in milliseconds, from the start of each waveform to the spike peak, i.e., the alignment point used during spike sorting. @rly [#2237](https://github.com/NeurodataWithoutBorders/pynwb/pull/2237)
  - Incorporates HDMF Common Schema 1.10.0, which changes `MeaningsTable.target` from a link to an object-reference attribute. @rly [#2244](https://github.com/NeurodataWithoutBorders/pynwb/pull/2244)
- Raised the minimum HDMF requirement to 6.2.0, which bundles the HDMF Common Schema 1.10.0 required by NWB Schema 2.11.0. @rly [#2244](https://github.com/NeurodataWithoutBorders/pynwb/pull/2244)

### Added
- Added a section to the "How to Configure Term Validations" tutorial showing how to populate a `HERD` from the fields that a loaded type configuration wraps with a `TermSetWrapper`. @oruebel [#2251](https://github.com/NeurodataWithoutBorders/pynwb/pull/2251)
- Added `model` and `serial_number` parameters to `mock_Device`. Passing a `DeviceModel` as `model` together with an `nwbfile` also places that `DeviceModel` in the `NWBFile`, so the link resolves when the file is written. @rly [#2238](https://github.com/NeurodataWithoutBorders/pynwb/pull/2238)

### Fixed
- Fixed `FeatureExtraction.times` and `Clustering.peak_over_rms` being copied into a Python list on construction, which was slow for data read from a file. @cboulay [#2253](https://github.com/NeurodataWithoutBorders/pynwb/pull/2253)
- Fixed `NWBFile.objects` becoming stale after containers were added to or removed from the file, including mutations made through nested containers. The object mapping is now rebuilt whenever it is accessed. @AtomicGlance [#2242](https://github.com/NeurodataWithoutBorders/pynwb/issues/2242)
- Fixed `ElectricalSeries.__init__`, `TimeSeries.get_timestamps`, and `TimeSeries.num_samples` failing on data backed by a zarr array. @rly [#2235](https://github.com/NeurodataWithoutBorders/pynwb/pull/2235)
- Fixed `TimeSeries.num_samples` returning `None` when the data or timestamps are backed by a `DataChunkIterator` that wraps an array. @rly [#2235](https://github.com/NeurodataWithoutBorders/pynwb/pull/2235)
- Fixed `Units.waveform_unit` having no effect on the written file. It is now written to the `unit` attribute of the `waveform_mean`, `waveform_sd`, and `waveforms` columns, and still defaults to `"volts"`. Reading a file whose waveform columns carry different `unit` or `sampling_rate` attributes now warns, since `Units` keeps a single value for each. @rly [#2237](https://github.com/NeurodataWithoutBorders/pynwb/pull/2237)
- Fixed `mock_DeviceModel` defaulting `manufacturer` to `None`. The mock now defaults it to `"manufacturer"`. @HugoFara [#2232](https://github.com/NeurodataWithoutBorders/pynwb/pull/2232)
- Fixed reading a file whose dates carry a sub-minute UTC offset (e.g. `1900-10-01T00:00:00-05:50:36`). @h-mayorquin [#2230](https://github.com/NeurodataWithoutBorders/pynwb/pull/2230)
- Fixed wide pandas DataFrames in the tutorials spilling out of the content column and into the right margin. @bendichter [#2236](https://github.com/NeurodataWithoutBorders/pynwb/pull/2236)
- Fixed the experimenter check in the "Annotating Multiple Streamed NWB Files with a Single HERD" example testing for `"Chen, Tsai-Wen"` while dandiset 000015 stores `"Tsai-Wen Chen"`, so the ORCID reference was never added. The example also streams the first 5 assets of the dandiset rather than all 210. @rly [#2246](https://github.com/NeurodataWithoutBorders/pynwb/pull/2246)
- Fixed `set_data_io` being silently ignored on `NWBData` subclasses (`GrayscaleImage`, `RGBImage`, `RGBAImage`, `ExternalImage`, `ImageReferences`, and `ScratchData`), so requested chunking and compression were dropped. @h-mayorquin [#2233](https://github.com/NeurodataWithoutBorders/pynwb/pull/2233)
- Fixed `ImageSeries` (and its subclasses) writing a derived `num_samples` dataset that the user never set. @adityasingh2400 [#2239](https://github.com/NeurodataWithoutBorders/pynwb/pull/2239)
- Fixed `OpticalSeries`, `OnePhotonSeries`, and `TwoPhotonSeries` not accepting `num_samples`, which made them impossible to construct with `format="external"` and `rate`. @rly [#2248](https://github.com/NeurodataWithoutBorders/pynwb/pull/2248)
- Fixed `ImageSeries.num_samples` returning `None` instead of `len(timestamps)` for an external-file series timed with `timestamps`, which also made `get_starting_time` and `get_duration` return `None`. @rly [#2250](https://github.com/NeurodataWithoutBorders/pynwb/pull/2250)
- Fixed `TimeSeriesReference.timestamps` returning incorrect times for a `TimeSeries` that has `starting_time` and `rate` instead of `timestamps`. @h-mayorquin @rly [#2245](https://github.com/NeurodataWithoutBorders/pynwb/pull/2245)

## PyNWB 4.1.0 (July 23, 2026)

### Changed
- Updated `ObjectMapper` `constructor_arg` and `object_attr` override functions to return the `hdmf.build.ObjectMapper.NO_OVERRIDE` sentinel instead of `None` to signal "no override". HDMF 6.2.0 deprecates returning `None` from an override function to signal "no override" (in HDMF 8.0 a `None` return will set the constructor argument or attribute to `None`, dropping data), and emits a `DeprecationWarning` when it happens (see [hdmf-dev/hdmf#1167](https://github.com/hdmf-dev/hdmf/pull/1167)). PyNWB resolves the sentinel via `getattr`, so it degrades to `None` on HDMF < 6.2.0 and keeps working with the existing `hdmf>=6.1.0` requirement without bumping the minimum version. @rly [#2224](https://github.com/NeurodataWithoutBorders/pynwb/pull/2224)
- Lifted the `<1.11` cap on the `linkml` and `linkml-runtime` termset extras and bumped the `dandi` docs dependency to `>=0.76.5`. dandi 0.76.5 lifts its `click<8.2` bound ([dandi/dandi-cli#1883](https://github.com/dandi/dandi-cli/pull/1883)), which had conflicted with the `click>=8.2` requirement of linkml 1.11. @rly [#2217](https://github.com/NeurodataWithoutBorders/pynwb/pull/2217)

### Added
- Added remote-read support to `pynwb.read_nwb`. The function now accepts remote URLs (`s3://`, `gs://`, `abfs://`, `https://`, etc.) and dispatches to the right backend based on the URL: `.zarr` suffixes (and DANDI Zarr assets under `/zarr/`) are read with `NWBZarrIO`, everything else with `NWBHDF5IO`. Remote files are opened through `fsspec`, which now uses the URL's actual scheme instead of the previous hardcoded `fsspec.filesystem("http")` that mishandled non-HTTP schemes. @h-mayorquin [#2190](https://github.com/NeurodataWithoutBorders/pynwb/pull/2190)

### Fixed
- Fixed `pynwb.read_nwb` leaking the `fsspec` file handle when reading a remote HDF5 file. `NWBHDF5IO` now closes the `fsspec` handle when it is closed. @rly [#2226](https://github.com/NeurodataWithoutBorders/pynwb/pull/2226)
- Worked around a deadlock in the HDF5 2.1 ROS3 driver that hung the Windows ROS3 CI jobs after the tests passed. @rly [#2228](https://github.com/NeurodataWithoutBorders/pynwb/issues/2228)
- Fixed `mock_electrodes` (and `mock_ElectricalSeries`) sizing the auto-created `ElectrodesTable` to a fixed 5 rows while the `DynamicTableRegion` followed `n_electrodes`, which raised an `IndexError` under HDMF 4.x+ for any data with more than 5 channels. The table is now sized to `n_electrodes`. @h-mayorquin [#2214](https://github.com/NeurodataWithoutBorders/pynwb/pull/2214)
- Fixed `read_nwb` and `_get_backend` reporting a nonexistent path as an unrecognized backend (and, without hdmf-zarr installed, suggesting `pip install hdmf-zarr`). A missing file now raises a `FileNotFoundError`. @rly [#2222](https://github.com/NeurodataWithoutBorders/pynwb/pull/2222)
- Fixed the `Deploy pre-release from dev` CI job, which failed with a `404` from the GitHub API because `scikit-ci-addons` resolved the `latest` tag to one of two duplicate draft releases it had itself created. Both release paths now use the `gh` CLI. @rly [#2225](https://github.com/NeurodataWithoutBorders/pynwb/pull/2225)


## PyNWB 4.0.0 (June 29, 2026)

### Removed
- Removed functionality that was deprecated with a "will be removed in PyNWB 4.0" notice. @rly [#2210](https://github.com/NeurodataWithoutBorders/pynwb/issues/2210)
  - `ProcessingModule.add_container`, `get_container`, `add_data_interface`, and `get_data_interface`. Use `add` and `get` instead.
  - The `extensions` argument of `get_type_map`, `get_manager`, and `NWBHDF5IO`. Load cached namespaces from the file or pass a prebuilt `manager` instead.
  - The `notes` argument and `notes` property of `ScratchData`. Use `description` instead.
  - The `notes` and `table_description` arguments of `NWBFile.add_scratch`. Use `description` instead.
  - The `ic_electrodes` argument of `NWBFile`. Use `icephys_electrodes` instead.
  - The `paths` argument of `pynwb.validate`. Use `path` and call `validate` once per file instead.
- Made `NWBFile.icephys_filtering` read-only. Use `IntracellularElectrode.filtering` instead. The legacy `/general/intracellular_ephys/filtering` value is still read from older files. @rly [#2210](https://github.com/NeurodataWithoutBorders/pynwb/issues/2210)

### Changed
- Consolidated dependency declarations into `pyproject.toml` and removed the `requirements.txt`, `requirements-dev.txt`, `requirements-opt.txt`, `requirements-doc.txt`, and `requirements-min.txt` files. Added user-installable `zarr` and `termset` optional-dependency extras (e.g. `pip install pynwb[zarr]`), and declared development dependencies as PEP 735 `[dependency-groups]` (`test`, `stream`, `docs`). `tox` now installs dependencies via extras and dependency groups, with minimum-version testing using `uv pip install --resolution lowest-direct`. Install development dependencies with `pip install --group test --group docs -e ".[zarr,termset]"`. @rly [#2205](https://github.com/NeurodataWithoutBorders/pynwb/pull/2205)
- Deprecated `NWBGroupSpec.add_group` and `NWBGroupSpec.add_dataset`. Use `NWBGroupSpec.set_group`, `NWBGroupSpec.set_dataset`, or pass the group or dataset to the `NWBGroupSpec` constructor. @rly [#2138](https://github.com/NeurodataWithoutBorders/pynwb/issues/2138)
- Fixed `TimeSeries.get_timestamps()` to handle numpy array timestamps when they are set. @pauladkisson [#2181](https://github.com/NeurodataWithoutBorders/pynwb/pull/2181)
- Fixed `Units.waveform_rate` and `Units.waveform_unit` to also map to the `sampling_rate` and `unit` attributes of the `waveforms` column on write and read, so waveform sampling metadata round-trips for `Units` tables that contain only `waveforms` (without `waveform_mean` or `waveform_sd`). @ehennestad [#2183](https://github.com/NeurodataWithoutBorders/pynwb/pull/2183)
- Added Python 3.14 support. @bendichter, @rly [#2168](https://github.com/NeurodataWithoutBorders/pynwb/pull/2168)
- Bumped the minimum HDMF dependency to >=6.1.0 for pandas 3.0 compatibility. See the [HDMF changelog](https://hdmf.readthedocs.io/en/stable/CHANGELOG.html) for the full list of changes in HDMF 6.1.0. @rly [#2171](https://github.com/NeurodataWithoutBorders/pynwb/issues/2171), [#2208](https://github.com/NeurodataWithoutBorders/pynwb/pull/2208)
- Deprecated Python 3.9 support. (EOL was Oct 31, 2025) @bendichter [#2141](https://github.com/NeurodataWithoutBorders/pynwb/pull/2141)
- Deprecated `BehavioralEvents` and `AnnotationSeries` in favor of using an `EventsTable` in `NWBFile.events`. Creating a new instance of either type now emits a `UserWarning`; reading existing files containing these types continues to work without warnings. @rly [#2156](https://github.com/NeurodataWithoutBorders/pynwb/pull/2156)

### Added
- Added optional `source_description` attribute to `EventsTable` for a short free-text label of where events originated (e.g., `"Acquisition system"`, `"Manual video review"`). Added `NWBFile.merge_events_tables()` to merge a list of `EventsTable` objects into a single DataFrame sorted by timestamp with a `source_events_table` column. Added `NWBFile.get_all_events()` to merge all tables in `NWBFile.events`. @rly [#2192](https://github.com/NeurodataWithoutBorders/pynwb/pull/2192)
- Added support for NWB Schema 2.10.0 ([NWBEP001](https://nwb-schema.readthedocs.io/)), which introduces the `EventsTable`, `TimestampVectorData`, and `DurationVectorData` neurodata types and a new `events` group on `NWBFile` for storing `EventsTable` instances. Use `NWBFile.add_events_table()` to add an `EventsTable` and `NWBFile.get_events_table()` to retrieve one. NWB Schema 2.10.0 also incorporates hdmf-common-schema 1.9.0, which adds the `MeaningsTable` neurodata type (re-exported via `hdmf.common`) and support for attaching one or more `MeaningsTable` instances to a `DynamicTable` to document the meanings of values in a column. See the [NWB Schema release notes](https://nwb-schema.readthedocs.io/en/latest/format_release_notes.html) and the [hdmf-common-schema release notes](https://hdmf-common-schema.readthedocs.io/en/latest/format_release_notes.html) for the full list of changes. @rly [#2156](https://github.com/NeurodataWithoutBorders/pynwb/pull/2156)
- Added support for HERD (HDMF External Resources Data Structure) as the `external_resources` field on `NWBFile`, enabling users to associate external resource annotations (e.g., ontology term mappings) with their NWB files. `link_resources` is inherited from `HERDManager` in hdmf. @mavaylon1, @rly [#2111](https://github.com/NeurodataWithoutBorders/pynwb/pull/2111)
- `NWBFile.get_external_resources()` returns the file's existing HERD or creates and attaches a new empty one if the file does not have external resources yet, mirroring `get_intracellular_recordings()`. @rly [#2200](https://github.com/NeurodataWithoutBorders/pynwb/pull/2200)
- Added `get_starting_time()` and `get_duration()` methods to `TimeSeries` to get the starting time and duration of the time series. @h-mayorquin [#2146](https://github.com/NeurodataWithoutBorders/pynwb/pull/2146)
- Added `get_starting_time()` and `get_duration()` methods to `TimeIntervals` to get the earliest start time and total duration (span from earliest start to latest stop) of all intervals. @h-mayorquin [#2146](https://github.com/NeurodataWithoutBorders/pynwb/pull/2146)
- Added `get_starting_time()` and `get_duration()` methods to `Units` to get the earliest spike time and total duration (span from earliest to latest spike) across all units. @h-mayorquin [#2164](https://github.com/NeurodataWithoutBorders/pynwb/pull/2164)
- Added pandas 3.0 compatibility. `NWBFile.add_scratch` now accepts a `pandas.Series` or a pandas `ExtensionArray` (e.g., `StringArray` and `ArrowStringArray`) as `data`, which is normalized to numpy when constructing `ScratchData`. This relies on the coercion added in [hdmf-dev/hdmf#1469](https://github.com/hdmf-dev/hdmf/pull/1469) (HDMF 6.1.0), which also makes the inherited PyArrow-backed string columns from pandas 3 DataFrames work across `TimeSeries` subclasses, `add_unit`, `add_electrode`, and `DynamicTable.from_dataframe`. The `pandas<3` cap has been lifted. @rly [#2208](https://github.com/NeurodataWithoutBorders/pynwb/pull/2208)

### Fixed
- Fixed ROS3 streaming and added an `aws_region` argument to `validate` so the AWS region can be passed through when validating a file opened with the `ros3` driver. HDF5 2.1.0 (h5py 3.16.0) requires the AWS region to be specified when opening an S3 URL with the `ros3` driver, so the ROS3 tests and the streaming tutorial now pass `aws_region="us-east-2"` (the region of the DANDI Archive S3 bucket). @rly [#2201](https://github.com/NeurodataWithoutBorders/pynwb/pull/2201)
- Fixed reading legacy files where `Device.model` is a string containing `/` or `:` (e.g., `"MFC_200/250-0.66_40mm"`), which previously raised a `ValueError`. The string is now remapped to a read-only `DeviceModel` that preserves the original name, with a warning explaining that the file cannot be written or exported until a `DeviceModel` with a valid name is created. Writing or exporting such a `DeviceModel` raises a clear error instead of silently corrupting the file. @rly [#2186](https://github.com/NeurodataWithoutBorders/pynwb/pull/2186)
- Fixed invalid CSS properties in documentation assistant toggle that prevented proper positioning on displays ≥1400px wide. @rly [#2151](https://github.com/NeurodataWithoutBorders/pynwb/pull/2151)

### Documentation and tutorial enhancements
- Added a tutorial on using HERD to annotate an NWB file with external resources and store it at `/general/external_resources`, plus a companion example showing how to annotate multiple NWB files streamed from a DANDI dandiset with a single HERD. @rly, @mavaylon1 [#2200](https://github.com/NeurodataWithoutBorders/pynwb/pull/2200)
- Added `pandas.ExtensionArray` to `nitpick_ignore` so the Sphinx build does not fail on the unresolved cross-reference that HDMF's `array_data` docval macro renders for every type that accepts array data. @rly [#2209](https://github.com/NeurodataWithoutBorders/pynwb/pull/2209)
- Added `app.readthedocs.org/projects/pynwb/*` to `linkcheck_ignore` to stop the Sphinx linkcheck CI job from intermittently failing when GitHub Actions runners get throttled by readthedocs. @h-mayorquin [#2191](https://github.com/NeurodataWithoutBorders/pynwb/pull/2191)
- Added documentation for `ExternalImage` to the images tutorial. @h-mayorquin [#2159](https://github.com/NeurodataWithoutBorders/pynwb/pull/2159)
- Fixed broken and redirecting links in documentation. @bendichter [#2165](https://github.com/NeurodataWithoutBorders/pynwb/pull/2165)
- Added `EventsTable` examples to the NWB file basics and behavior tutorials. @rly [#2156](https://github.com/NeurodataWithoutBorders/pynwb/pull/2156)
- Added example of setting `Units.resolution` in the ecephys tutorial. @h-mayorquin [#2174](https://github.com/NeurodataWithoutBorders/pynwb/pull/2174)


## PyNWB 3.1.3 (December 9, 2025)

### Added
- Added 'target_tables' kwarg to DynamicTable subclasses to allow classes that extend DynamicTable subclasses to specify the mapping of DynamicTableRegion columns to the target tables. @rly, @stephprince [#2096](https://github.com/NeurodataWithoutBorders/pynwb/issues/2096)

### Fixed
- Fixed incorrect warning for path not ending in `.nwb` when no path argument was provided. @t-b [#2130](https://github.com/NeurodataWithoutBorders/pynwb/pull/2130)
- Fixed inability to read files created with extensions that had schema conflicts with the DeviceModel type introduced in NWB Schema 2.9.0. @stephprince [#2132](https://github.com/NeurodataWithoutBorders/pynwb/pull/2132)
- Fixed issue with setting `neurodata_type_inc` when reading NWB files with cached schema versions less than 2.2.0. @rly [#2135](https://github.com/NeurodataWithoutBorders/pynwb/pull/2135)
- Fixed import structure test. @rly [#2136](https://github.com/NeurodataWithoutBorders/pynwb/pull/2136)

### Changed
- Changed UI of documentation assistant to be an accordion that is always visible. @bendichter [#2124](https://github.com/NeurodataWithoutBorders/pynwb/pull/2124)
- Updated minimum HDMF version to 4.1.2 and updated tests accordingly. @rly [#2144](https://github.com/NeurodataWithoutBorders/pynwb/pull/2144)


## PyNWB 3.1.2 (August 13, 2025)

### Fixed
- Fixed parsing of the nwb_version attribute which followed the previous suggestion to have a `NWB-` prefix.
  @t-b [#2118](https://github.com/NeurodataWithoutBorders/pynwb/pull/2118)
- Fixed a performance regression introduced in pynwb 2.8.0 that affected reading NWB files with a large
  number of objects or fields of objects. @rly [#2121](https://github.com/NeurodataWithoutBorders/pynwb/pull/2121)
- Fixed `load_type_config`, `unload_type_config`, and `get_loaded_type_config` acting on a copy of the global type map
  instead of the global type map itself. @rly [#2121](https://github.com/NeurodataWithoutBorders/pynwb/pull/2121)

### Changed
- Added an argument `copy` to `get_type_map` to control whether a copy of the type map is returned or not.
  If `copy=False`, the returned type map will be a direct reference to the global type map. @rly
  [#2121](https://github.com/NeurodataWithoutBorders/pynwb/pull/2121)
- Deprecated calling `get_type_map` with the `extensions` argument. Call `load_namespaces` on the returned `TypeMap`
  instead. @rly [#2121](https://github.com/NeurodataWithoutBorders/pynwb/pull/2121)

## PyNWB 3.1.1 (July 22, 2025)

### Bug fixes
- Fixed reading and exporting of files written with NWB Schema < 2.9.0 that contained a reference to the electrodes table. @rly [#2112](https://github.com/NeurodataWithoutBorders/pynwb/pull/2112)
- Updated tests to skip streaming tests gracefully if offline. @rly [#2113](https://github.com/NeurodataWithoutBorders/pynwb/pull/2113)
- Added check in `PlaneSegmentation` constructor for required columns. @rly [#2102](https://github.com/NeurodataWithoutBorders/pynwb/pull/2102)


## PyNWB 3.1.0 (July 8, 2025)

### Breaking changes
- Removed unused functions `prepend_string` and `_not_parent` in `core.py`, `_not_parent` in `file.py`, and `NWBBaseTypeMapper.get_nwb_file` in `io/core.py` @oruebel [#2036](https://github.com/NeurodataWithoutBorders/pynwb/pull/2036)

### Enhancements and minor changes
- Added support for NWB Schema 2.9.0.
  - Added `BaseImage` and `ExternalImage` as new neurodata types. The first so both `Image` and `ExternalImage` can inherit from it. The second to store external images. @rly [#2079](https://github.com/NeurodataWithoutBorders/pynwb/pull/2079)
  - Added new `ElectrodesTable` neurodata type. @mavaylon1 [#1890](https://github.com/NeurodataWithoutBorders/pynwb/pull/1890)
  - Formally defined and renamed `ElectrodeTable` as the `ElectrodesTable` neurodata type. @mavaylon1 [#1890](https://github.com/NeurodataWithoutBorders/pynwb/pull/1890)
  - Formally defined bands within `DecompositionSeries` as the neurodatatype `FrequencyBandsTable`. @mavaylon1 @rly [#2063](https://github.com/NeurodataWithoutBorders/pynwb/pull/2063)
  - Added new `DeviceModel` neurodata type to store device model information. @rly [#2088](https://github.com/NeurodataWithoutBorders/pynwb/pull/2088)
  - Deprecated `Device.model_name`, `Device.model_number`, and `Device.manufacturer` fields in favor of `DeviceModel`. @rly [#2088](https://github.com/NeurodataWithoutBorders/pynwb/pull/2088)
  - Added support for 2D `EventDetection.source_index` to indicate [time_index, channel_index]. @stephprince [#2091](https://github.com/NeurodataWithoutBorders/pynwb/pull/2091)
  - Made `EventDetection.times` optional. @stephprince [#2091](https://github.com/NeurodataWithoutBorders/pynwb/pull/2091)
  - Deprecated `EventDetection.times`. @stephprince [#2101](https://github.com/NeurodataWithoutBorders/pynwb/pull/2101)
- Automatically add timezone information to timestamps reference time if no timezone information is specified. @stephprince [#2056](https://github.com/NeurodataWithoutBorders/pynwb/pull/2056)
- Added option to disable typemap caching and updated type map cache location. @stephprince [#2057](https://github.com/NeurodataWithoutBorders/pynwb/pull/2057)
- Added dictionary-like operations directly on `ProcessingModule` objects (e.g., `len(processing_module)`). @bendichter [#2020](https://github.com/NeurodataWithoutBorders/pynwb/pull/2020)
- When an external file is detected when initializing an ImageSeries and no format is provided, automatically set format to "external" instead of raising an error. @stephprince [#2060](https://github.com/NeurodataWithoutBorders/pynwb/pull/2060)
- Added mask_type option to `mock_PlaneSegmentation`. @pauladkisson [#2067](https://github.com/NeurodataWithoutBorders/pynwb/pull/2067)
- Improved the documentation of the `spike_times` in the Units table methods @h-mayorquin [#2085](https://github.com/NeurodataWithoutBorders/pynwb/pull/2085)
- Removed core namespace warning unless cached version is newer. @stephprince [#2077](https://github.com/NeurodataWithoutBorders/pynwb/pull/2077)
- Bumped minimum HDMF version to 4.1.0. @stephprince [#2077](https://github.com/NeurodataWithoutBorders/pynwb/pull/2077)

### Bug fixes
- Fixed `add_data_interface` functionality that was mistakenly removed in PyNWB 3.0. @stephprince [#2052](https://github.com/NeurodataWithoutBorders/pynwb/pull/2052)
- Fixed bug in `IntracellularRecordingsTable.__init__` were `IntracellularResponsesTable` wasn't created correctly when custom category tables were provided @oruebel. [#2031](https://github.com/NeurodataWithoutBorders/pynwb/pull/2031)
- Fixed shape check in `SpikeEventSeries.__init__` to support `AbstractDataChunkIterator` for timestamps/data. @oruebel [#2031](https://github.com/NeurodataWithoutBorders/pynwb/pull/2031)
- Added unit tests to enhance coverage of `core.py`, `image.py`, `spec.py`, `icephys.py`, `epoch.py` and others. @oruebel [#2031](https://github.com/NeurodataWithoutBorders/pynwb/pull/2031)
- Fixed missing `IndexSeries.indexed_images`. @rly [#2074](https://github.com/NeurodataWithoutBorders/pynwb/pull/2074)
- Fixed missing `__nwbfields__` and `_fieldsname` for `NWBData` and its subclasses. @rly [#2082](https://github.com/NeurodataWithoutBorders/pynwb/pull/2082)
- Fixed caching of the type map when using HDMF 4.1.0. @rly [#2087](https://github.com/NeurodataWithoutBorders/pynwb/pull/2087)
- Removed use of complex numbers in scratch tutorial because of incompatibilities with HDMF 4.1.0. @stephprince [#2090](https://github.com/NeurodataWithoutBorders/pynwb/pull/2090/)
- Made `ImagingPlane.description` optional to conform with the NWB Schema. @rly [#2051](https://github.com/NeurodataWithoutBorders/pynwb/pull/2051)

### Documentation and tutorial enhancements
- Added NWB AI assistant to the home page of the documentation. @magland [#2076](https://github.com/NeurodataWithoutBorders/pynwb/pull/2076)

## PyNWB 3.0.0 (February 26, 2025)

### Breaking changes
- The validation methods have been updated with multiple breaking changes. @stephprince [#1911](https://github.com/NeurodataWithoutBorders/pynwb/pull/1911)
   - The behavior of `pynwb.validate(io=...)` now matches the behavior of `pynwb.validate(path=...)`. In previous pynwb versions, `pynwb.validate(io=...)` did not use the cached namespaces during validation. To obtain the same behavior as in previous versions, you can update the function call to `pynwb.validate(io=..., use_cached_namespaces=False)`
   - `pynwb.validate` will return only a list of validation errors instead of a tuple: (list of validation_errors, status code)
   - the `pynwb.validate(path=...)` argument has been added as a replacement for `pynwb.validate(paths=[...])`, which will be deprecated in a future major release [#2024](https://github.com/NeurodataWithoutBorders/pynwb/pull/2024)
   - The validate module has been renamed to `validation.py`. The validate method can be
   imported using `import pynwb; pynwb.validate` or `from pynwb import validate`

### Deprecations
- The following deprecated classes will now raise errors when creating new instances of these classes: ``ClusteringWaveforms``, ``Clustering``, ``SweepTable``. Reading files using these data types will continue to be supported.
- The following methods and arguments have been deprecated:
  - ``ProcessingModule.add_container`` and ``ProcessingModule.add_data_interface`` are replaced by  ``ProcessingModule.add``
  - ``ProcessingModule.get_container`` and ``ProcessingModule.get_data_interface`` are replaced by ``ProcessingModule.get``
  - ``ScratchData.notes`` is deprecated. Use ``ScratchData.description`` instead.
  - ``NWBFile.ic_electrodes`` is deprecated. Use ``NWBFile.icephys_electrodes`` instead.
  - ``NWBFile.ec_electrodes`` is deprecated. Use ``NWBFile.electrodes`` instead.
  - ``NWBFile.icephys_filtering`` is deprecated. Use ``IntracellularElectrode.filtering`` instead.
  - ``NWBFile.modules`` is deprecated. Use ``NWBFile.processing`` instead.
  - ``ImageSeries.format`` is fixed to 'external' if an external file is provided.
  - ``ImageSeries.bits_per_pixel`` is deprecated.
  - ``ImagingPlane.manifold``, ``ImagingPlane.conversion`` and ``ImagingPlane.unit`` are deprecated. Use ``ImagingPlane.origin_coords`` and ``ImagingPlane.grid_spacing`` instead.
  - ``IndexSeries.unit`` is fixed to "N\A".
  - ``IndexSeries.indexed_timeseries`` is deprecated. Use ``IndexSeries.indexed_images`` instead.
- The following deprecated methods have been removed:
  - ``NWBFile.add_ic_electrode`` is removed. Use ``NWBFile.add_icephys_electrode`` instead.
  - ``NWBFile.create_ic_electrode`` is removed. Use ``NWBFile.create_icephys_electrode`` instead.
  - ``NWBFile.get_ic_electrode`` is removed. Use ``NWBFile.get_icephys_electrode`` instead.
  - ``pynwb._get_resources`` is removed.

### Enhancements and minor changes
- Added `__all__` to modules. @bendichter [#2021](https://github.com/NeurodataWithoutBorders/pynwb/pull/2021)
- Added `pynwb.read_nwb` convenience method to simplify reading an NWBFile written with any backend @h-mayorquin [#1994](https://github.com/NeurodataWithoutBorders/pynwb/pull/1994)
- Constrained `hdmf<5` to prevent future compatibility issues. [#2040](https://github.com/NeurodataWithoutBorders/pynwb/pull/2040)

### Bug fixes
- Made distance, orientation, and field_of_view optional in OpticalSeries to match schema @bendichter [#2023](https://github.com/NeurodataWithoutBorders/pynwb/pull/2023)
- Added support for NWB schema 2.8.0. @rly [#2001](https://github.com/NeurodataWithoutBorders/pynwb/pull/2001)
  - Removed `SpatialSeries.bounds` field that was not functional. This will be fixed in a future release. @rly [#1907](https://github.com/NeurodataWithoutBorders/pynwb/pull/1907), [#1996](https://github.com/NeurodataWithoutBorders/pynwb/pull/1996)
  - Added support for `NWBFile.was_generated_by` field. @stephprince [#1924](https://github.com/NeurodataWithoutBorders/pynwb/pull/1924)
  - Added support for `model_number`, `model_name`, and `serial_number` fields to `Device`. @stephprince [#1997](https://github.com/NeurodataWithoutBorders/pynwb/pull/1997)
  - Deprecated `EventWaveform` neurodata type. @rly [#1940](https://github.com/NeurodataWithoutBorders/pynwb/pull/1940)
  - Deprecated `ImageMaskSeries` neurodata type. @rly [#1941](https://github.com/NeurodataWithoutBorders/pynwb/pull/1941)
- Added enhancements to the validation CLI. @stephprince [#1911](https://github.com/NeurodataWithoutBorders/pynwb/pull/1911)
  - Added an entry point for the validation module. You can now use `pynwb-validate "file.nwb"`.
  - Added the `--json-outpath-path` CLI argument to output validation results in a machine readable format.
- Removed python 3.8 support, added python 3.13 support. @stephprince [#2007](https://github.com/NeurodataWithoutBorders/pynwb/pull/2007)
- Added warnings when using positional arguments in `Container` constructor methods. Positional arguments will raise errors in the next major release. @stephprince [#1972](https://github.com/NeurodataWithoutBorders/pynwb/pull/1972)
- `mock_ElectricalSeries`. Make number of electrodes between data and electrode region agree when explicitly passing data @h-mayorquin [#2019](https://github.com/NeurodataWithoutBorders/pynwb/pull/2019)

### Documentation and tutorial enhancements
- Updated `SpikeEventSeries`, `DecompositionSeries`, and `FilteredEphys` examples. @stephprince [#2012](https://github.com/NeurodataWithoutBorders/pynwb/pull/2012)
- Replaced deprecated `scipy.misc.face` dataset in the images tutorial with another example. @stephprince [#2016](https://github.com/NeurodataWithoutBorders/pynwb/pull/2016)
- Removed Allen Brain Observatory example which was unnecessary and difficult to maintain. @rly [#2026](https://github.com/NeurodataWithoutBorders/pynwb/pull/2026)

## PyNWB 2.8.3 (November 19, 2024)

### Enhancements and minor changes
- Added `NWBHDF5IO.read_nwb` convenience method to simplify reading an NWB file. @h-mayorquin [#1979](https://github.com/NeurodataWithoutBorders/pynwb/pull/1979)
- Removed unused references to region references and builders in preparation for changes in HDMF 4.0. @rly [#1991](https://github.com/NeurodataWithoutBorders/pynwb/pull/1991)
- Made gain an optional argument for PatchClampSeries to match the schema. @stephprince [#1975](https://github.com/NeurodataWithoutBorders/pynwb/pull/1975)
- Added warning when writing files with `NWBHDF5IO` without the `.nwb` extension. @stephprince [#1978](https://github.com/NeurodataWithoutBorders/pynwb/pull/1978)
- Cache global type map to speed import 3X. @sneakers-the-rat [#1931](https://github.com/NeurodataWithoutBorders/pynwb/pull/1931)

### Bug fixes
- Fixed bug in how `ElectrodeGroup.__init__` validates its `position` argument. @oruebel [#1770](https://github.com/NeurodataWithoutBorders/pynwb/pull/1770)
- Changed `SpatialSeries.reference_frame` from required to optional as specified in the schema. @rly [#1986](https://github.com/NeurodataWithoutBorders/pynwb/pull/1986)

### Documentation and tutorial enhancements
- Added documentation example for `SpikeEventSeries`. @stephprince [#1983](https://github.com/NeurodataWithoutBorders/pynwb/pull/1983)
- Added documentation example for `AnnotationSeries`. @stephprince [#1989](https://github.com/NeurodataWithoutBorders/pynwb/pull/1989)
- Added documentation example for `DecompositionSeries`. @stephprince [#1981](https://github.com/NeurodataWithoutBorders/pynwb/pull/1981)

## PyNWB 2.8.2 (September 9, 2024)

### Enhancements and minor changes
- Added support for numpy 2.0. @mavaylon1 [#1956](https://github.com/NeurodataWithoutBorders/pynwb/pull/1956)
- Make `get_cached_namespaces_to_validate` a public function @stephprince [#1961](https://github.com/NeurodataWithoutBorders/pynwb/pull/1961)

### Documentation and tutorial enhancements
- Added pre-release pull request instructions to release process documentation @stephprince [#1928](https://github.com/NeurodataWithoutBorders/pynwb/pull/1928)
- Added section on how to use the `family` driver in `h5py` for splitting data across multiple files @oruebel [#1949](https://github.com/NeurodataWithoutBorders/pynwb/pull/1949)

### Bug fixes
- Fixed `can_read` method to return False if no nwbfile version can be found @stephprince [#1934](https://github.com/NeurodataWithoutBorders/pynwb/pull/1934)
- Changed `epoch_tags` to be a NWBFile property instead of constructor argument. @stephprince [#1935](https://github.com/NeurodataWithoutBorders/pynwb/pull/1935)
- Exposed option to not cache the spec in `NWBHDF5IO.export`. @rly [#1959](https://github.com/NeurodataWithoutBorders/pynwb/pull/1959)

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
- Added `bounds` field to `SpatialSeries` to set optional boundary range (min, max) for each dimension of data. @mavaylon1 [#1869](https://github.com/NeurodataWithoutBorders/pynwb/pull/1869)
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
