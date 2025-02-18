from django.urls import include, path
from django.views.generic import RedirectView

from drf_spectacular.views import SpectacularJSONAPIView, SpectacularRedocView
from rest_framework import routers

from woo_search.search_index.api.viewsets import (
    DocumentViewSet,
    PublicationViewSet,
    SearchViewSet,
)

app_name = "api"

router = routers.DefaultRouter(trailing_slash=False, use_regex_path=False)
router.include_format_suffixes = False

router.register("documenten", DocumentViewSet, basename="document")
router.register("publicaties", PublicationViewSet, basename="publication")
router.register("search", SearchViewSet, basename="search")

urlpatterns = [
    path("docs/", RedirectView.as_view(pattern_name="api:api-docs")),
    path(
        "v1/",
        include(
            [
                path(
                    "",
                    SpectacularJSONAPIView.as_view(schema=None),
                    name="api-schema-json",
                ),
                path(
                    "docs/",
                    SpectacularRedocView.as_view(url_name="api:api-schema-json"),
                    name="api-docs",
                ),
            ]
        ),
    ),
    path("v1/", include(router.urls)),
]
