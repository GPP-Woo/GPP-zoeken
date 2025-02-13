from django.utils.translation import gettext_lazy as _

from rest_framework import serializers


class PublisherSerializer(serializers.Serializer):
    uuid = serializers.CharField()
    naam = serializers.CharField(max_length=255)


class InformatieCategorieSerializer(serializers.Serializer):
    uuid = serializers.CharField()
    naam = serializers.CharField(max_length=255)


class DocumentSerializer(serializers.Serializer):
    uuid = serializers.CharField()
    publicatie = serializers.CharField(
        help_text=_("The unique identifier of the publication."),
    )
    publisher = PublisherSerializer(
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
    registratiedatum = serializers.DateTimeField()
    laatst_gewijzigd_datum = serializers.DateTimeField()


class PublicationSerializer(serializers.Serializer):
    uuid = serializers.CharField()
    publisher = PublisherSerializer(
        help_text=_("The organisation which publishes the publication.")
    )
    informatie_categorieen = InformatieCategorieSerializer(
        help_text=_(
            "The information categories clarify the kind of information present in the publication."
        ),
        required=True,
        many=True,
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
    registratiedatum = serializers.DateTimeField()
    laatst_gewijzigd_datum = serializers.DateTimeField()
