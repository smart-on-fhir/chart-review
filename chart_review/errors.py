import sys
from typing import NoReturn

import rich.console

ERROR_INVALID_PROJECT = 10


def exit_for_invalid_project(msg: str) -> NoReturn:
    # Be very helpful - this is likely the user's first interaction with chart-review.
    stderr = rich.console.Console(stderr=True)
    stderr.print(msg, style="bold red", highlight=False)
    stderr.print()
    stderr.print("This does not appear to be a chart-review project folder.")
    stderr.print("See https://docs.smarthealthit.org/cumulus/chart-review/ to set up your project.")
    stderr.print()
    stderr.print("Or pass --help for usage info.")
    sys.exit(ERROR_INVALID_PROJECT)
