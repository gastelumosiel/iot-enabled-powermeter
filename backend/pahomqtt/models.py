from django.db import models

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
    frequency = models.BooleanField(default=False)
    date = models.DateTimeField()

    class Meta:
        ordering = ["esp_id"]
        db_table = 'data_modules'