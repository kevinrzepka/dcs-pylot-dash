#  Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
#  SPDX-License-Identifier: MIT
#  License-Filename: LICENSE
import logging
import sys
from pathlib import Path

from sbom_to_oss_attrib.attribution import OssAttributionGenerator

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    _input_file: Path = Path(sys.argv[1])
    OssAttributionGenerator().parse_sbom(_input_file)  # TODO
