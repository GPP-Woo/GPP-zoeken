from rest_framework import serializers


class DocumentSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    publicatie = serializers.UUIDField()
    publisher = serializers.UUIDField()
    identifier = serializers.CharField(max_length=255, required=False)
    officiele_titel = serializers.CharField(max_length=255)
    verkorte_titel = serializers.CharField(max_length=255, required=False)
    omschrijving = serializers.CharField(required=False)
    creatiedatum = serializers.DateField()
    registratiedatum = serializers.DateTimeField()
    laatst_gewijzigd_datum = serializers.DateTimeField()
