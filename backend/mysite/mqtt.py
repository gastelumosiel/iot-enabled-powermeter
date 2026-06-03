import json
import datetime
import paho.mqtt.client as mqtt
from django.conf import settings
from django.db import close_old_connections
from pahomqtt.models import Messages


def on_connect(mqtt_client, userdata, flags, rc):
    if rc == 0:
        print('Connected successfully')
        mqtt_client.subscribe('django/mqtt')
    else:
        print('Bad connection. Code: ', rc)


def parse_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in ('true', '1', 'yes', 'y')
    return bool(value)


def on_message(mqtt_client, userdata, msg):
    payload = msg.payload.decode('utf-8', errors='ignore')
    print(f'Received message on topic: {msg.topic} with payload: {payload}')

    try:
        msg_data = json.loads(payload)
    except json.JSONDecodeError as exc:
        print('MQTT payload is not valid JSON:', exc)
        return

    try:
        close_old_connections()
        Messages.objects.create(
            esp_id=msg_data.get('esp_id', ''),
            voltage=float(msg_data.get('voltage', 0)),
            current=float(msg_data.get('current', 0)),
            p_active=float(msg_data.get('p_active', 0)),
            p_reactive=float(msg_data.get('p_reactive', 0)),
            p_apparent=float(msg_data.get('p_apparent', 0)),
            power_factor=float(msg_data.get('power_factor', 0)),
            phase=float(msg_data.get('phase', 0)),
            frequency=float(msg_data.get('frequency', False)),
            date=datetime.datetime.fromtimestamp(
                float(msg_data.get('date', datetime.datetime.now(datetime.timezone.utc).timestamp())),
                tz=datetime.timezone.utc,
            )
        )
        print('Saved MQTT message to DB.')
    except Exception as exc:
        print('Failed to save MQTT message to DB:', exc)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(settings.MQTT_USER, settings.MQTT_PASSWORD)
client.connect(
    host=settings.MQTT_SERVER,
    port=settings.MQTT_PORT,
    keepalive=settings.MQTT_KEEPALIVE
)
