#!/usr/bin/env bash
#
# Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE
#

set -euo pipefail

SBOM_DIR='sboms'
mkdir -p "$SBOM_DIR"

# generate python full SBOM
sbom_python_full_file_name=sbom-api.json
sbom_file="$SBOM_DIR/$sbom_python_full_file_name"
# ensure regular venv is used
source .venv/bin/activate
uv sync --active --group cyclonedx
uv run --no-sync --active cyclonedx-py venv --gather-license-texts > "$sbom_file"
num_components_full=$(cat $sbom_file | jq -r '.components | length')

# generate python prod SBOM
env_name='prod'
venv_name=".venv-$env_name"
sbom_file="$SBOM_DIR/sbom-api-$env_name.json"
rm -rf "$venv_name"
uv venv "$venv_name"
source "$venv_name"/bin/activate
uv sync --active --group cyclonedx --no-group dev
uv run --no-sync --active cyclonedx-py venv --gather-license-texts > "$sbom_file"
rm -rf "$venv_name"
num_components_prod=$(cat $sbom_file | jq -r '.components | length')

# generate python dev SBOM
env_name='dev'
venv_name=".venv-$env_name"
sbom_file="$SBOM_DIR/sbom-api-$env_name.json"
rm -rf "$venv_name"
uv venv "$venv_name"
source "$venv_name"/bin/activate
uv sync --active --only-group cyclonedx --only-group dev
uv run --no-sync --active cyclonedx-py venv --gather-license-texts > "$sbom_file"
rm -rf "$venv_name"
num_components_dev=$(cat $sbom_file | jq -r '.components | length')

# perform sanity checks
[ "$num_components_full" -gt 0 ]
[ "$num_components_dev" -gt 0 ]
[ "$num_components_prod" -gt 0 ]
[ "$num_components_dev" -le "$num_components_full" ]
[ "$num_components_prod" -le "$num_components_full" ]
# [ "$num_components_dev" -ne "$num_components_prod" ]  it might actually be

# ensure regular venv is used again
source .venv/bin/activate

# generate UI SBOM
sbom_ui_full_file_name="sbom-ui.json"
sbom_file="$SBOM_DIR/$sbom_ui_full_file_name"
#trivy fs --format cyclonedx --output "$sbom_file" ./dcs-pylot-dash-ui/pnpm-lock.yaml
# generate UI SBOM with cdxgen
pnpm -C ./dcs-pylot-dash-ui exec cdxgen -t pnpm --json-pretty -o ../"$sbom_file"

# merge full SBOM
sudo docker run --rm -t -v ./"$SBOM_DIR"/:/"$SBOM_DIR"/ cyclonedx/cyclonedx-cli@sha256:4c42a0f3f24a62aee3c914f5a0c2f5cbf50cdf61093e250c3dd952c4efa012d0 \
merge --group "kevinrzepka" --name "dcs-pylot-dash" --version "1.0.0" \
--input-files "$SBOM_DIR/$sbom_python_full_file_name" --input-files "$SBOM_DIR/$sbom_ui_full_file_name" \
--output-file $SBOM_DIR/sbom.json
