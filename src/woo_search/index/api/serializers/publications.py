from rest_framework import serializers

from ...constants import DocumentActionTypeOptions, PublicationStatusOptions


class EigenaarSerializer(serializers.Serializer):
    weergave_naam = serializers.CharField()
    identifier = serializers.CharField(max_length=255)


class Documenthandelingen(serializers.Serializer):
    soort_handeling = serializers.ChoiceField(choices=DocumentActionTypeOptions)
    at_time = serializers.DateTimeField()
    was_associated_with = serializers.UUIDField()


class DocumentSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    identifier = serializers.CharField(max_length=255, required=False)
    publicatie = serializers.UUIDField()
    officiele_title = serializers.CharField(max_length=255)
    verkorte_title = serializers.CharField(max_length=255, required=False)
    omschrijving = serializers.CharField(max_length=None, required=False)
    creatiedatum = serializers.DateField()
    bestandsnaam = serializers.CharField(max_length=255)
    bestandsomvang = serializers.IntegerField()
    eigenaar = EigenaarSerializer()
    publicatiestatus = serializers.ChoiceField(choices=PublicationStatusOptions)
    registratiedatum = serializers.DateTimeField()
    laatst_gewijzigd_datum = serializers.DateTimeField()
    documenthandelingen = Documenthandelingen()
