"""
Bootstrap the environment.

Load the secrets from the .env file and store them in the environment, so
they are available for Django settings initialization.

.. warning::

    do NOT import anything Django related here, as this file needs to be loaded
    before Django is initialized.
"""

import logging
import os
import tempfile
import threading
from pathlib import Path

from django.conf import settings

from dotenv import load_dotenv
from requests import Session
from self_certifi import (
    EXTRA_CERTS_ENVVAR,
    load_self_signed_certs as _load_self_signed_certs,
)

logger = logging.getLogger(__name__)

_SETUP_DONE = False

env_lock = threading.Lock()


def setup_env():
    global _SETUP_DONE

    if _SETUP_DONE:
        return

    # load the environment variables containing the secrets/config
    dotenv_path = Path(__file__).resolve().parent.parent.parent / ".env"
    load_dotenv(dotenv_path)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "woo_search.conf.dev")

    load_self_signed_certs()
    monkeypatch_requests()

    _SETUP_DONE = True


def load_self_signed_certs() -> None:  # pragma: no cover
    """
    Load self-signed/private CA bundles in an idempotent manner.

    self-certifi works by setting the ``REQUESTS_CA_BUNDLE`` envvar and errors out if
    this envvar is already set (as it conflicts with the way it operates). If the setup
    function runs multiple times, the envvar set by self-certifi would trip self-certifi
    in the second run.

    The guard clauses here ensure that loading the self-signed certs is done only once.
    """
    _certs_initialized = bool(os.environ.get("REQUESTS_CA_BUNDLE"))
    if _certs_initialized:
        return

    needs_extra_verify_certs = os.environ.get(EXTRA_CERTS_ENVVAR)
    if not needs_extra_verify_certs:
        return

    # don't block - if we can't acquire the lock, another thread already holds it and
    # will result in the (shared) os.environ being updated.
    if not env_lock.acquire(blocking=False):
        return

    try:
        # create target directory for resulting combined certificate file
        target_dir = tempfile.mkdtemp()
        _load_self_signed_certs(target_dir)
    finally:
        env_lock.release()


def monkeypatch_requests():
    """
    Add a default timeout for any requests calls.

    Clean up the code by removing the try/except if requests is installed, or removing
    the call to this function in setup_env if it isn't
    """
    if hasattr(Session, "_original_request"):
        logger.debug(
            "Session is already patched OR has an ``_original_request`` attribute."
        )
        return

    Session._original_request = Session.request  # type: ignore

    def new_request(self, *args, **kwargs):
        kwargs.setdefault("timeout", settings.REQUESTS_DEFAULT_TIMEOUT)
        return self._original_request(*args, **kwargs)

    Session.request = new_request
