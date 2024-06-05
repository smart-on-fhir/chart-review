"""Utility methods"""

from enum import Enum, EnumMeta
from typing import Optional, Union
from collections.abc import Iterable
import logging
import json

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

    with open(path, "r") as f:
        return json.load(f, strict=False)


def write_json(path: str, data: dict | list, indent: Optional[int] = 4) -> None:
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

    with open(path, "r") as f:
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


def csv_map(csv_file: str) -> dict:
    """
    Get a simple map of csv file contents. For more complex handling, use pandas.
    :param csv_file: path to CSV file with rows "key,value"
    :return: dict {key:value}
    """
    res = {}
    with open(csv_file, "r") as fp:
        for line in fp.readlines():
            line = line.replace('"', "").strip()
            key, val = line.split(",")
            res[key] = val
    return res


###############################################################################
# Helper Functions: Pretty Print JSON, useful for Testing/Debugging
###############################################################################
def print_json(jsonable) -> None:
    """
    :param jsonable: dict or list of serializable object
    """
    if isinstance(jsonable, dict):
        print(json.dumps(jsonable, indent=4))
    elif isinstance(jsonable, list):
        print(json.dumps(jsonable, indent=4))
    else:
        print(jsonable)


def print_line(heading=None) -> None:
    """
    :param heading: optionally give a header to the line seperator
    """
    seperator = "##############################################################"
    if heading:
        print(f"\n{seperator}\n{heading}\n{seperator}")
    else:
        print(seperator)


###############################################################################
# Helper Functions: enum type smoothing
###############################################################################
def guard_str(object) -> str:
    if isinstance(object, Enum):
        return str(object.name)
    elif isinstance(object, EnumMeta):
        return str(object.name)
    elif isinstance(object, str):
        return object
    else:
        raise Exception(f"expected str|Enum but got {type(object)}")


def guard_iter(object) -> Iterable:
    if isinstance(object, Enum):
        return guard_iter(object.value)
    elif isinstance(object, EnumMeta):
        return guard_iter(object.value)
    elif isinstance(object, Iterable):
        return object
    else:
        raise Exception(f"expected Iterable|Enum but got {type(object)}")


def guard_in(entry, strict: Iterable):
    if entry in strict:
        return entry
    else:
        raise Exception(f"expected entry {entry} to be in {strict}")
