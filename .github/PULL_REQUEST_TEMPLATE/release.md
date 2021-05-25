Prepare for release of PyNWB [version]

### Before merging:
- [ ] Major and minor releases: Update package versions in `requirements.txt`, `requirements-dev.txt`,
  `requirements-doc.txt`, `requirements-min.txt`, `setup.py` as needed
  See https://requires.io/github/NeurodataWithoutBorders/pynwb/requirements/?branch=dev
- [ ] Check legal file dates and information in `Legal.txt`, `license.txt`, `README.rst`, `docs/source/conf.py`,
  and any other locations as needed
- [ ] Update `setup.py` as needed
- [ ] Update `README.rst` as needed
- [ ] Update `src/pynwb/nwb-schema` submodule as needed. Check the version number and commit SHA manually
- [ ] Update changelog (set release date) in `CHANGELOG.md` and any other docs as needed
- [ ] Run tests locally including gallery tests and validation tests, and inspect all warnings and outputs
  (`python test.py -v > out.txt`)
- [ ] Test docs locally (`make apidoc`, `make html`)
- [ ] Push changes to this PR and make sure all PRs to be included in this release have been merged
- [ ] Check that the readthedocs build for this PR succeeds (build latest to pull the new branch, then activate and
  build docs for new branch): https://readthedocs.org/projects/pynwb/builds/

### After merging:
1. Create release by following steps in `docs/source/make_a_release.rst` or use alias `git pypi-release [tag]` if set up
2. After the CI bot creates the new release (wait ~10 min), update the release notes on the
   [GitHub releases page](https://github.com/NeurodataWithoutBorders/pynwb/releases) with the changelog
3. Check that the readthedocs "latest" and "stable" builds run and succeed
4. Update [conda-forge/pynwb-feedstock](https://github.com/conda-forge/pynwb-feedstock) with the latest version number
   and SHA256 retrieved from PyPI > PyNWB > Download Files > View hashes for the `.tar.gz` file. Re-render as needed
