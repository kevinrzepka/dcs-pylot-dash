#  Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
#  SPDX-License-Identifier: MIT
#  License-Filename: LICENSE
import argparse
import dataclasses
import logging.config
import re
import sys
from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
from pathlib import Path
from re import Pattern
from typing import Any

import yaml


@dataclass
class CopyrightHeaderGeneratorSettings:
    num_lines: int = 3
    update_existing: bool = False
    copyright_pattern: str = r'(copyright.*?(\d{4}))'
    # if empty: All
    enabled_extensions: set[str] = dataclasses.field(default_factory=set)
    contents_dir_path: Path = Path(__file__).parent / "extensions"


class CopyrightHeaderGenerator:
    _LOGGER: logging.Logger = logging.getLogger(__name__)

    _settings: CopyrightHeaderGeneratorSettings
    # Key: File extension without dot, e.g., "py"
    _contents: dict[str, str]

    def __init__(self, settings: CopyrightHeaderGeneratorSettings):
        self._settings = settings
        self._contents = self._load_contents()

    def _load_contents(self) -> dict[str, str]:
        self._LOGGER.info(f"loading copyright contents from '{self._settings.contents_dir_path}'")
        contents: dict[str, str] = {}
        for extension_file_path in self._settings.contents_dir_path.iterdir():
            extension_name: str = extension_file_path.stem
            self._LOGGER.info(
                f"loading copyright content for extension '{extension_name}' from '{extension_file_path}'")
            contents[extension_name] = extension_file_path.read_text()
        return contents

    def update_file_content(self, file_path: Path) -> str | None:
        """
        Updates the content of a file by inserting or replacing copyright information.

        If the provided file does not exist, has no suffix, is empty, or the copyright
        information is not available for the file's suffix, the content will not be
        updated. The function also takes into account existing copyright lines and may
        update or insert content based on specific patterns and settings.

        Parameters:
            - file_path specifies the path to the file that should be updated.

        Behavior:
            - If the file starts with a shebang (#!), it will preserve the shebang at
              the top of the file.
            - Checks if an existing copyright line is present:
                - If the existing copyright fully matches the new line, no update is
                  made.
                - If the existing copyright partially matches and the setting
                  `update_existing` is disabled, no update is made.
            - If no copyright line exists, the new copyright content is inserted.
            - If an existing copyright line is found and the `update_existing` setting
              is enabled, the existing lines are replaced with the new copyright
              content.

        :param file_path: The path to the file to be updated.
        :type file_path: Path
        :return: Updated file content as a string if changes occur, or None if no changes
                 are made or the file cannot be updated.
        :rtype: str | None
        """
        if not file_path.exists() or len(file_path.suffix) == 0:
            self._LOGGER.debug(f"skipping file '{file_path}' because it does not exist or has no suffix")
            return None

        file_content: str = file_path.read_text()
        lines: list[str] = file_content.splitlines()
        if len(file_content) == 0 or len(lines) == 0:
            self._LOGGER.debug(f"skipping file '{file_path}' because it is empty")
            return None

        file_extension: str = file_path.suffix[1:]
        if len(self._settings.enabled_extensions) > 0 and file_extension not in self._settings.enabled_extensions:
            self._LOGGER.debug(
                f"skipping file '{file_path}' because its extension is not enabled (Enabled extensions are: {self._settings.enabled_extensions})")
            return None

        copyright_content: str | None = self._contents.get(file_extension)
        if copyright_content is None:
            self._LOGGER.warning(f"no copyright found for extension '{file_extension}', skipping file '{file_path}'")
            return None
        comment_char: str = copyright_content[0]
        copyright_content_first_line: str = copyright_content.splitlines()[0]
        copyright_pattern: Pattern = re.compile(self._settings.copyright_pattern)

        updated_file_content: str = ""
        search_offset: int = 0
        if lines[0].startswith("#!/"):
            self._LOGGER.info(f"shebang found at top of file '{file_path}': {lines[0]}, preserving it")
            search_offset = 1
            updated_file_content = lines[0] + "\n"

        existing_copyright_start_line_index: int = -1
        existing_copyright_end_line_index: int = -1
        for i in range(search_offset, self._settings.num_lines):
            line: str = lines[i]
            copyright_pattern_matches: list[Any] = copyright_pattern.findall(line.lower())
            if line.startswith(copyright_content_first_line):  # existing perfect match
                return None
            elif len(copyright_pattern_matches) > 0:
                if not self._settings.update_existing:  # existing partial match, no update -> nothing to do
                    return None
                existing_copyright_start_line_index = i
                for j in range(i, len(lines)):
                    if lines[j].startswith(comment_char):
                        existing_copyright_end_line_index = j
                    else:
                        self._LOGGER.info(
                            f"existing copyright of file {file_path} will be updated from line {i + 1} to line {j}")
                        break
                break

        for i in range(search_offset, existing_copyright_start_line_index):
            updated_file_content += lines[i] + "\n"

        updated_file_content += copyright_content
        for i in range(max(search_offset, existing_copyright_end_line_index + 1), len(lines)):
            updated_file_content += lines[i] + "\n"

        return updated_file_content


if __name__ == "__main__":
    parser: ArgumentParser = ArgumentParser(
        prog='Copyright Header Generator',
        description='Ensures copyright headers are present (and optionally updated) in source files.'
    )
    parser.add_argument("--num-lines", required=False, default=3, type=int,
                        help="Number of lines to scan for an existing copyright header")
    parser.add_argument("--extensions", required=False, type=str,
                        help="Comma-separated list of file extensions (without dot, e.g., 'py,sh') to handle")
    parser.add_argument("--update-existing", required=False, default=False, type=bool,
                        help="Whether existing notices shall be updated")
    parser.add_argument("files", nargs="+", help="Files to update")
    namespace: Namespace = parser.parse_args()
    settings: CopyrightHeaderGeneratorSettings = CopyrightHeaderGeneratorSettings()
    if namespace.num_lines is not None:
        settings.num_lines = int(namespace.num_lines)
    if namespace.update_existing is not None:
        settings.update_existing = bool(namespace.update_existing)
    if namespace.extensions is not None and len(namespace.extensions) > 0:
        settings.enabled_extensions = set(namespace.extensions.split(","))

    logging_config_path: Path = Path(__file__).parent / "logging.yaml"
    with logging_config_path.open() as f:
        logging.config.dictConfig(yaml.safe_load(f))

    print(settings)
    print(sys.argv)
    print(argparse.REMAINDER)

    copyright_header_generator: CopyrightHeaderGenerator = CopyrightHeaderGenerator(settings)
    for file_path in namespace.files:
        updated_file_content: str | None = copyright_header_generator.update_file_content(Path(file_path))
        if updated_file_content is not None:
            print(f"Updated file {file_path}")
