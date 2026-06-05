from rest_framework import serializers
from django.utils import timezone

from pahomqtt.models import Device, Messages


class DeviceSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="device_id", read_only=True)
    timestamp = serializers.DateTimeField(read_only=True)
    vrms = serializers.FloatField(read_only=True)
    irms = serializers.FloatField(read_only=True)
    active_power = serializers.FloatField(read_only=True)
    reactive_power = serializers.FloatField(read_only=True)
    apparent_power = serializers.FloatField(read_only=True)
    power_factor = serializers.FloatField(read_only=True)
    phase = serializers.FloatField(read_only=True)
    frequency = serializers.FloatField(read_only=True)
    energy_kwh = serializers.FloatField(read_only=True)

    class Meta:
        model = Device
        fields = [
            "id",
            "device_id",
            "name",
            "icon",
            "timestamp",
            "vrms",
            "irms",
            "active_power",
            "reactive_power",
            "apparent_power",
            "power_factor",
            "phase",
            "frequency",
            "energy_kwh",
            "status",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        reading = getattr(instance, "latest_reading", None)
        offline_after = self.context.get("offline_after_seconds", 5 * 60)

        if reading is not None:
            age_seconds = (timezone.now() - reading.date).total_seconds()
            status = "online" if age_seconds <= offline_after else "offline"
            if status == "online" and reading.p_active <= 0.2:
                status = "idle"
            data.update(
                {
                    "timestamp": reading.date,
                    "vrms": reading.voltage,
                    "irms": reading.current,
                    "active_power": reading.p_active,
                    "reactive_power": reading.p_reactive,
                    "apparent_power": reading.p_apparent,
                    "power_factor": reading.power_factor,
                    "phase": reading.phase,
                    "frequency": reading.frequency,
                    "energy_kwh": round(
                        self.context.get("energy_by_device", {}).get(instance.device_id, 0),
                        3,
                    ),
                    "status": status,
                }
            )
        else:
            data.update(
                {
                    "timestamp": instance.updated_at,
                    "vrms": 0,
                    "irms": 0,
                    "active_power": 0,
                    "reactive_power": 0,
                    "apparent_power": 0,
                    "power_factor": 0,
                    "phase": 0,
                    "frequency": 0,
                    "energy_kwh": 0,
                }
            )

        return data


class HistoryPointSerializer(serializers.Serializer):
    label = serializers.CharField()
    power = serializers.FloatField()
    value = serializers.FloatField(required=False)
