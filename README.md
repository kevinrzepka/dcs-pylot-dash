# About

This is a free open-source tool to generate Lua and HTML code that allows showing live plane telemetry data from the
video game "DCS World" in a web browser.

The live version can be found at: https://pylotdash.eu

# Disclaimer

This private, non-commercial project is not affiliated with, associated with, authorized by, endorsed by, approved by,
or in any other way officially connected with "DCS World", "Eagle Dynamics SA" and/or any of its subsidiaries,
affiliates, and related entities.
The official website of "DCS World" can be found at https://www.digitalcombatsimulator.com/

# Third-party licenses

This software uses third-party components.
See [third_party_licenses.txt](./third_party_licenses.txt) for their respective copyright and license notices. <br>
For the licenses of third-party components that are distributed (superset for operators and users),
see [third_party_licenses_distributed.txt](./third_party_licenses_distributed.txt).

# License

See [LICENSE](./LICENSE)

# Development

## Environment Setup

This section describes how to install all required tools to test, build and run this software.

### Docker

See https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository

### Python 3.14

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

## Testing

`uv run pytest` (included in `./build.sh`)

## UI Development

### Set up Prettier

https://prettier.io/docs/install

- install: `pnpm add --save-dev --save-exact prettier@3.7.4`
- dry-run: `npx prettier . --check`
- run: `pnpm exec prettier . --write`

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

### Set up PrimeNG

https://primeng.org/installation

- add packages: `pnpm add pnpm add primeng@21.0.1 @primeuix/themes@2.0.2`
- Add icons: https://primeng.org/icons
    - `pnpm add primeicons@7.0.0`
    - `styles.css`: `@import "primeicons/primeicons.css";`

### Add drag and drop

https://angular.dev/guide/drag-drop

- apply updates: `pnpm update`

### Angular CSP caveat

https://stackoverflow.com/questions/67565858/angular-12-css-optimization-inline-event-handler-with-content-security-policy/67582075#67582075

Must add the following to the CSP:

`script-src 'unsafe-hashes' 'sha256-MhtPZXr7+LpJUY5qtMutB+qWfQtMaPccfe7QXtCcEYc=' 'self';`

## Upgrading dependencies

After upgrading dependencies, increment and sync the versions, generate the SBOMs, generate the attributions, and run
the vulnerability scan:

- `uv self update`
- Update [`Dockerfile`](./Dockerfile)
- `./sync-versions.sh`
- `./generate-sboms.sh`
- `./generate-attributions.sh`
- `trivy sbom --disable-telemetry sboms/sbom.json`

### Python

to include all groups, not just prod and dev, they must be specified explicitly:

- `uv sync --all-groups`

### Node

- Find Angular updates, but this includes versions that may not satisfy pnpm constraints: `pnpm run ng update`
- Update all packages (ensure appropriate version syntax in [
  `dcs-pylot-dash-ui/package.json`](dcs-pylot-dash-ui/package.json) : `pnpm update`

## Versioning

- Source of truth: `pyproject.toml` -> `uv version --short`
- Set new version: `uv version <new-version>`
- Sync versions after upgrade: `./sync-versions.sh` (included in `./build.sh`)

relevant locations:

- [pyproject.toml](pyproject.toml)
- `dcs_pylot_dash.app_settings.DCSPylotDashAppSettings`
- [dcs-pylot-dash-ui/package.json](dcs-pylot-dash-ui/package.json)
- [deployment/dcs-pylot-dash/Chart.yaml](deployment/dcs-pylot-dash/Chart.yaml)

# Building from source

`./build.sh`

## Build UI

`./build-ui.sh`

Manual steps:

- install all: `pnpm i --frozen-lockfile`
- prod dependencies only: `pnpm i --frozen-lockfile --prod`
- build dist: `pnpm run build`

## Build Docker image

`./build-image.sh`

https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html

- list of capabilities: https://docs.docker.com/engine/containers/run/#runtime-privilege-and-linux-capabilities
- set ulimits: https://ss64.com/bash/ulimit.html,
    - but: http://docs.docker.com/reference/cli/docker/container/run/#for-nproc-usage

run with shell:

```bash
sudo docker run --rm -it --read-only --memory-swappiness=0 --security-opt=no-new-privileges --cap-drop all -m=1g --cpus=1 --entrypoint /bin/bash kevinrzepka/dcs-pylot-dash
```

run with regular entrypoint:

```bash
sudo docker run --rm -it --read-only --memory-swappiness=0 --security-opt=no-new-privileges --cap-drop all -m=1g --cpus=1 -p 8000:8000 kevinrzepka/dcs-pylot-dash:latest
```

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
- However, for many packages, like angular, the license and external ref information is missing entirely.

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
    - homepage link, not always GitHub, sometimes GitHub but link to tree document

Non-working options with `npm` only:

- generate `package-lock.json`: `npm i --package-lock-only`
- generate SBOM via plain np fails with an error:
  `npm sbom --package-lock-only=true --sbom-type=application --sbom-format=cyclonedx`
- cleanup: `rm -f package-lock.json`

Other options:

- license files are present in installed `./node_modules`
- angular generates `dcs-pylot-dash-ui/dist/dcs-pylot-dash-ui/3rdpartylicenses.txt`

## Vulnerability Scan (Trivy)

https://trivy.dev/docs/latest/guide/target/sbom/#cyclonedx

- image: `sudo trivy image --disable-telemetry dcs-pylot-dash`
- SBOM: `trivy sbom --disable-telemetry sboms/sbom.json`
- just `uv.lock`: `trivy fs --disable-telemetry --include-dev-deps uv.lock`
- repository (finds `uv.lock`): `trivy repo --disable-telemetry --include-dev-deps .`
    - can add `.trivyignore`, but that does not work

## Generate third-party attribution / license notice

`./generate-attributions.sh`

manual steps:

- set GitHub API PAT: ` export GITHUB_LICENSE_API_TOKEN=github_pat_<HEX...>`
- all components: `./generate-attribution.sh sboms/sbom.json third_party_licenses.txt`
- distributed (i.e. python prod + ui prod) components:
  `./generate-attribution.sh sboms/sbom-ui-prod.json third_party_licenses_distributed.txt`

When building the UI, angular also generates a file: `dcs-pylot-dash-ui/dist/dcs-pylot-dash-ui/3rdpartylicenses.txt`

# Deployment

The deployment scenario is that there is an `nginx` reverse proxy that handles TLS termination and forwards requests to
the k8s workloads. The reverse proxy is exposed on the WAN interface, no k8s workloads should be exposed on the WAN
interface. The following sections describe how to (not) achieve this.

## Preparing the K3s cluster

Install `k3s`:

```shell
curl -sfL https://get.k3s.io | sh -
sudo kubectl get nodes
systemctl status k3s
ln -s /etc/rancher/k3s/k3s.yaml ~/.kube/config
```

### `LoadBalancer` service - NOT recommended

Impossible to not expose the load balancer pod on the WAN interface.

### `LoadBalancer` service and `ingress` (`traefik`) - NOT recommended but possible

**IMPORTANT:** ensure `traefik` uses a different listening address (e.g. `127.0.0.1`) than the default `0.0.0.0` and
different ports than
`80`/`443`, e.g. `50080`/`50443`:

- https://docs.k3s.io/networking/networking-services
- https://github.com/k3s-io/k3s-charts/tree/main/charts/traefik
- https://docs.k3s.io/add-ons/helm#customizing-packaged-components-with-helmchartconfig
- https://github.com/k3s-io/k3s-charts/blob/main/charts/traefik/38.0.101%2Bup38.0.1/values.yaml

- create an additional `HelmChartConfig` manifest in `/var/lib/rancher/k3s/server/manifests`

```shell
cat << EOF | sudo tee /var/lib/rancher/k3s/server/manifests/traefik-port-config.yaml
apiVersion: helm.cattle.io/v1
kind: HelmChartConfig
metadata:
  name: traefik
  namespace: kube-system
spec:
  valuesContent: |-
    ports:
      traefik:
        hostIP: "127.0.0.1"
      web:
        exposedPort: 50080
      websecure:
        exposedPort: 50443
EOF
```

- apply values: `sudo systemctl restart k3s`
- ensure nat entries are updated: `sudo nft list table nat`
- webapp should be available at:
    - the "intended" host address: `http://localhost:50080`
    - the traefik node address, e.g. `http://10.42.0.50:8000/`
    - the cluster IP of the service, e.g.: `http://10.43.132.111:8080`
    - the webapp node address, e.g.: `http://10.42.0.61:8000`
- webapp should **not** be available at:
    - the host interface address, e.g. `http://10.0.2.15:50080/`

**Problem:** Unfortunately, this causes the health (`/ping`) check bind address to be `127.0.0.1`, which of course
fails the liveness
and readiness probes, since connection attempts from the k8s api server are refused. At the moment, the helm chart does
not allow specifying a bind address different from `hostIp` for the health check. And the `hostIp` must be `127.0.0.1`
or
the NAT rules will expose `traefik` on the WAN interface. <br> It is also not possible to disable the probes via the
helm
chart. A hacky solution that works is to manually edit the deployment and delete the probes there.

### `NodePort` service without `ingress` - recommended

- disable `traefik` in the `k3s` service: Append `--disable=traefik` to `ExecStart` in
  `/etc/systemd/system/k3s.service`:

```
ExecStart=/usr/local/bin/k3s \
    server --disable=traefik \
```

- configure the API server to expose `NodePort` services only on `127.0.0.1`: Append to `/etc/rancher/k3s/config.yaml`:

```
kube-proxy-arg:
  - "nodeport-addresses=127.0.0.1/32"
```

- reload the service:

```
systemctl daemon-reload
systemctl restart k3s
```

Now the `nat` table should look like this (truncated for readability):

```
nft list table nat
# Warning: table ip nat is managed by iptables-nft, do not touch!
table ip nat {
	chain PREROUTING {
		type nat hook prerouting priority dstnat; policy accept;
		 counter packets 17 bytes 1524 jump KUBE-SERVICES
		 ...
	}
	chain KUBE-SERVICES {
	    ...
		ip daddr 127.0.0.1  counter packets 10 bytes 600 jump KUBE-NODEPORTS
	}
	chain KUBE-NODEPORTS {
		ip daddr 127.0.0.0/8 ip protocol tcp  tcp dport 32080 xt match "nfacct" counter packets 0 bytes 0 jump KUBE-EXT-CDOT2HNW3SM5ZYBQ
		ip protocol tcp  tcp dport 32080 counter packets 0 bytes 0 jump KUBE-EXT-CDOT2HNW3SM5ZYBQ
	}
}
```

## Installing the Helm chart

- Install helm: https://helm.sh/docs/intro/install/
- add to `~/.profile` (also for `root` when running helm with `sudo` later):
  `export KUBECONFIG=/etc/rancher/k3s/k3s.yaml`

See [Chart notes](./deployment/dcs-pylot-dash/templates/NOTES.txt)

- Ensure the image was bult for the current `HEAD`: `./build.sh`

Install (`--dry-run=server`):

```shell
image_tag=$(git rev-parse HEAD)
sudo docker save kevinrzepka/dcs-pylot-dash:$image_tag | sudo k3s ctr images import -
sudo helm upgrade dcs-pylot-dash deployment/dcs-pylot-dash \
-n dcs-pylot-dash -i --dry-run=server --debug \
--set image.tag="$image_tag"
```

Uninstall:

```shell
sudo helm uninstall dcs-pylot-dash \
-n dcs-pylot-dash --debug
```
