Prepare for release of PyNWB [version]

### Before merging:
- [ ] Make sure all PRs to be included in this release have been merged to `dev`.
- [ ] Major and minor releases: Update the dependency version bounds in `pyproject.toml` and the pinned
  versions in `environment-ros3.yml` to the latest as needed. The `zarr` and `numcodecs` upper bounds in the
  `zarr` extra track hdmf-zarr's own bounds. Check hdmf-zarr's requirements before touching them rather than
  raising them to the latest release.
- [ ] Update the actions referenced in `.github/workflows/` to their latest releases. `pypa/gh-action-pypi-publish`
  validates the distributions with the `twine` and `packaging` versions it bundles, and an outdated release rejects
  metadata that current build backends emit. Set the `twine` pin in the "Check distribution metadata" steps to the
  version in the action's
  [`requirements/runtime.txt`](https://github.com/pypa/gh-action-pypi-publish/blob/release/v1/requirements/runtime.txt)
  (the `release/v1` branch tracks the latest v1 release).
- [ ] Major releases: Remove the deprecated functionality slated for removal in this version.
- [ ] Check legal file dates and information in `Legal.txt`, `license.txt`, `README.rst`, `docs/source/conf.py`,
  and any other locations as needed
- [ ] Update `pyproject.toml` as needed
- [ ] Confirm the version number matches the severity of the changes, following
  [semantic versioning](https://semver.org). A changelog entry that removes or narrows accepted input, changes a
  return type, or turns a warning into an exception is a breaking change and belongs in a major release. Two
  cases are exempt from that rule and may go in a minor release: input that was accepted but could not be
  written or read back correctly, and a change in the type of an exception that was already raised for the same
  input. Record the reasoning in this pull request.
- [ ] Update `README.rst` as needed
- [ ] Update `src/pynwb/nwb-schema` submodule as needed. Check the version number and commit SHA
  manually. Make sure we are using the latest release and not the latest commit on the `main` branch.
- [ ] Update changelog (set release date) in `CHANGELOG.md` and any other docs as needed
- [ ] Cross-check the changelog against `git log --oneline <previous-tag>..HEAD` so that every merged PR is
  represented.
- [ ] Confirm the release notes will be extracted from the new heading by running the `awk` from
  `deploy_release.yml` with `hdr="## PyNWB <version>"` against `CHANGELOG.md` and checking that the output is
  non-empty and stops before the previous version's heading.
- [ ] Run tests locally including gallery and validation tests, and inspect all warnings and outputs
  (`python test.py -v -p -i -b -w -x > out.txt 2>&1`). Try to remove all warnings.
- [ ] Test docs locally and inspect all warnings and outputs `cd docs; make clean && make html`
- [ ] Build and test-install the distributions from a clean clone (`git clone --recurse-submodules` into a temp
  directory): run `python -m build`, then install the `.whl` and the `.tar.gz` into separate fresh virtual
  environments and confirm `import pynwb`, that `nwb-schema/core` ships with the expected schema version, and that
  writing and validating a minimal `NWBFile` succeeds.
- [ ] After pushing this branch to GitHub, manually trigger the "Run all tests" GitHub Actions workflow on this
  branch by going to https://github.com/NeurodataWithoutBorders/pynwb/actions/workflows/run_all_tests.yml, selecting
  "Run workflow" on the right, selecting this branch, and clicking "Run workflow". Make sure all tests pass, and
  check the ROS3 streaming jobs specifically, since those need a conda environment and are not run locally.
- [ ] Check that the readthedocs build for this PR succeeds (see the PR check)

### After merging:
1. Create release by following steps in `docs/source/make_a_release.rst` or use alias `git pypi-release [tag]` if set up
2. After the CI bot creates the new release (wait ~10 min), check the release notes on the
   [GitHub releases page](https://github.com/NeurodataWithoutBorders/pynwb/releases). The workflow fills them
   from this version's section of `CHANGELOG.md`, and falls back to auto-generated notes if that section is
   empty or its heading does not match the tag.
3. Check that the readthedocs "stable" build runs and succeeds
4. Either monitor [conda-forge/pynwb-feedstock](https://github.com/conda-forge/pynwb-feedstock) for the
   regro-cf-autotick-bot bot to create a PR updating the version of PyNWB to the latest PyPI release, usually within
   24 hours of release, or manually create a PR updating `recipe/meta.yaml` with the latest version number
   and SHA256 retrieved from PyPI > PyNWB > Download Files > View hashes for the `.tar.gz` file. Re-render and update
   dependencies as needed.
