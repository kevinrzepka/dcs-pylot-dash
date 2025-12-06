#  Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
#  SPDX-License-Identifier: MIT
#  License-Filename: LICENSE
import sys
from pathlib import Path

import yaml

from sbom_to_oss_attrib.attribution_generator import OssAttributionGenerator

if __name__ == "__main__":
    logging_config_path: Path = Path(__file__).parent / "logging.yaml"
    with logging_config_path.open() as f:
        yaml.safe_load(f)
    _input_file: Path = Path(sys.argv[1])
    OssAttributionGenerator().parse_sbom(_input_file)  # TODO
