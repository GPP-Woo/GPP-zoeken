from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from ...typing import DocumentIndexType


class NestedPublisherSerializer(serializers.Serializer):
    uuid = serializers.CharField()
    naam = serializers.CharField(max_length=255)


class NestedInformationCategorySerializer(serializers.Serializer):
    uuid = serializers.CharField()
    naam = serializers.CharField(max_length=255)


class NestedTopicSerializer(serializers.Serializer):
    uuid = serializers.CharField()
    officiele_titel = serializers.CharField(max_length=255)


class DocumentSerializer(serializers.Serializer):
    uuid = serializers.CharField()
    publicatie = serializers.CharField(
        help_text=_("The unique identifier of the publication."),
    )
    informatie_categorieen = NestedInformationCategorySerializer(
        help_text=_(
            "The information categories present on the publication that the document "
            "belongs to."
        ),
        required=True,
        many=True,
    )
    onderwerpen = NestedTopicSerializer(
        help_text=_(
            "The topics present on the publication that the document belongs to. "
            "Topics capture socially relevant information that spans multiple "
            "publications. They can remain relevant for tens of years and exceed the "
            "life span of a single publication."
        ),
        required=False,
        many=True,
        allow_null=True,
        default=[],
    )
    publisher = NestedPublisherSerializer(
        help_text=_(
            "The organisation which publishes the publication of this document."
        )
    )
    identifier = serializers.CharField(
        help_text=_("The (primary) unique identifier."),
        max_length=255,
        required=False,
        allow_blank=True,
        default="",
    )
    officiele_titel = serializers.CharField(max_length=255)
    verkorte_titel = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        default="",
    )
    omschrijving = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )
    creatiedatum = serializers.DateField(
        help_text=_(
            "Date when the (physical) document came into existence. Not to be confused "
            "with the registration timestamp of the document - the creation date is "
            "typically *before* the registration date."
        )
    )
    registratiedatum = serializers.DateTimeField(
        help_text=_(
            "System timestamp reflecting when the document was registered in the "
            "GPP-Publicatiebank. Not to be confused with the creation date of the "
            "document, which is usually *before* the registration date."
        )
    )
    laatst_gewijzigd_datum = serializers.DateTimeField(
        help_text=_(
            "System timestamp reflecting when the document was last modified in the "
            "GPP-Publicatiebank."
        ),
    )


class DocumentIndexSerializer(DocumentSerializer):
    download_url = serializers.URLField(
        help_text=_(
            "The URL to where the document can be downloaded from to index the "
            "contents."
        ),
        write_only=True,
        required=False,
        allow_blank=True,
        default="",
    )
    file_size = serializers.IntegerField(
        help_text=_("The size of the document file on disk, in bytes."),
        write_only=True,
        required=False,
        allow_null=True,
        default=None,
    )

    def validate(self, attrs: DocumentIndexType):
        download_url = attrs["download_url"]
        file_size = attrs["file_size"]

        if download_url and file_size is None:
            raise serializers.ValidationError(
                {"file_size": _("Field is required when using `downloadUrl`.")}
            )

        return attrs


class PublicationSerializer(serializers.Serializer):
    uuid = serializers.CharField()
    publisher = NestedPublisherSerializer(
        help_text=_("The organisation which publishes the publication.")
    )
    informatie_categorieen = NestedInformationCategorySerializer(
        help_text=_(
            "The information categories clarify the kind of information present in "
            "the publication."
        ),
        required=True,
        many=True,
    )
    onderwerpen = NestedTopicSerializer(
        help_text=_(
            "Topics capture socially relevant information that spans multiple "
            "publications. They can remain relevant for tens of years and exceed the "
            "life span of a single publication."
        ),
        required=False,
        many=True,
        allow_null=True,
        default=[],
    )
    officiele_titel = serializers.CharField(max_length=255)
    verkorte_titel = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        default="",
    )
    omschrijving = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )
    registratiedatum = serializers.DateTimeField(
        help_text=_(
            "System timestamp reflecting when the publication was registered in the "
            "GPP-Publicatiebank."
        )
    )
    laatst_gewijzigd_datum = serializers.DateTimeField(
        help_text=_(
            "System timestamp reflecting when the publication was last modified in the "
            "GPP-Publicatiebank."
        ),
    )


class TopicSerializer(serializers.Serializer):
    uuid = serializers.CharField()
    officiele_titel = serializers.CharField(max_length=255)
    omschrijving = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )
    registratiedatum = serializers.DateTimeField(
        help_text=_(
            "System timestamp reflecting when the topic was registered in the "
            "GPP-Publicatiebank."
        )
    )
    laatst_gewijzigd_datum = serializers.DateTimeField(
        help_text=_(
            "System timestamp reflecting when the topic was last modified in the "
            "GPP-Publicatiebank."
        ),
    )
