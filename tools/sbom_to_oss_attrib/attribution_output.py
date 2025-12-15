# Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE
from pathlib import Path

from sbom_to_oss_attrib.attribution_generator import Attribution, AttributionEntry
from sbom_to_oss_attrib.utils import StringUtils


class AttributionTextFileBuilder:
    SEPARATOR_CHAR = "-"
    SEPARATOR_LENGTH = 80

    _output_versions: bool = False

    def __init__(self, output_versions: bool = False):
        self._output_versions = output_versions

    def output_to_file(self, attribution: Attribution, output_file: Path):
        text = self.generate_text(attribution)
        if output_file.exists():
            output_file.unlink()
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.touch()
        output_file.write_text(text)

    def generate_text(self, attribution: Attribution) -> str:
        entries_by_name: list[AttributionEntry] = list(attribution.entries)
        entries_by_name.sort(key=lambda e: e.name.lower())
        text: str = ""
        for entry in entries_by_name:
            text += self.generate_text_for_entry(entry)
        return text

    def generate_text_for_entry(self, entry: AttributionEntry) -> str:
        text: str = f"\n{self.SEPARATOR_CHAR * self.SEPARATOR_LENGTH}\n"
        text += f"Name:                       {entry.name}\n" f"SPDX-License-Identifier:    {entry.license_id}\n"
        if self._output_versions and StringUtils.is_not_empty(entry.version):
            text += f"Version:                    {entry.version}\n"
        if StringUtils.is_not_empty(entry.homepage):
            text += f"Homepage:                   {entry.homepage}\n"
        if StringUtils.is_not_empty(entry.authors):
            text += f"Authors:                    {entry.authors}\n"
        if StringUtils.is_not_empty(entry.license_text):
            text += "License text:\n" "\n" f"{entry.license_text}\n\n"
        return text
