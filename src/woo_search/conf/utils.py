# ruff: noqa: F403,F405
import json
import logging
from collections.abc import Sequence
from functools import lru_cache
from pathlib import Path

from decouple import Undefined, undefined
from open_api_framework.conf.utils import config as _config

logger = logging.getLogger(__name__)


def config[T](option: str, default: T | Undefined = undefined, *args, **kwargs) -> T:
    """
    Pull a config parameter from the environment.

    Read the config variable ``option``. If it's optional, use the ``default`` value.
    Input is automatically cast to the correct type, where the type is derived from the
    default value if possible.

    Pass ``split=True`` to split the comma-separated input into a list.
    """
    kwargs["default"] = default
    return _config(option, *args, **kwargs)  # type: ignore


def mute_logging(config: dict) -> None:  # pragma: no cover
    """
    Disable (console) output from logging.

    :arg config: The logging config, typically the django LOGGING setting.
    """

    # set up the null handler for all loggers so that nothing gets emitted
    for name, logger in config["loggers"].items():
        if name == "flaky_tests":
            continue
        logger["handlers"] = ["null"]

    # some tooling logs to a logger which isn't defined, and that ends up in the root
    # logger -> add one so that we can mute that output too.
    config["loggers"].update(
        {
            "": {"handlers": ["null"], "level": "CRITICAL", "propagate": False},
        }
    )


@lru_cache(maxsize=1)
def load_indexable_file_types(base: Path) -> Sequence[str]:  # pragma: no cover
    """
    Load the JSON configuration file and extract relevant mime types.

    The shared file types configuration file documents all the supported file types
    and which of those can be indexed as full text in elastic search.
    """
    config_file = base / "shared" / "dotgithub" / "fileTypes.json"
    if not config_file.exists():
        logger.warning("file_does_not_exist", extra={"file": str(config_file)})
        return []

    with config_file.open() as infile:
        file_types = json.load(infile)

    return [
        file_type["mimeType"]
        for file_type in file_types
        if file_type.get("canBeIndexed")
    ]
