# ruff: noqa: F403,F405
from functools import partial

from django.utils.functional import SimpleLazyObject
from django.utils.translation import gettext_lazy as _

from open_api_framework.conf.base import *  # noqa
from self_certifi import EXTRA_CERTS_ENVVAR as _EXTRA_CERTS_ENVVAR
from upgrade_check import UpgradeCheck, VersionRange
from vng_api_common.conf.api import BASE_REST_FRAMEWORK

from .utils import config, load_indexable_file_types

TIME_ZONE = "Europe/Amsterdam"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

INSTALLED_APPS = INSTALLED_APPS + [
    # External applications.
    "capture_tag",
    "hijack",
    "hijack.contrib.admin",
    "maykin_common",
    "timeline_logger",
    "drf_polymorphic",
    # Project applications.
    "woo_search.accounts",
    "woo_search.api",
    "woo_search.search_index",
    "woo_search.utils",
]

INSTALLED_APPS.remove("vng_api_common")
INSTALLED_APPS.remove("notifications_api_common")

MIDDLEWARE = MIDDLEWARE + [
    "hijack.middleware.HijackUserMiddleware",
    # NOTE: affects *all* requests, not just API calls. We can't subclass (yet) either
    # to modify the behaviour, since drf-spectacular has a bug in its `issubclass`
    # check, which is unreleased at the time of writing:
    # https://github.com/tfranzel/drf-spectacular/commit/71c7a04ee8921c01babb11fbe2938397a372dac7
    "djangorestframework_camel_case.middleware.CamelCaseMiddleWare",
]

# Remove unused/irrelevant middleware added by OAF
MIDDLEWARE.remove("corsheaders.middleware.CorsMiddleware")
MIDDLEWARE.remove("csp.contrib.rate_limiting.RateLimitedCSPMiddleware")

#
# SECURITY settings
#

CSRF_FAILURE_VIEW = "woo_search.accounts.views.csrf_failure"
LOGIN_URL = "admin:login"

#
# Custom settings
#
PROJECT_NAME = _("WOO Search")

# Displaying environment information
ENVIRONMENT_LABEL = config("ENVIRONMENT_LABEL", ENVIRONMENT)
ENVIRONMENT_BACKGROUND_COLOR = config("ENVIRONMENT_BACKGROUND_COLOR", "orange")
ENVIRONMENT_FOREGROUND_COLOR = config("ENVIRONMENT_FOREGROUND_COLOR", "black")
SHOW_ENVIRONMENT = config("SHOW_ENVIRONMENT", default=True)

# This setting is used by the csrf_failure view (accounts app).
# You can specify any path that should match the request.path
# Note: the LOGIN_URL Django setting is not used because you could have
# multiple login urls defined.
LOGIN_URLS = [reverse_lazy("admin:login")]

# Default (connection timeout, read timeout) for the requests library (in seconds)
REQUESTS_DEFAULT_TIMEOUT = (10, 30)

#
# Elasticsearch DSL custom settings
#
SEARCH_INDEX = {
    "HOST": config(
        "ELASTICSEARCH_HOST",
        default="",
        group="Elastic Search",
        help_text="Host where the ES cluster is deployed, e.g. https://es.example.com:9200",
    ),
    "USER": config(
        "ELASTICSEARCH_USER",
        default="",
        group="Elastic Search",
        help_text="Username for ES authentication.",
    ),
    "PASSWORD": config(
        "ELASTICSEARCH_PASSWORD",
        default="",
        group="Elastic Search",
        help_text="Password for ES authentication.",
    ),
    "TIMEOUT": config(
        "ELASTICSEARCH_TIMEOUT",
        default=60,
        group="Elastic Search",
        help_text="HTTP timeout for ES API interactions.",
    ),
    "CA_CERTS": config(
        "ELASTICSEARCH_CA_CERTS",
        default="",
        group="Elastic Search",
        help_text=(
            "Path to CA bundle (in PEM) format if self-signed certificates or "
            "a private CA are used to connect to the ES cluster. Alternatively, "
            f"if {_EXTRA_CERTS_ENVVAR} is defined, it will be used."
        ),
    ),
    # https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-refresh.html
    "REFRESH": config(
        "ELASTICSEARCH_REFRESH",
        default=False,
        group="Elastic Search",
        help_text=(
            "Refresh control for ES index, update, delete and bulk APIs. In "
            "production, you should leave this to the default of 'false'."
        ),
    ),
    "INDEXED_CHARS": config(
        "ELASTICSEARCH_INDEXED_CHARS",
        default=100000,
        group="Elastic Search",
        help_text=(
            "Attachment processor number of chars being used for "
            "extraction to prevent huge fields.\n"
            "- Use `-1` for no limit.\n"
            "- default and max `100000`."
        ),
    ),
    "MAX_INDEX_FILE_SIZE": config(
        "ELASTICSEARCH_MAX_INDEX_FILE_SIZE",
        default=99 / 1.33 * 1000 * 1000,  # 99mb (not mib)
        group="Elastic Search",
        help_text=(
            "The maximum file size (in bytes) that leads to full text indexing of the "
            "file content. For files larger than this limit, only the metadata is "
            "indexed. Keep in mind that Elastic Search must be configured "
            "appropriately to allow sufficiently large HTTP request body sizes."
        ),
    ),
}

SEARCH_INDEXABLE_FILE_TYPES = SimpleLazyObject(
    partial(load_indexable_file_types, BASE_DIR)
)

##############################
#                            #
# 3RD PARTY LIBRARY SETTINGS #
#                            #
##############################

#
# Django-Admin-Index
#
ADMIN_INDEX_SHOW_REMAINING_APPS = False
ADMIN_INDEX_SHOW_REMAINING_APPS_TO_SUPERUSERS = True
ADMIN_INDEX_DISPLAY_DROP_DOWN_MENU_CONDITION_FUNCTION = (
    "maykin_common.django_two_factor_auth.should_display_dropdown_menu"
)

#
# DJANGO-AXES
#
# The number of login attempts allowed before a record is created for the
# failed logins. Default: 3
AXES_FAILURE_LIMIT = 10
# If set, defines a period of inactivity after which old failed login attempts
# will be forgotten. Can be set to a python timedelta object or an integer. If
# an integer, will be interpreted as a number of hours. Default: None
AXES_COOLOFF_TIME = 1

#
# MAYKIN-2FA
#
# It uses django-two-factor-auth under the hood so you can configure
# those settings too.
#
# we run the admin site monkeypatch instead.
# Relying Party name for WebAuthn (hardware tokens)
TWO_FACTOR_WEBAUTHN_RP_NAME = f"WOO Search ({ENVIRONMENT})"


#
# DJANGO-HIJACK
#
HIJACK_PERMISSION_CHECK = "maykin_2fa.hijack.superusers_only_and_is_verified"
HIJACK_INSERT_BEFORE = (
    '<div class="content">'  # note that this only applies to the admin
)

# Subpath (optional)
# This environment variable can be configured during deployment.
SUBPATH = config("SUBPATH", default="")
if SUBPATH:
    SUBPATH = f"/{SUBPATH.strip('/')}"

#
# DJANGO REST FRAMEWORK
#

REST_FRAMEWORK = BASE_REST_FRAMEWORK.copy()
REST_FRAMEWORK["PAGE_SIZE"] = 10
REST_FRAMEWORK["DEFAULT_SCHEMA_CLASS"] = "drf_spectacular.openapi.AutoSchema"
REST_FRAMEWORK["DEFAULT_FILTER_BACKENDS"] = (
    "django_filters.rest_framework.DjangoFilterBackend",
)
REST_FRAMEWORK["DEFAULT_PAGINATION_CLASS"] = (
    "rest_framework.pagination.PageNumberPagination"
)
REST_FRAMEWORK["DEFAULT_PERMISSION_CLASSES"] = (
    "woo_search.api.permissions.TokenAuthPermission",
)
REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"] = (
    "woo_search.api.authorization.TokenAuthentication",
)
REST_FRAMEWORK["EXCEPTION_HANDLER"] = "rest_framework.views.exception_handler"

API_VERSION = "1.2.0"

SPECTACULAR_SETTINGS = {
    "SCHEMA_PATH_PREFIX": "/api/v1",
    "TITLE": "WOO Search",
    "DESCRIPTION": _(
        """
## Documentation

The WOO Search API provides an interface to the underlying Elastic Search index.

Through this API, it's possible to:

 * make published publications and documents available for search
 * schedule removal of publications and documents in case they're being retracted,
   making them no longer available for search
 * perform (faceted) search queries to find publications and/or documents

When a supported file type (files supported by [Apache Tika](https://tika.apache.org/1.10/formats.html))
is provided during indexing, then the text content of the document itself will be
included and search queries will include the content for possible hits.

**Authentication**

This API makes use of API Key authentication. All requests must have the
`Authorization: Token <token-value>` HTTP header, where `<token-value>` is
replaced with the actual API key. API keys are managed in the admin interface,
and you obtain one by contacting the administrator.

"""
    ),
    "POSTPROCESSING_HOOKS": [
        "drf_spectacular.hooks.postprocess_schema_enums",
        "drf_spectacular.contrib.djangorestframework_camel_case.camelize_serializer_fields",
        "maykin_common.drf_spectacular.hooks.remove_invalid_url_defaults",
    ],
    "SERVE_INCLUDE_SCHEMA": False,
    "CAMELIZE_NAMES": True,
    "TOS": None,
    "CONTACT": {
        "url": "https://github.com/GPP-Woo/GPP-zoeken",
        "email": "support@maykinmedia.nl",
    },
    "LICENSE": {
        "name": "EUPL",
        "url": "https://github.com/GPP-Woo/GPP-zoeken/blob/main/LICENSE.md",
    },
    "VERSION": API_VERSION,
    "TAGS": [],
    "EXTERNAL_DOCS": {
        "description": "Functional and technical documentation",
        "url": "https://gpp-zoeken.readthedocs.io/",
    },
    "ENUM_NAME_OVERRIDES": {
        "ResultTypesEnum": "woo_search.search_index.constants.ResultTypeChoices",
    },
}

#
# ZGW-CONSUMERS
#
ZGW_CONSUMERS_IGNORE_OAS_FIELDS = True

#
# CELERY - async task queue
#
# CELERY_BROKER_URL  defined in open-api-framework
# CELERY_RESULT_BACKEND  defined in open-api-framework

# Add (by default) 1 (soft), 5 (hard) minute timeouts to all Celery tasks.
CELERY_TASK_TIME_LIMIT = config("CELERY_TASK_HARD_TIME_LIMIT", default=5 * 60)  # hard
CELERY_TASK_SOFT_TIME_LIMIT = config(
    "CELERY_TASK_SOFT_TIME_LIMIT", default=1 * 60
)  # soft

CELERY_BEAT_SCHEDULE = {}

# Only ACK when the task has been executed. This prevents tasks from getting lost, with
# the drawback that tasks should be idempotent (if they execute partially, the mutations
# executed will be executed again!)
CELERY_TASK_ACKS_LATE = True

# ensure that no tasks are scheduled to a worker that may be running a very long-running
# operation, leading to idle workers and backed-up workers. The `-O fair` option
# *should* have the same effect...
CELERY_WORKER_PREFETCH_MULTIPLIER = 1

#
# SELF-CERTIFI
#

# don't assign to a setting, since self-certifi looks directly at the environment. We
# just hook things up here so they get included in the generated environment
# documentation.
config(
    _EXTRA_CERTS_ENVVAR,
    default="",
    help_text=(
        "Comma-separated list of additional paths containing certificates (in PEM "
        "format) to add to the trust store. Useful when working with self-signed "
        "certificates or private certificate authorities. This setting is ignored if "
        "'REQUESTS_CA_BUNDLE' is (already) defined."
    ),
)

#
# DJANGO-UPGRADE-CHECK
#
UPGRADE_CHECK_PATHS = {
    "2.0.0": UpgradeCheck(VersionRange(minimum="0.1.0")),
}
