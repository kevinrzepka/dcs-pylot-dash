# TODO

- oss attribution
- privacy policy
- ui
- package isoduration: SbomLicenseContainer(license=SbomLicense(name="declared license of 'isoduration'", id=None,
  url=None, acknowledgement='declared', text=SbomLicenseText(content='UNKNOWN', content_type='text/plain',
  encoding=None)))
- non-affiliation notice
- warning for generated scripts, e.g., with MIT license
- uv test instructions for tools
- fix duplicate log lines
- test image content:
    - no dev packages
    - file permissions work

# About

# Usage

## Uvicorn configuration

https://uvicorn.dev/settings/

# Development

## Environment setup

### Trivy

https://trivy.dev/docs/latest/getting-started/installation/#debianubuntu-official

```bash
sudo apt install -y wget gnupg
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | gpg --dearmor | sudo tee /usr/share/keyrings/trivy.gpg > /dev/null
echo "deb [signed-by=/usr/share/keyrings/trivy.gpg] https://aquasecurity.github.io/trivy-repo/deb generic main" | sudo tee -a /etc/apt/sources.list.d/trivy.list
sudo apt update && sudo apt install trivy -y
```

### Pre-Commit

run all pre-commit hooks: `uv run pre-commit run --all-files`
create venv from lockfile: `uv sync --frozen`

# Building from source

## Build Docker image

https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html

list of capabilities: https://docs.docker.com/engine/containers/run/#runtime-privilege-and-linux-capabilities
set ulimits: https://ss64.com/bash/ulimit.html,
but: http://docs.docker.com/reference/cli/docker/container/run/#for-nproc-usage

Build and run with shell:

```bash
sudo docker build -t dcs-pylot-dash . && \
sudo docker run --rm -it --read-only --memory-swappiness=0 --security-opt=no-new-privileges --cap-drop all -m=1g --cpus=1 --entrypoint /bin/bash dcs-pylot-dash
```

Build and run with regular entrypoint:

```bash
sudo docker build -t dcs-pylot-dash . && \
sudo docker run --rm -it --read-only --memory-swappiness=0 --security-opt=no-new-privileges --cap-drop all -m=1g --cpus=1
```

### Check image

## Vulnerability Scan (Trivy)

https://trivy.dev/docs/latest/guide/target/sbom/#cyclonedx

- image: `sudo trivy --disable-telemetry image dcs-pylot-dash`
- SBOM: `trivy sbom --disable-telemetry sboms/sbom.json`
- just `uv.lock`: `trivy fs --disable-telemetry --include-dev-deps uv.lock`
- repository (finds `uv.lock`): `trivy repo --disable-telemetry --include-dev-deps .`
    - can add `.trivyignore`, but that does not work

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

# Third-party licenses

This software uses third-party components that may be copyrighted by others.
See [third_party_licenses.txt](./third_party_licenses.txt) for details.

# License

See [LICENSE](./LICENSE)
