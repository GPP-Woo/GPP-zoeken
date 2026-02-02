# ruff: noqa: F403,F405
import json
import logging
from collections.abc import Callable, Sequence
from functools import lru_cache
from pathlib import Path

from maykin_common.config import config as _config
from open_api_framework.conf.utils import config as _legacy_config

logger = logging.getLogger(__name__)


def wrap_config[T, **P](wrapped: Callable[P, T]):
    def inner(
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> T:
        help_text = kwargs.pop("help_text", "")
        group = kwargs.pop("group", "")

        # ensure the docs registration stuff is still happening
        option = args[0]
        assert isinstance(option, str)
        _legacy_kwargs = {**kwargs, "help_text": help_text, "group": group}
        _legacy_config(option, **_legacy_kwargs)  # type: ignore

        # can't handle the typing overlaods in a decorator...
        return wrapped(*args, **kwargs)

    return inner


config = wrap_config(_config)


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
