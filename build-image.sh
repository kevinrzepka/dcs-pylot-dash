#!/usr/bin/env bash
#
# Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE
#

set -euo pipefail

# Build and tag the image with the git commit first, then tag it with 'latest'
commit_id=$(git rev-parse HEAD)
base_image_name=kevinrzepka/dcs-pylot-dash
full_image_name="$base_image_name:$commit_id"
sudo docker build --build-arg BUILD_DATE="$(date +"%Y-%m-%dT%H:%M:%S%z")" --build-arg BUILD_COMMIT="$(git rev-parse --short HEAD)" -t "$full_image_name" .
sudo docker tag "$full_image_name" "$base_image_name:latest"

# ensure no dev packages are in image
# first find some prod packages to ensure the mechanism works, then ensure the mechanism finds 0 dev packages
run_cmd="""
sudo docker run --rm -it --read-only \
--memory-swappiness=0 --security-opt=no-new-privileges --cap-drop all \
-m=1g --cpus=1 \
--entrypoint /bin/bash $full_image_name -c --
"""
# shellcheck disable=SC2090
$run_cmd 'find .venv -name fastapi' > tmp.txt
num_prod_packages=$(($(wc -l < tmp.txt)))
$run_cmd 'find .venv -name pytest' > tmp.txt
num_dev_packages=$(($(wc -l < tmp.txt)))
rm -f tmp.txt

if  [[ num_prod_packages -eq 0 ]]; then
  echo "fail: did not find any prod packages"
  exit 1
fi

if  [[ num_dev_packages -ne 0 ]]; then
  echo "fail: found dev packages"
  exit 1
fi

echo "successfully built image: $full_image_name"
