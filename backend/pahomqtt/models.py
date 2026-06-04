from django.db import models
from django.conf import settings


class Device(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="devices", null=True, blank=True)
    device_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=120)
    icon = models.CharField(max_length=40, default="plug", blank=True)
    status = models.CharField(max_length=20, default="offline")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["device_id"]
        db_table = "Devices"

    def __str__(self):
        return f"{self.device_id} - {self.name}"


class UserCfeSettings(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cfe_settings")
    rate = models.CharField(max_length=40, default="domestic_1c")
    period_start = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "User_CFE_Settings"

    def __str__(self):
        return f"{self.user} - {self.rate}"


class ESPModule(models.Model):
    esp_id = models.CharField(max_length=100, unique=True)
    owner = models.CharField(max_length=120, blank=True, default="")

    class Meta:
        ordering = ["owner"]
        db_table = "ESP_Modules"


# Create your models here.
class Messages(models.Model):
    esp_id = models.CharField(max_length=100, blank=True, default="")
    voltage = models.FloatField()
    current = models.FloatField()
    p_active = models.FloatField()
    p_reactive = models.FloatField()
    p_apparent = models.FloatField()
    power_factor = models.FloatField()
    phase = models.FloatField()
    frequency = models.FloatField()
    date = models.DateTimeField()

    class Meta:
        ordering = ["date"]
        db_table = "data_modules"
