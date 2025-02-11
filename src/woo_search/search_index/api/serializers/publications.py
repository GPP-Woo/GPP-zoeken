from django.utils.translation import gettext_lazy as _

from rest_framework import serializers


class DocumentSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    publicatie = serializers.UUIDField(
        help_text=_("The unique identifier of the publication."),
    )
    publisher = serializers.UUIDField()
    identifier = serializers.CharField(
        help_text=_("The (primary) unique identifier."),
        max_length=255,
        required=False,
        allow_blank=True,
    )
    officiele_titel = serializers.CharField(max_length=255)
    verkorte_titel = serializers.CharField(
        max_length=255, required=False, allow_blank=True
    )
    omschrijving = serializers.CharField(required=False)
    creatiedatum = serializers.DateField(
        help_text=_(
            "Date when the (physical) document came into existence. Not to be confused "
            "with the registration timestamp of the document - the creation date is "
            "typically *before* the registration date."
        )
    )
    registratiedatum = serializers.DateTimeField()
    laatst_gewijzigd_datum = serializers.DateTimeField()
