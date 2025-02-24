from django.utils.translation import gettext_lazy as _

from drf_polymorphic.serializers import PolymorphicSerializer
from rest_framework import serializers

from ...client import SearchResult, SearchResults
from ...constants import ResultTypeChoices, SortChoices
from ...typing import SearchParameters
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
    registratiedatum_vanaf = serializers.DateTimeField(
        required=False,
        allow_null=True,
        default=None,
        help_text=_("Filter results registered after or on the given value."),
    )
    registratiedatum_tot = serializers.DateTimeField(
        required=False,
        allow_null=True,
        default=None,
        help_text=_("Filter results registered before or on the given value."),
    )
    laatst_gewijzigd_datum_vanaf = serializers.DateTimeField(
        required=False,
        allow_null=True,
        default=None,
        help_text=_("Filter results last modified after or on the given value."),
    )
    laatst_gewijzigd_datum_tot = serializers.DateTimeField(
        required=False,
        allow_null=True,
        default=None,
        help_text=_("Filter results last modified before or on the given value."),
    )
    creatiedatum_vanaf = serializers.DateField(
        required=False,
        allow_null=True,
        default=None,
        help_text=_("Filter documents that were created after or on the given value."),
    )
    creatiedatum_tot = serializers.DateField(
        required=False,
        allow_null=True,
        default=None,
        help_text=_("Filter documents that were created before or on the given value."),
    )

    def validate(self, attrs: SearchParameters) -> SearchParameters:
        # only the Document index has creatiedatum
        result_type = attrs["result_type"]
        creatiedatum_vanaf = attrs["creatiedatum_vanaf"]
        creatiedatum_tot = attrs["creatiedatum_tot"]

        match (result_type, creatiedatum_vanaf, creatiedatum_tot):
            # if filtering for document, then any value for creatiedatum is okay
            case (ResultTypeChoices.document.value, _, _):
                pass
            # not specifying any creatiedatum -> also okay
            case (_, None, None):
                pass
            # publication or all are selected and either creatiedatum vanaf or
            # creatiedatum_tot are set -> we can't filter that as it's not indexed
            case _:
                assert creatiedatum_vanaf or creatiedatum_tot
                raise serializers.ValidationError(
                    _(
                        "You can only filter on creatiedatum when the result type is "
                        "restricted to 'document', as publications don't have this field."
                    )
                )

        return attrs


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
