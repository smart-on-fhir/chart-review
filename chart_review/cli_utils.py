"""Helper methods for CLI parsing."""

import argparse


def add_project_args(parser: argparse.ArgumentParser) -> None:
    group = parser.add_argument_group("configuration")
    group.add_argument(
        "--project-dir",
        default=".",
        metavar="DIR",
        help=(
            "Directory holding project files, "
            "like labelstudio-export.json (default: current dir)"
        ),
    )
    group.add_argument(
        "--config", "-c", metavar="PATH", help="Config file (default: [project-dir]/config.yaml)"
    )
