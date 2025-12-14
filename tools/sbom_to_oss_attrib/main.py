# Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE
import asyncio
import logging.config
import os
from argparse import ArgumentParser, Namespace, BooleanOptionalAction
from logging import Logger
from pathlib import Path

import yaml

from sbom_to_oss_attrib.attribution_generator import OssAttributionGenerator, Attribution
from sbom_to_oss_attrib.attribution_output import AttributionTextFileBuilder

if __name__ == "__main__":
    parser: ArgumentParser = ArgumentParser(
        prog="OSS Attribution Generator",
        description="Generates an OSS Attribution file from a Software Bill of Materials (SBOM) file.",
    )
    parser.add_argument(
        "-i",
        "--input-file-path",
        type=str,
        required=True,
        help="Path of the CycloneDX SBOM file (.json) to generate an OSS Attribution for. Example: ./path/to/sbom.json",
    )
    parser.add_argument(
        "-o",
        "--output-file-path",
        type=str,
        required=False,
        help="Path of the OSS Attribution (.txt) file to generate. Example: ./path/to/oss_attribution.txt",
    )
    parser.add_argument(
        "--resolve-from-github",
        action=BooleanOptionalAction,
        default=True,
        required=False,
        help="Whether missing license information shall be resolved from GitHub. "
        "If set, requires a GitHub API token to be set as environment variable GITHUB_LICENSE_API_TOKEN (value: github_pat_<HEX...>).",
    )
    parser.add_argument(
        "--cache-github-responses",
        action=BooleanOptionalAction,
        default=True,
        required=False,
        help="Whether to cache (and read cached) responses from GitHub to avoid rate limiting.",
    )
    parser.add_argument(
        "--persist-cache",
        action=BooleanOptionalAction,
        default=True,
        required=False,
        help="Whether to persist cached responses from GitHub.",
    )
    parser.add_argument(
        "--cache-file-path",
        type=str,
        default=OssAttributionGenerator.CACHE_FILE_PATH_DEFAULT.name,
        required=False,
        help="Path of the file to store cached GitHub responses and load them from .",
    )
    namespace: Namespace = parser.parse_args()

    logging_config_path: Path = Path(__file__).parent / "logging.yaml"
    with logging_config_path.open() as f:
        logging.config.dictConfig(yaml.safe_load(f))

    logger: Logger = logging.getLogger(__name__)
    license_api_token: str | None = os.getenv("GITHUB_LICENSE_API_TOKEN")
    if namespace.resolve_from_github and license_api_token is None:
        logger.error(
            "--resolve-from-github requires environment variable GITHUB_LICENSE_API_TOKEN to be set (value: github_pat_<HEX...>)."
        )
        parser.print_help()
        exit(1)

    sbom_file_path: Path = Path(namespace.input_file_path).resolve()

    cache_github_responses: bool = namespace.cache_github_responses
    persist_cache: bool = namespace.persist_cache
    cache_file_path: Path = Path(namespace.cache_file_path).resolve()
    attribution_generator: OssAttributionGenerator = OssAttributionGenerator(
        github_api_token=license_api_token,
        cache_github_responses=cache_github_responses,
        persist_cache=persist_cache,
        cache_file_path=cache_file_path,
    )
    attribution: Attribution = asyncio.run(attribution_generator.build_attribution(sbom_file_path))

    attribution_text_file_builder: AttributionTextFileBuilder = AttributionTextFileBuilder()
    if namespace.output_file_path is not None:
        attribution_file_path: Path = Path(namespace.output_file_path).resolve(strict=True)
        attribution_text_file_builder.output_to_file(attribution, attribution_file_path)
    else:
        attribution_text: str = attribution_text_file_builder.generate_text(attribution)
        logger.info(attribution_text)
