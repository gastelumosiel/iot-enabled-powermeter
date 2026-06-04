# main.py -- put your code here!
from machine import Pin
import json

def sub_cb(topic, msg):
  print((topic, msg))
  if topic == b'notification' and msg == b'received':
    print('ESP received hello message')

def connect_and_subscribe():
  global client_id, mqtt_server, topic_sub, mqtt_user, mqtt_pass
  client = MQTTClient(client_id, mqtt_server)
  client.set_callback(sub_cb)
  client.connect()
  client.subscribe(topic_sub)
  print('Connected to %s MQTT broker, subscribed to %s topic' % (mqtt_server, topic_sub))
  return client

def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  time.sleep(10)
  machine.reset()

try:
  client = connect_and_subscribe()
except OSError as e:
  restart_and_reconnect()

onoff = True
led = Pin(10, Pin.OUT)
json_light = json.dumps({"esp_id":"ESP_001", "voltage":120, "current":0.1, "p_active":12, "p_reactive":0.1, "p_apparent":13, "power_factor":0.99, "phase":1, "frequency":60, "date":1780520078})
json_load = json.dumps({"esp_id":"ESP_001", "voltage":133, "current":15, "p_active":1300, "p_reactive":50, "p_apparent":1350, "power_factor":0.80, "phase":16, "frequency":61, "date":1780520079})

while True:
  try:
    client.check_msg()
    if (time.time() - last_message) > message_interval:
      msg = b'Hello #%d' % counter
      #client.publish(topic_pub, msg)
      last_message = time.time()
      counter += 1
      if onoff:
        led.on()
        # client.publish(topic_pub, "Led: On")
        client.publish(topic_pub, json_light)
      else:
        led.off()
        # client.publish(topic_pub, "Led: Off")
        client.publish(topic_pub, json_load)

      onoff = not onoff

  except OSError as e:
    restart_and_reconnect()