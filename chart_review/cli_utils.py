"""Helper methods for CLI parsing."""

import argparse

from chart_review import cohort, config


def add_project_args(parser: argparse.ArgumentParser, is_global: bool = False) -> None:
    group = parser.add_argument_group("configuration")
    group.add_argument(
        "--project-dir",
        "-p",
        default=None if is_global else argparse.SUPPRESS,
        metavar="DIR",
        help=(
            "directory holding project files, "
            "like labelstudio-export.json (default: current dir)"
        ),
    )
    group.add_argument(
        "--config",
        "-c",
        default=None if is_global else argparse.SUPPRESS,
        metavar="PATH",
        help="config file (default: [project-dir]/config.yaml)",
    )


def get_cohort_reader(args: argparse.Namespace) -> cohort.CohortReader:
    proj_config = config.ProjectConfig(project_dir=args.project_dir, config_path=args.config)
    return cohort.CohortReader(proj_config)
