#!/usr/bin/env bash
#
# Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE
#

set -euo pipefail

SBOM_DIR='sboms/'
mkdir -p "$SBOM_DIR"

# generate full BOM
sbom_file="$SBOM_DIR/sbom.json"
# ensure regular venv is used
source .venv/bin/activate
uv sync --active --group cyclonedx
uv run --no-sync --active cyclonedx-py venv --gather-license-texts > "$sbom_file"
num_components_full=$(cat $sbom_file | jq -r '.components | length')

# generate prod BOM
env_name='prod'
venv_name=".venv-$env_name"
sbom_file="$SBOM_DIR/sbom-$env_name.json"
rm -rf "$venv_name"
uv venv "$venv_name"
source "$venv_name"/bin/activate
uv sync --active --group cyclonedx --no-group dev
uv run --no-sync --active cyclonedx-py venv --gather-license-texts > "$sbom_file"
rm -rf "$venv_name"
num_components_prod=$(cat $sbom_file | jq -r '.components | length')

# generate dev BOM
env_name='dev'
venv_name=".venv-$env_name"
sbom_file="$SBOM_DIR/sbom-$env_name.json"
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
[ "$num_components_dev" -ne "$num_components_prod" ]

# ensure regular venv is used again
source .venv/bin/activate


