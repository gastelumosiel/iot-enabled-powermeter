# boot.py -- run on boot-up
try:
    import usocket as socket
except:
    import socket
import network
import esp
esp.osdebug(None)

import gc
gc.collect()

from config_storage import load_string, ssid_txt, pass_txt, fb_txt

first_boot = True
"""
continue_perm = load_string(fb_txt, default="(empty)")
if continue_perm == "continue":
    first_boot = False

if first_boot:
    ssid = 'ESP_001'
    password = '123456789'

    ap = network.WLAN(network.AP_IF)

    ap.active(True)
    ap.config(essid=ssid, password=password, authmode=network.AUTH_WPA_WPA2_PSK)

    while ap.active() == False:
        pass

    print('Connection successful')
    print(ap.ifconfig())
    from access_point import run
    run()
else:
    ssid = load_string(ssid_txt, default="(empty)")
    password = load_string(pass_txt, default="(empty)")"""
ssid = "S22UltradeRene"
password = "pwje3672"

import time
from umqttsimple import MQTTClient
import ubinascii
import machine
import micropython
import ntptime

mqtt_server = 'srv1612408.hstgr.cloud'

client_id = ubinascii.hexlify(machine.unique_id())
topic_sub = b'notification'
topic_pub = b'django/mqtt'

last_message = 0
message_interval = 1
counter = 0

station = network.WLAN(network.STA_IF)

station.active(True)
station.disconnect()   # clear any old state

# print(station.scan())

station.connect(ssid, password)

for _ in range(30):   # wait up to 15s
    if station.isconnected():
        break
    time.sleep(0.5)

if station.isconnected():
    print("Connected:", station.ifconfig())
else:
    print("Failed to connect")

print('Connection successful')
print(station.ifconfig())

ntptime.host = "pool.ntp.org"
ntptime.timeout = 2  # seconds

# Sync RTC with NTP
try:
    ntptime.settime()  # Sets RTC to UTC
    print("Time synchronized!")
except Exception as e:
    print("NTP sync failed:", e)

# Show current UTC time
print("UTC time:", time.localtime(), time.time())
