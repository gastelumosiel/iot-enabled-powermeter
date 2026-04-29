from django.shortcuts import render
from django.http import JsonResponse
from django.views import View


class Sum(View):
    def get(self, request):
        firstnum = int(request.GET.get('first',0))
        secondnum = int(request.GET.get('second',0))
        thirdnum = firstnum + secondnum
        return JsonResponse({'result':thirdnum})
    
class Subtraction(View):
    def get(self, request):
        firstnum = int(request.GET.get('first',0))
        secondnum = int(request.GET.get('second',0))
        thirdnum = firstnum - secondnum
        return JsonResponse({'result':thirdnum})
    
class Product(View):
    def get(self, request):
        firstnum = int(request.GET.get('first',0))
        secondnum = int(request.GET.get('second',0))
        thirdnum = firstnum * secondnum
        return JsonResponse({'result':thirdnum})
    
class Division(View):
    def get(self, request):
        firstnum = int(request.GET.get('first',0))
        secondnum = int(request.GET.get('second',0))
        thirdnum = firstnum / secondnum
        return JsonResponse({'result':thirdnum})