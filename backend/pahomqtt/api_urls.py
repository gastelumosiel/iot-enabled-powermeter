from django.urls import path
from rest_framework.routers import DefaultRouter

from pahomqtt import api_views


router = DefaultRouter()
router.register("devices", api_views.DeviceViewSet, basename="device")

urlpatterns = [
    path("auth/login/", api_views.login, name="api-login"),
    path("auth/register/", api_views.register, name="api-register"),
    path("user/profile/", api_views.profile, name="api-profile"),
    path("analytics/history/", api_views.analytics_history, name="api-analytics-history"),
    path("cfe/summary/", api_views.cfe_summary, name="api-cfe-summary"),
    path("cfe/tariffs/", api_views.cfe_tariffs, name="api-cfe-tariffs"),
    *router.urls,
]
