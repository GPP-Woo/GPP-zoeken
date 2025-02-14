from rest_framework import serializers
from drf_polymorphic.serializers import PolymorphicSerializer


from woo_search.search_index.api.serializers import (
    DocumentSerializer,
    PublicationSerializer,
)
from woo_search.search_index.constants import SortChoices, ResultTypeChoices


class DocumentPolymorphicSerializer(serializers.Serializer):
    record = DocumentSerializer(read_only=True)


class PublicationPolymorphicSerializer(serializers.Serializer):
    record = PublicationSerializer(read_only=True)


class SearchSerializer(serializers.Serializer):
    query = serializers.CharField(required=False)
    page = serializers.IntegerField(default=1)
    page_size = serializers.IntegerField(
        default=10,
    )
    sort = serializers.ChoiceField(
        choices=SortChoices.choices,
        default=SortChoices.relevance,
    )
    result_type = serializers.ChoiceField(
        choices=ResultTypeChoices.choices,
        default=ResultTypeChoices.all,
    )

    def to_internal_value(self, data):
        page = data["page"]
        page_size = data["page_size"]

        # Elasticsearch's pagination doesn't work with pages.
        # It instead has a `from` argument which states from which record
        # it will return values.
        data["page"] = page_size * (page - 1)

        return super().to_internal_value(data)


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
