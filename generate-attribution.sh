#!/usr/bin/env bash
#
# Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE
#

set -euo pipefail

SBOM_DIR='sboms/'
sbom_file="$SBOM_DIR/sbom.json"

# ensure regular venv is used
export PYTHONPATH=tools
uv run --no-sync tools/sbom_to_oss_attrib/main.py -i "$sbom_file" -o third_party_licenses.txt
unset PYTHONPATH
