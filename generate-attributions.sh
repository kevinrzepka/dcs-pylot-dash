#!/usr/bin/env bash
#
# Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE
#

set -euo pipefail

if [[ -z ${GITHUB_LICENSE_API_TOKEN+u} ]]; then
  echo 'Environment variable "GITHUB_LICENSE_API_TOKEN" must be set. Value example: github_pat_<HEX...>'
  exit 1
fi

./generate-attribution-for-sbom.sh sboms/sbom-distributed.json third_party_licenses_distributed.txt
./generate-attribution-for-sbom.sh sboms/sbom.json third_party_licenses.txt
