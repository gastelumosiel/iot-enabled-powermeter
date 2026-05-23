from django.shortcuts import render
import json
from django.http import JsonResponse
from mysite.mqtt import client as mqtt_client
from mysite.mqtt import message_topic, message_received
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
@csrf_exempt
def publish_message(request):
    request_data = json.loads(request.body)
    rc, mid = mqtt_client.publish(request_data['topic'], request_data['msg'])
    return JsonResponse({'code':rc})
#hello world 