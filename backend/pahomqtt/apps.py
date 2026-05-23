from django.apps import AppConfig


class PahomqttConfig(AppConfig):
    name = 'pahomqtt'

    def ready(self):
        if getattr(self, '_mqtt_started', False):
            return

        import mysite.mqtt as mqtt
        mqtt.client.loop_start()
        self._mqtt_started = True
