from django.utils.translation import gettext_lazy as _

from rest_framework import serializers


class DocumentSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    publicatie = serializers.UUIDField(
        help_text=_("The unique identifier of the publication."),
    )
    publisher = serializers.UUIDField()
    identifier = serializers.CharField(
        help_text=_("De (primaire) unieke identificatie."),
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
            "De datum waarop het document ontstaan is. "
            "Niet te verwarren met de registratiedatum - "
            "de creatiedatum valt typisch voor de registratiedatum."
        )
    )
    registratiedatum = serializers.DateTimeField()
    laatst_gewijzigd_datum = serializers.DateTimeField()
