#!/usr/bin/env bash
#
# Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE
#

set -euo pipefail

# build dist
pnpm -C ./dcs-pylot-dash-ui/ i --frozen-lockfile
pnpm -C ./dcs-pylot-dash-ui/ run build

# copy dist to src of API
ui_dest=src/dcs_pylot_dash/static/ui
rm -rf "$ui_dest"
mkdir -p "$ui_dest"
cp -r ./dcs-pylot-dash-ui/dist/dcs-pylot-dash-ui/browser/* "$ui_dest"
