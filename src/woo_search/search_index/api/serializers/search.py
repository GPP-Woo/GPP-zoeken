from django.utils.translation import gettext_lazy as _

from drf_polymorphic.serializers import PolymorphicSerializer
from rest_framework import serializers

from ...constants import ResultTypeChoices, SortChoices
from . import DocumentSerializer, PublicationSerializer


class DocumentPolymorphicSerializer(serializers.Serializer):
    record = DocumentSerializer(read_only=True)


class PublicationPolymorphicSerializer(serializers.Serializer):
    record = PublicationSerializer(read_only=True)


class SearchSerializer(serializers.Serializer):
    query = serializers.CharField(
        required=False,
        help_text=_(
            "Filtering records based on the provided search term."
            " This field searches the data within the following fields"
            " (with priority based on the order below):\n\n"
            "- `identifier` **field only present in Document*\n"
            "- `officieleTitel`\n"
            "- `verkorteTitel`\n"
            "- `omschrijving`"
        ),
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

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        page = data["page"]
        page_size = data["page_size"]

        # Elasticsearch's pagination doesn't work with pages.
        # It instead has a `from` argument which states from which record
        # it will return values.
        data["page"] = page_size * (page - 1)

        return data


class SearchResponseResultsSerializer(PolymorphicSerializer):
    type = serializers.CharField()

    discriminator_field = "type"
    serializer_mapping = {
        "document": DocumentPolymorphicSerializer,
        "publication": PublicationPolymorphicSerializer,
    }


class SearchResponseSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    next = serializers.BooleanField(default=False)
    previous = serializers.BooleanField(default=False)
    results = SearchResponseResultsSerializer(many=True)
