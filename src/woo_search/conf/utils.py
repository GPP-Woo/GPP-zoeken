import logging

from decouple import Csv, Undefined, undefined
from open_api_framework.conf.utils import config as _config
from sentry_sdk.integrations import DidNotEnable, django, redis

logger = logging.getLogger(__name__)


def config[T](option: str, default: T | Undefined = undefined, *args, **kwargs) -> T:
    """
    Pull a config parameter from the environment.

    Read the config variable ``option``. If it's optional, use the ``default`` value.
    Input is automatically cast to the correct type, where the type is derived from the
    default value if possible.

    Pass ``split=True`` to split the comma-separated input into a list.
    """
    if kwargs.get("split") is True:
        kwargs.pop("split")
        kwargs["cast"] = Csv()
        if default == []:
            default = ""  # type: ignore
    return _config(option, default=default, *args, **kwargs)  # type: ignore


def get_sentry_integrations() -> list:
    """
    Determine which Sentry SDK integrations to enable.
    """
    default = [
        django.DjangoIntegration(),
        redis.RedisIntegration(),
    ]
    extra = []

    try:
        from sentry_sdk.integrations import celery
    except DidNotEnable:  # happens if the celery import fails by the integration
        pass
    else:
        extra.append(celery.CeleryIntegration())

    return [*default, *extra]


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
