# TODO

- oss attribution: Add best-effort approach for libraries with odd license file names
- package isoduration: SbomLicenseContainer(license=SbomLicense(name="declared license of 'isoduration'", id=None,
  url=None, acknowledgement='declared', text=SbomLicenseText(content='UNKNOWN', content_type='text/plain',
  encoding=None)))
- warning for generated scripts, e.g., with MIT license
- uv test instructions for tools
- add security.txt?
- add CSP and nonce: https://angular.dev/best-practices/security#content-security-policy
- https://angular.dev/best-practices/security#enforcing-trusted-types?
- copyright, license in generated files
- include ui libs in sbom and attribution
- rate limiting config
    - test
- input validation
    - test
- copy resources to docker image
- option to remove versions in attribution (default)

# About

# Usage

## Uvicorn configuration

https://uvicorn.dev/settings/

# Development

## Environment setup

This section describes how to install all required tools to test, build and run this software.

### Docker

See https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository

### Python

https://launchpad.net/~deadsnakes/+archive/ubuntu/ppa

```shell
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.14 python3.14-dev python3.14-venv
```

### uv

https://docs.astral.sh/uv/getting-started/installation/#standalone-installer

```shell
curl -LsSf https://astral.sh/uv/install.sh | sh
uv self update
echo 'eval "$(uv generate-shell-completion bash)"' >> ~/.bashrc
```

### pnpm

https://pnpm.io/installation

- install:

```shell
curl -fsSL https://get.pnpm.io/install.sh | env PNPM_VERSION="10.24.0" bash -
source /home/vbox/.bashrc
```

- configure:

```shell
pnpm env list --remote
pnpm env add -g 24.11.1
pnpm env use -g 24.11.1
npm config set ignore-scripts true --global
pnpm config set -g minimumReleaseAge 10080
pnpm config get
```

### Trivy

https://trivy.dev/docs/latest/getting-started/installation/#debianubuntu-official

```bash
sudo apt install -y wget gnupg
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | gpg --dearmor | sudo tee /usr/share/keyrings/trivy.gpg > /dev/null
echo "deb [signed-by=/usr/share/keyrings/trivy.gpg] https://aquasecurity.github.io/trivy-repo/deb generic main" | sudo tee -a /etc/apt/sources.list.d/trivy.list
sudo apt update && sudo apt install trivy -y
```

### Pre-Commit

- install hooks: `pre-commit install`
- run all pre-commit hooks: `uv run pre-commit run --all-files`
- create venv from lockfile: `uv sync --frozen`

## UI

### Set up Angular project

https://angular.dev/installation

- install Angular CLI: `pnpm install -g @angular/cli@21.0.2`
- create project with `pnpm`, this respects the min age policy:
  `ng new  dcs-pylot-dash-ui --package-manager pnpm --skip-git true --skip-tests true --ssr false --style css --routing true --ai-config none`
- check dependencies:
    - `pnpm list`
    - `pnpm audit`
    - `pnpm outdated`
- set up dev proxy: https://angular.dev/tools/cli/serve#proxying-to-a-backend-server
- start: `pnpm start`

### Set up Prettier

https://prettier.io/docs/install

- install: `pnpm add --save-dev --save-exact prettier@3.7.4`
- dry-run: `npx prettier . --check`
- run: `pnpm exec prettier . --write`

### Set up PrimeNG

https://primeng.org/installation

- add packages: `pnpm add pnpm add primeng@21.0.1 @primeuix/themes@2.0.2`
- Add icons: https://primeng.org/icons
    - `pnpm add primeicons@7.0.0`
    - `styles.css`: `@import "primeicons/primeicons.css";`

### Add Angular component

- add component: `ng generate component hello --skip-tests true`

### Add drag and drop

https://angular.dev/guide/drag-drop

# Building from source

## Build UI

- install all: `pnpm i --frozen-lockfile`
- prod dependencies only: `pnpm i --frozen-lockfile --prod`

## Build Docker image

https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html

- list of capabilities: https://docs.docker.com/engine/containers/run/#runtime-privilege-and-linux-capabilities
- set ulimits: https://ss64.com/bash/ulimit.html,
    - but: http://docs.docker.com/reference/cli/docker/container/run/#for-nproc-usage

Build and run with shell:

```bash
sudo docker build -t kevinrzepka/dcs-pylot-dash . && \
sudo docker run --rm -it --read-only --memory-swappiness=0 --security-opt=no-new-privileges --cap-drop all -m=1g --cpus=1 --entrypoint /bin/bash kevinrzepka/dcs-pylot-dash
```

Build and run with regular entrypoint:

```bash
sudo docker build -t kevinrzepka/dcs-pylot-dash . && \
sudo docker run --rm -it --read-only --memory-swappiness=0 --security-opt=no-new-privileges --cap-drop all -m=1g --cpus=1 kevinrzepka/dcs-pylot-dash
```

## Vulnerability Scan (Trivy)

https://trivy.dev/docs/latest/guide/target/sbom/#cyclonedx

- image: `sudo trivy image --disable-telemetry dcs-pylot-dash`
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

### For UI

See:

- https://docs.npmjs.com/cli/v11/commands/npm-sbom
- https://github.com/orgs/pnpm/discussions/3367

Problems:

- `pnpm` does not have an `sbom` command
- `npm sbom` requires a `package-lock.json` file, which is not generated by `pnpm`
- running `npm i --package-lock-only` will lock different versions
- some components appear multiple times in different versions

`cyclonedx/cdxgen`:
See https://github.com/cdxgen/cdxgen?tab=readme-ov-file#resolving-licenses

- set required env vars: ` export GITHUB_TOKEN=github_pat_<HEX...>`
- run:
  `FETCH_LICENSE=true pnpm -C ./dcs-pylot-dash-ui exec cdxgen -t pnpm --json-pretty --profile license-compliance -o ../sboms/sbom-ui.json`
    - this takes a long time, but there are still no license texts in the SBOM, even with `--profile license-compliance`
    - the external references are also present when `FETCH_LICENSE=false` -> missing benefit?!
- the simpler command should suffice:
  `pnpm -C ./dcs-pylot-dash-ui exec cdxgen -t pnpm --json-pretty -o ../sboms/sbom-ui.json`

`cyclonedx-npm`:
https://www.npmjs.com/package/@cyclonedx/cyclonedx-npm

- does not work because npm does not understand `node_modules` installed by `pnpm`:
  `pnpm exec cyclonedx-npm --gather-license-texts --flatten-components --validate -o ../sboms/sbom-ui.json`

Options with Trivy and `pnpm`:

- SBOM, with license IDs, but missing text and any external refs:
  `trivy fs --scanners license --format cyclonedx --output result.json ./dcs-pylot-dash-ui`
    - does have a `purl`, e.g.: `"purl": "pkg:npm/%40angular/cdk@21.0.2`
- license info, not in SBOM format: `pnpm licenses list --json`
    - `author` mentioned
    - homepage link, not always github, sometimes github but link to tree document

Non-working options with `npm` only:

- generate `package-lock.json`: `npm i --package-lock-only`
- generate SBOM via plain np fails with an error:
  `npm sbom --package-lock-only=true --sbom-type=application --sbom-format=cyclonedx`
- cleanup: `rm -f package-lock.json`

Other options:

- license files are present in installed `./node_modules`

## Generate third-party attribution / license notice

- set GitHub API PAT: ` export GITHUB_LICENSE_API_TOKEN=github_pat_<HEX...>`
- run: `./generate-attribution.sh`

# Third-party licenses

This software uses third-party components that may be copyrighted by others.
See [third_party_licenses.txt](./third_party_licenses.txt) for details.

# License

See [LICENSE](./LICENSE)

# Disclaimer

This private, non-commercial project is not affiliated with, associated with, authorized by, endorsed by, approved by,
or in any other way officially connected with "DCS World", "Eagle Dynamics SA" and/or any of its subsidiaries,
affiliates, and
related entities.
The official website of "DCS World" can be found at https://www.digitalcombatsimulator.com/
