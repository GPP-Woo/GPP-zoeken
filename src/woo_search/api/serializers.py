from rest_framework import serializers


class CeleryTaskIdSerializer(serializers.Serializer):
    task_id = serializers.UUIDField()
