# PyNWB Changelog

## PyNWB 2.0.0 (Upcoming)

### Internal improvements:
- Add support for nwb-schema 2.3.0
  - ...

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
