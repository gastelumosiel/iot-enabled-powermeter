from rest_framework import serializers
from module.models import Module


class ModuleSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    esp_id = serializers.CharField()
    voltage = serializers.FloatField()
    current = serializers.FloatField()
    p_active = serializers.FloatField()
    p_reactive = serializers.FloatField()
    p_apparent = serializers.FloatField()
    power_factor = serializers.FloatField()
    phase = serializers.FloatField()
    frequency = serializers.FloatField()
    date = serializers.DateTimeField()

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return Module.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """
        instance.esp_id = validated_data.get("esp_id", instance.esp_id)
        instance.voltage = validated_data.get("voltage", instance.voltage)
        instance.current = validated_data.get("current", instance.current)
        instance.p_active = validated_data.get("p_active", instance.p_active)
        instance.p_reactive = validated_data.get("p_reactive", instance.p_reactive)
        instance.p_apparent = validated_data.get("p_apparent", instance.p_apparent)
        instance.power_factor = validated_data.get("power_factor", instance.power_factor)
        instance.phase = validated_data.get("phase", instance.phase)
        instance.frequency = validated_data.get("frequency", instance.frequency)
        instance.date = validated_data.get("date", instance.date)

        instance.save()
        return instance