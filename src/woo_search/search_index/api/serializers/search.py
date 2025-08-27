from django.utils.translation import gettext_lazy as _

from drf_polymorphic.serializers import PolymorphicSerializer
from rest_framework import serializers

from ...client import (
    InformationCategoryBucket,
    PublisherBucket,
    ResultTypeBucket,
    SearchResult,
    SearchResults,
    TopicBucket,
)
from ...constants import ResultTypeChoices, SortChoices
from ...typing import SearchParameters
from . import DocumentSerializer, PublicationSerializer, TopicSerializer


class SearchSerializer(serializers.Serializer):
    query = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text=_(
            "Filtering records based on the provided search term."
            " This search query is applied to the data within the following fields"
            " (with priority based on the order below):\n\n"
            "- `identifiers`\n"
            "- `officieleTitel`\n"
            "- `verkorteTitel`\n"
            "- `omschrijving`\n"
            "- `document content` **field only present in Document*\n"
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
    result_types = serializers.ListField(
        child=serializers.ChoiceField(choices=ResultTypeChoices.choices),
        help_text=_(
            "Specify to which document types the results should be limited. If left "
            "blank or an empty list is provided, all result types are included."
        ),
        default=list,
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
        help_text=_("Filter results registered before the given value."),
    )
    gepubliceerd_op_vanaf = serializers.DateTimeField(
        required=False,
        allow_null=True,
        default=None,
        help_text=_(
            "Filter results published after or on the given value. "
            "**Disclaimer**: this field will also search on the "
            "registration date of `Topics`."
        ),
    )
    gepubliceerd_op_tot = serializers.DateTimeField(
        required=False,
        allow_null=True,
        default=None,
        help_text=_(
            "Filter results published before the given value."
            "**Disclaimer**: this field will also search on the "
            "registration date of `Topics`."
        ),
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
        help_text=_("Filter results last modified before the given value."),
    )
    creatiedatum_vanaf = serializers.DateField(
        required=False,
        allow_null=True,
        default=None,
        help_text=_("Filter documents that were created after or on the given value."),
    )
    creatiedatum_tot_en_met = serializers.DateField(
        required=False,
        allow_null=True,
        default=None,
        help_text=_("Filter documents that were created before or on the given value."),
    )
    datum_begin_geldigheid_vanaf = serializers.DateTimeField(
        required=False,
        allow_null=True,
        default=None,
        help_text=_(
            "Filter publications that came into affect after or on the given value."
        ),
    )
    datum_begin_geldigheid_tot = serializers.DateTimeField(
        required=False,
        allow_null=True,
        default=None,
        help_text=_(
            "Filter publications that came into affect before the given value."
        ),
    )
    datum_einde_geldigheid_vanaf = serializers.DateTimeField(
        required=False,
        allow_null=True,
        default=None,
        help_text=_(
            "Filter publications that stopped being in effect after or on the "
            "given value."
        ),
    )
    datum_einde_geldigheid_tot = serializers.DateTimeField(
        required=False,
        allow_null=True,
        default=None,
        help_text=_(
            "Filter publications that stopped being in effect before the given value."
        ),
    )
    publishers = serializers.ListField(
        label=_("Publishers"),
        child=serializers.UUIDField(label=_("Publisher UUID")),
        default=list,
        allow_empty=True,
        help_text=_(
            "Filter results published by (one of) the given publishers' `uuid`."
        ),
    )
    informatie_categorieen = serializers.ListField(
        label=_("Information categories"),
        child=serializers.UUIDField(label=_("Category UUID")),
        default=list,
        allow_empty=True,
        help_text=_(
            "Filter results published by (one of) the given categories' `uuid`."
        ),
    )
    onderwerpen = serializers.ListField(
        label=_("Topics"),
        child=serializers.UUIDField(label=_("Topic UUID")),
        default=list,
        allow_empty=True,
        help_text=_("Filter results related to (one of) the given topics' `uuid`."),
    )

    def validate(self, attrs: SearchParameters) -> SearchParameters:
        # only the Document index has creatiedatum
        result_types = attrs["result_types"]
        creatiedatum_vanaf = attrs["creatiedatum_vanaf"]
        creatiedatum_tot_en_met = attrs["creatiedatum_tot_en_met"]

        match (result_types, creatiedatum_vanaf, creatiedatum_tot_en_met):
            # if filtering for document only, then any value for creatiedatum is okay
            case ([ResultTypeChoices.document.value], _, _):
                pass
            # not specifying any creatiedatum -> also okay
            case (_, None, None):
                pass
            # publication or all are selected and either creatiedatum vanaf or
            # creatiedatum_tot_en_met are set -> we can't filter that as it's not
            # indexed
            case _:
                assert creatiedatum_vanaf or creatiedatum_tot_en_met
                raise serializers.ValidationError(
                    _(
                        "You can only filter on creatiedatum when the result type is "
                        "restricted to 'document', as publications don't have this "
                        "field."
                    )
                )

        return attrs


class ResultTypeBucketSerializer(serializers.Serializer[ResultTypeBucket]):
    naam = serializers.ChoiceField(
        source="result_type",
        label=_("Result type / index name"),
        choices=ResultTypeChoices.choices,
        help_text=_("Indicates the type of record/index that was hit."),
    )
    count = serializers.IntegerField(
        label=_("Amount of hits"),
        min_value=0,
        help_text=_(
            "The amount of search results for this particular record type/index."
        ),
    )


class PublisherBucketSerializer(serializers.Serializer[PublisherBucket]):
    uuid = serializers.UUIDField(
        label=_("UUID"),
        help_text=_("Unique ID identifying the publisher in GPP-publicatiebank."),
    )
    naam = serializers.CharField(
        source="name",
        label=_("Name"),
        help_text=_("Name of the publishing organisation."),
    )
    count = serializers.IntegerField(
        label=_("Amount of hits"),
        min_value=0,
        help_text=_("The amount of search results published by this organisation."),
    )


class InformationCategoryBucketSerializer(
    serializers.Serializer[InformationCategoryBucket]
):
    uuid = serializers.UUIDField(
        label=_("UUID"),
        help_text=_(
            "Unique ID identifying the information category in GPP-publicatiebank."
        ),
    )
    naam = serializers.CharField(
        source="name",
        label=_("Name"),
        help_text=_("Name of the information category."),
    )
    count = serializers.IntegerField(
        label=_("Amount of hits"),
        min_value=0,
        help_text=_("The amount of search results sharing this category."),
    )


class TopicBucketSerializer(serializers.Serializer[TopicBucket]):
    uuid = serializers.UUIDField(
        label=_("UUID"),
        help_text=_("Unique ID identifying the topic in GPP-publicatiebank."),
    )
    officiele_titel = serializers.CharField(
        source="name",
        label=_("Official title"),
        help_text=_("Official title of the topic."),
    )
    count = serializers.IntegerField(
        label=_("Amount of hits"),
        min_value=0,
        help_text=_("The amount of search results sharing this topic."),
    )


class SearchFacetsSerializer(serializers.Serializer):
    result_types = ResultTypeBucketSerializer(source="result_type_buckets", many=True)
    publishers = PublisherBucketSerializer(source="publisher_buckets", many=True)
    informatie_categorieen = InformationCategoryBucketSerializer(
        source="information_category_buckets",
        many=True,
    )
    onderwerpen = TopicBucketSerializer(
        source="topic_buckets",
        many=True,
    )


class DocumentResultSerializer(serializers.Serializer[SearchResult]):
    record = DocumentSerializer(read_only=True)


class PublicationResultSerializer(serializers.Serializer[SearchResult]):
    record = PublicationSerializer(read_only=True)


class TopicResultSerializer(serializers.Serializer[SearchResult]):
    record = TopicSerializer(read_only=True)


class SearchResultsSerializer(PolymorphicSerializer):
    type = serializers.CharField()

    discriminator_field = "type"
    serializer_mapping = {
        "document": DocumentResultSerializer,
        "publication": PublicationResultSerializer,
        "topic": TopicResultSerializer,
    }


class SearchResponseSerializer(serializers.Serializer[SearchResults]):
    facets = SearchFacetsSerializer(source="*")
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
