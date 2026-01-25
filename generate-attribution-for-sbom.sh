#!/usr/bin/env bash
#
# Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE
#

set -euo pipefail


print_usage() {
  echo "Usage: generate-attribution.sh [path-to-input-sbom_file] [path-to-output-txt-file]"
  exit 1
}

if [[ "$#" -ne 2 ]]; then
  print_usage
fi

sbom_file="$1"
output_file="$2"

# ensure regular venv is used
export PYTHONPATH=tools
uv run --no-sync tools/sbom_to_oss_attrib/main.py -i "$sbom_file" -o "$output_file"
unset PYTHONPATH
