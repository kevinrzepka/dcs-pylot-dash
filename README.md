# TOOD

- oss attribution
- privacy policy
- ui
- caching for license info, esp. github responses
- package isoduration: SbomLicenseContainer(license=SbomLicense(name="declared license of 'isoduration'", id=None,
  url=None, acknowledgement='declared', text=SbomLicenseText(content='UNKNOWN', content_type='text/plain',
  encoding=None)))
- non-affiliation notice
- warning for generated scripts, e.g., with MIT license

# About

# Usage

# Building from source

## Generate SBOMs

`./generate-sboms.sh`

Problems:

- beware that `uv run` syncs the entire `venv`, unless `--no-sync` is specified
- `uv sync` does not include arbitrary group names, `--all-groups` is needed
- `uvx` runs a tool in a new `venv`
- `cyclonedx-py venv` always uses the current `venv`, where only the tool exists now
- `--no-default-groups` does not work, but `--only-group` does
- `cyclonedx-py requirements` does not include license information, unlike `venv`
- `uv pip list` also does not include license or URL

The best approach is currently to include cyclonedx-py in the SBOM, by running `uv run cyclonedx-py`

# License

See [LICENSE](./LICENSE)