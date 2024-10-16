import os
import warnings

os.environ.setdefault("IS_HTTPS", "no")
os.environ.setdefault("SECRET_KEY", "for-testing-purposes-only")
os.environ.setdefault("LOG_REQUESTS", "no")

from .base import *  # noqa isort:skip
from .utils import mute_logging  # noqa isort:skip

INSTALLED_APPS += [
    "django_extensions",
]

CACHES.update(
    {
        "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
        "axes": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"},
    }
)

# shut up logging
mute_logging(LOGGING)

# don't spend time on password hashing in tests/user factories
PASSWORD_HASHERS = ["django.contrib.auth.hashers.UnsaltedMD5PasswordHasher"]

ENVIRONMENT = "CI"

#
# Django-axes
#
AXES_BEHIND_REVERSE_PROXY = False

# THOU SHALT NOT USE NAIVE DATETIMES
warnings.filterwarnings(
    "error",
    r"DateTimeField .* received a naive datetime",
    RuntimeWarning,
    r"django\.db\.models\.fields",
)
