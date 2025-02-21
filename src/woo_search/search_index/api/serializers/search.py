from django.utils.translation import gettext_lazy as _

from drf_polymorphic.serializers import PolymorphicSerializer
from rest_framework import serializers

from ...client import SearchResult, SearchResults
from ...constants import ResultTypeChoices, SortChoices
from . import DocumentSerializer, PublicationSerializer


class SearchSerializer(serializers.Serializer):
    query = serializers.CharField(
        required=False,
        help_text=_(
            "Filtering records based on the provided search term."
            " This search query is applied to the data within the following fields"
            " (with priority based on the order below):\n\n"
            "- `identifier` **field only present in Document*\n"
            "- `officieleTitel`\n"
            "- `verkorteTitel`\n"
            "- `omschrijving`\n"
            "\nYou can use double quotes for exact matches and `AND`/`OR` syntax for "
            "complex queries."
        ),
        default="",
    )
    page = serializers.IntegerField(
        default=1, help_text=_("A page number within the paginated result set.")
    )
    page_size = serializers.IntegerField(
        default=10, help_text=_("Number of results to return per page.")
    )
    sort = serializers.ChoiceField(
        choices=SortChoices.choices,
        default=SortChoices.relevance,
    )
    result_type = serializers.ChoiceField(
        choices=ResultTypeChoices.choices,
        default=ResultTypeChoices.all,
        help_text=_("Which table(s) should be present in the returning body."),
    )


class DocumentResultSerializer(serializers.Serializer[SearchResult]):
    record = DocumentSerializer(read_only=True)


class PublicationResultSerializer(serializers.Serializer[SearchResult]):
    record = PublicationSerializer(read_only=True)


class SearchResultsSerializer(PolymorphicSerializer):
    type = serializers.CharField()

    discriminator_field = "type"
    serializer_mapping = {
        "document": DocumentResultSerializer,
        "publication": PublicationResultSerializer,
    }


class SearchResponseSerializer(serializers.Serializer[SearchResults]):
    count = serializers.IntegerField(source="total_count")
    next = serializers.SerializerMethodField(method_name="get_has_next")
    previous = serializers.SerializerMethodField(method_name="get_has_previous")
    results = SearchResultsSerializer(many=True)

    def get_has_next(self, instance: SearchResults) -> bool:
        page: int = self.context["page"]
        page_size: int = self.context["page_size"]
        return page * page_size < instance.total_count

    def get_has_previous(self, instance: SearchResults) -> bool:
        return self.context["page"] > 1
