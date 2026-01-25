#!/usr/bin/env bash
#
# Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE
#

set -euo pipefail

CYCLONEDX_CLI_IMAGE_DIGEST='4c42a0f3f24a62aee3c914f5a0c2f5cbf50cdf61093e250c3dd952c4efa012d0'

SBOM_GROUP='kevinrzepka'
SBOM_NAME='dcs-pylot-dash'
SBOM_VERSION='1.0.0'

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

ENV_NAME_PROD="prod"
ENV_NAME_DEV="dev"

# generate python prod SBOM
env_name="$ENV_NAME_PROD"
venv_name=".venv-$env_name"
sbom_python_prod_file_name="sbom-api-$env_name.json"
sbom_file="$SBOM_DIR/$sbom_python_prod_file_name"
rm -rf "$venv_name"
uv venv "$venv_name"
source "$venv_name"/bin/activate
uv sync --active --group cyclonedx --no-group dev
uv run --no-sync --active cyclonedx-py venv --gather-license-texts > "$sbom_file"
rm -rf "$venv_name"
num_components_prod=$(cat $sbom_file | jq -r '.components | length')

# generate python dev SBOM
env_name="$ENV_NAME_DEV"
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

# generate UI prod-only SBOM
sbom_ui_prod_file_name="sbom-ui-prod.json"
sbom_file="$SBOM_DIR/$sbom_ui_prod_file_name"
pnpm -C ./dcs-pylot-dash-ui exec cdxgen -t pnpm --no-install-deps --required-only --json-pretty -o ../"$sbom_file"

# generate UI full SBOM
sbom_ui_full_file_name="sbom-ui.json"
sbom_file="$SBOM_DIR/$sbom_ui_full_file_name"
pnpm -C ./dcs-pylot-dash-ui exec cdxgen -t pnpm --no-install-deps --json-pretty -o ../"$sbom_file"

# merge distributed SBOM (ui prod + python prod)
sudo docker run --rm -t -v ./"$SBOM_DIR"/:/"$SBOM_DIR"/ cyclonedx/cyclonedx-cli@sha256:"$CYCLONEDX_CLI_IMAGE_DIGEST" \
merge --group "$SBOM_GROUP" --name "$SBOM_NAME" --version "$SBOM_VERSION" \
--input-files "$SBOM_DIR/$sbom_python_prod_file_name" --input-files "$SBOM_DIR/$sbom_ui_prod_file_name" \
--output-file $SBOM_DIR/sbom-distributed.json

# merge full SBOM
sudo docker run --rm -t -v ./"$SBOM_DIR"/:/"$SBOM_DIR"/ cyclonedx/cyclonedx-cli@sha256:"$CYCLONEDX_CLI_IMAGE_DIGEST" \
merge --group "$SBOM_GROUP" --name "$SBOM_NAME" --version "$SBOM_VERSION" \
--input-files "$SBOM_DIR/$sbom_python_full_file_name" --input-files "$SBOM_DIR/$sbom_ui_full_file_name" \
--output-file $SBOM_DIR/sbom.json

echo "Successfully generated SBOMs"
