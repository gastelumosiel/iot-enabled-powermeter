from django.db import models

class ESPModule(models.Model):
    esp_id = models.CharField(max_length=100, unique=True)
    owner = models.CharField()

    class Meta:
        ordering = ["owner"]
        db_table = 'ESP_Modules'


# Create your models here.
class Messages(models.Model):
    esp_id = models.ForeignKey(ESPModule, on_delete=models.CASCADE)
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
        db_table = 'Sensor_Messages'