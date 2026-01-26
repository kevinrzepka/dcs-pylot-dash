#!/usr/bin/env bash


# Syncs all versions to the value in pyproject.toml
set -euo pipefail

project_version=$(uv version --short)
echo "Syncing all versions to: $project_version"

# update UI: dcs-pylot-dash-ui/package.json.
# 'pnpm version' exists but seems to hava an issue with -C. Also, showing the version gives an inconvenient output
package_json_path='dcs-pylot-dash-ui/package.json'
jq --arg v "$project_version" -r '.version |= $v' "$package_json_path" > "$package_json_path.tmp" && mv "$package_json_path.tmp" "$package_json_path"

effective_ui_version=$(jq -r '.version' "$package_json_path")
if [[ "$effective_ui_version" != "$project_version" ]]; then
  echo "UI version $effective_ui_version does not match project version $project_version"
  exit 1
fi

helm_chart_dir="deployment/dcs-pylot-dash"
helm_chart_path="$helm_chart_dir/Chart.yaml"
sed -i \
  -e "s/^version: .*/version: ${project_version}/" \
  -e "s/^appVersion: .*/appVersion: \"${project_version}\"/" \
  "$helm_chart_path"

# helm show chart does not include quotes around values
effective_helm_app_version=$(helm show chart "$helm_chart_dir" | grep -oP '(?<=appVersion: )\d\.\d.\d')
effective_helm_chart_version=$(helm show chart "$helm_chart_dir" | grep -oP '(?<=version: )\d\.\d.\d')

if [[ "$effective_helm_app_version" != "$effective_helm_chart_version" ]]; then
  echo "Helm chart app version $effective_helm_app_version does not match helm chart version $effective_helm_chart_version"
  exit 1
fi

if [[ "$effective_helm_chart_version" != "$project_version" ]]; then
  echo "Helm chart version $effective_helm_chart_version does not match project version $project_version"
  exit 1
fi

echo "Successfully synced versions to: $project_version"
