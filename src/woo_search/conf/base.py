from textwrap import dedent

from django.utils.translation import gettext_lazy as _
from elasticsearch_dsl import connections

from open_api_framework.conf.base import *  # noqa
from vng_api_common.conf.api import BASE_REST_FRAMEWORK

from .utils import config

init_sentry()


TIME_ZONE = "Europe/Amsterdam"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

INSTALLED_APPS.remove("django.contrib.sites")

INSTALLED_APPS = INSTALLED_APPS + [
    # External applications.
    "capture_tag",
    "hijack",
    "hijack.contrib.admin",
    "timeline_logger",
    # Project applications.
    "woo_search.accounts",
    "woo_search.api",
    "woo_search.logging",
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

#
# SECURITY settings
#

CSRF_FAILURE_VIEW = "woo_search.accounts.views.csrf_failure"

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
ELASTICSEARCH_DSL_HOSTS = config("ELASTICSEARCH_DSL_HOSTS", default=["http://localhost:9200/"])
ELASTICSEARCH_DSL_TIMEOUT = config("ELASTICSEARCH_DSL_TIMEOUT", default=60)

ELASTICSEARCH_USER = config("ELASTICSEARCH_USER", default="elastic")
ELASTICSEARCH_SECRET = config("ELASTICSEARCH_SECRET", default="insecure-elastic")

assert ELASTICSEARCH_DSL_HOSTS
assert ELASTICSEARCH_DSL_TIMEOUT

if ELASTICSEARCH_USER and ELASTICSEARCH_SECRET:
    connections.create_connection(
        hosts=ELASTICSEARCH_DSL_HOSTS,
        timeout=ELASTICSEARCH_DSL_TIMEOUT,
        http_auth=(ELASTICSEARCH_USER, ELASTICSEARCH_SECRET)
    )
else:
    connections.create_connection(
        hosts=ELASTICSEARCH_DSL_HOSTS,
        timeout=ELASTICSEARCH_DSL_TIMEOUT,
    )

assert connections.get_connection().cluster.health()

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
    "woo_search.utils.django_two_factor_auth.should_display_dropdown_menu"
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
REST_FRAMEWORK["EXCEPTION_HANDLER"] = "rest_framework.views.exception_handler"

SPECTACULAR_SETTINGS = {
    "SCHEMA_PATH_PREFIX": "/api/v1",
    "TITLE": "WOO Search",
    "DESCRIPTION": dedent(
        """
        The WOO Search API provides an interface to the underlying Elastic Search index.

        Through this API, it's possible to add published documents to the API, or to
        schedule removal of a publication in case it's being retracted. When a supported
        file type is provided, the content of the document itself will also be indexed.

        **Authentication**

        TODO - not implemented yet!

        This API makes use of API Key authentication. All requests must have the
        `Authorization: token <token-value>` HTTP header, where `<token-value>` is
        replaced with the actual API key. API keys are managed in the admin interface,
        and you obtain one by contacting the administrator(s).

        **Audit logging**

        TODO - not implemented yet!

        Audit logging is done at the request level. Clients must send the respective
        HTTP request headers, and the values in those headers will be recorded in the
        audit logs.
    """
    ),
    "POSTPROCESSING_HOOKS": [
        "drf_spectacular.hooks.postprocess_schema_enums",
        "drf_spectacular.contrib.djangorestframework_camel_case.camelize_serializer_fields",
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
    "VERSION": "0.1.0",
    "TAGS": [],
    "EXTERNAL_DOCS": {
        "description": "Functional and technical documentation",
        "url": "https://woo-search.readthedocs.io/",
    },
}

#
# ZGW-CONSUMERS
#
ZGW_CONSUMERS_IGNORE_OAS_FIELDS = True
