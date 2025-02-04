"""Utility methods"""

import json
import logging
from typing import Optional, Union

###############################################################################
# Helper Functions: read/write JSON and text
###############################################################################


def read_json(path: str) -> Union[dict, list[dict]]:
    """
    Reads json from a file
    :param path: filesystem path
    :return: message: coded message
    """
    logging.debug("read_json() %s", path)

    with open(path) as f:
        return json.load(f, strict=False)


def write_json(path: str, data: Union[dict, list], indent: Optional[int] = 4) -> None:
    """
    Writes data to the given path, in json format
    :param path: filesystem path
    :param data: the structure to write to disk
    :param indent: whether and how much to indent the output
    """
    logging.debug("write_json() %s", path)

    with open(path, "w") as f:
        json.dump(data, f, indent=indent)


def read_text(path: str) -> str:
    """
    Reads data from the given path, in text format
    :param path: (currently filesystem path)
    :return: message: coded message
    """
    logging.debug("read_text() %s", path)

    with open(path) as f:
        return f.read()


def write_text(path: str, text: str) -> None:
    """
    Writes data to the given path, in text format
    :param path: filesystem path
    :param text: the text to write to disk
    """
    logging.debug("write_text() %s", path)

    with open(path, "w") as f:
        f.write(text)
