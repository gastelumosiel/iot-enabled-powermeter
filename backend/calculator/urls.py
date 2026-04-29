from django.urls import path
from . import views

urlpatterns = [
    path('sum', views.Sum.as_view()),
    path('minus', views.Subtraction.as_view()),
    path('times', views.Product.as_view()),
    path('over', views.Division.as_view()),
]