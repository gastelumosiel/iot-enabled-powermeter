from django.shortcuts import render
import json
from django.http import JsonResponse
from mysite.mqtt import client as mqtt_client
from mysite.mqtt import message_topic, message_received, message_flag
from django.views.decorators.csrf import csrf_exempt
from .models import Messages
import datetime


# Create your views here.
@csrf_exempt
def publish_message(request):
    request_data = json.loads(request.body)
    rc, mid = mqtt_client.publish(request_data['topic'], request_data['msg'])
    return JsonResponse({'code':rc})

if message_flag is True:
    message_flag = False
    print("Saving message")
    if not isinstance(message_received, str):
        raise TypeError("Input must be a JSON string.")
    msg = json.loads(message_received)
    save_entry = Messages(esp_id = msg["esp_id"],
                          voltage = msg["voltage"],
                          current = msg["current"],
                          p_active = msg["p_active"],
                          p_reactive = msg["p_apparent"],
                          power_factor = msg["power_factor"],
                          phase = msg["phase"],
                          frequency = msg["frequency"],
                          date = datetime.datetime.fromtimestamp(msg["date"]))
    save_entry.save()