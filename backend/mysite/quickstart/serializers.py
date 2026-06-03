from django.contrib.auth.models import Group, User
from rest_framework import serializers
from pahomqtt.models import ESPModule, Messages


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ["url", "username", "email", "groups"]

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ["url", "name"]

class MessagesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Messages
        fields = ["esp_id", "voltage", "current", "p_active", "p_reactive", "p_apparent", "power_factor", "phase", "frequency", "date"]

class ESPSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ESPModule
        fields = ["esp_id", "owner"]