#!/usr/bin/env bash

set -euo pipefail

commit_id=$(git rev-parse HEAD)

echo "starting build: ${commit_id}"

uv run pytest

./build-ui.sh
./build-image.sh

sudo trivy image --disable-telemetry kevinrzepka/dcs-pylot-dash:"$commit_id"

microk8s helm lint deployment/dcs-pylot-dash \
-n dcs-pylot-dash --debug \
--set image.tag="$commit_id"

echo "successfully finished build: ${commit_id}"
