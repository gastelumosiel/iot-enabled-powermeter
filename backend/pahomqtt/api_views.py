from datetime import timedelta

from django.contrib.auth import authenticate, get_user_model
from django.core import signing
from django.db.models import Sum
from django.db.models.functions import TruncDate, TruncHour, TruncMonth
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from pahomqtt.models import Device, Messages
from pahomqtt.serializers import DeviceSerializer


TARIFFS = {
    "domestic_1": {
        "label": "Tarifa 1",
        "code": "1",
        "monthlyLimit": 250,
        "sourceUrl": "https://app.cfe.mx/Aplicaciones/CCFE/Tarifas/TarifasCRECasa/Tarifas/Tarifa1.aspx",
        "blocks": [
            {"key": "basic", "kwh": 75, "price": 1.12},
            {"key": "intermediate", "kwh": 65, "price": 1.36},
            {"key": "excess", "kwh": None, "price": 3.99},
        ],
    },
    "domestic_1a": {
        "label": "Tarifa 1A",
        "code": "1A",
        "monthlyLimit": 300,
        "sourceUrl": "https://app.cfe.mx/Aplicaciones/CCFE/Tarifas/TarifasCRECasa/Tarifas/Tarifa1A.aspx",
        "blocks": [
            {"key": "basic", "kwh": 100, "price": 1.01},
            {"key": "intermediate", "kwh": 50, "price": 1.17},
            {"key": "excess", "kwh": None, "price": 4.0},
        ],
    },
    "domestic_1b": {
        "label": "Tarifa 1B",
        "code": "1B",
        "monthlyLimit": 400,
        "sourceUrl": "https://app.cfe.mx/Aplicaciones/CCFE/Tarifas/TarifasCRECasa/Tarifas/Tarifa1B.aspx",
        "blocks": [
            {"key": "basic", "kwh": 125, "price": 1.01},
            {"key": "intermediate", "kwh": 100, "price": 1.21},
            {"key": "excess", "kwh": None, "price": 4.0},
        ],
    },
    "domestic_1c": {
        "label": "Tarifa 1C",
        "code": "1C",
        "monthlyLimit": 850,
        "sourceUrl": "https://app.cfe.mx/Aplicaciones/CCFE/Tarifas/TarifasCRECasa/Tarifas/Tarifa1C.aspx",
        "blocks": [
            {"key": "basic", "kwh": 150, "price": 1.01},
            {"key": "intermediate", "kwh": 150, "price": 1.21},
            {"key": "excess", "kwh": None, "price": 4.0},
        ],
    },
    "domestic_1d": {
        "label": "Tarifa 1D",
        "code": "1D",
        "monthlyLimit": 1000,
        "sourceUrl": "https://app.cfe.mx/Aplicaciones/CCFE/Tarifas/TarifasCRECasa/Tarifas/Tarifa1D.aspx",
        "blocks": [
            {"key": "basic", "kwh": 175, "price": 1.01},
            {"key": "intermediate", "kwh": 225, "price": 1.21},
            {"key": "excess", "kwh": None, "price": 4.0},
        ],
    },
    "domestic_1e": {
        "label": "Tarifa 1E",
        "code": "1E",
        "monthlyLimit": 2000,
        "sourceUrl": "https://app.cfe.mx/Aplicaciones/CCFE/Tarifas/TarifasCRECasa/Tarifas/Tarifa1E.aspx",
        "blocks": [
            {"key": "basic", "kwh": 300, "price": 0.98},
            {"key": "intermediate", "kwh": 450, "price": 1.16},
            {"key": "excess", "kwh": None, "price": 4.0},
        ],
    },
    "domestic_1f": {
        "label": "Tarifa 1F",
        "code": "1F",
        "monthlyLimit": 2500,
        "sourceUrl": "https://app.cfe.mx/Aplicaciones/CCFE/Tarifas/TarifasCRECasa/Tarifas/Tarifa1F.aspx",
        "blocks": [
            {"key": "basic", "kwh": 300, "price": 0.98},
            {"key": "intermediate", "kwh": 900, "price": 1.16},
            {"key": "excess", "kwh": None, "price": 4.0},
        ],
    },
}


def _frontend_user(user):
    name = user.get_full_name() or user.first_name or user.username
    return {"email": user.email, "name": name}


def _signed_token(user):
    return signing.dumps({"user_id": user.pk, "email": user.email}, salt="powerlytix-api")


def _registered_device_ids(user):
    if not user or not user.is_authenticated:
        return []
    return list(Device.objects.filter(owner=user).values_list("device_id", flat=True))


def _latest_readings(device_ids=None):
    readings = Messages.objects.order_by("esp_id", "-date")
    if device_ids is not None:
        readings = readings.filter(esp_id__in=device_ids)
    latest = {}
    for reading in readings:
        latest.setdefault(reading.esp_id, reading)
    return latest


def _energy_by_device(device_ids=None):
    rows = Messages.objects.values("esp_id").annotate(total=Sum("p_active"))
    if device_ids is not None:
        rows = rows.filter(esp_id__in=device_ids)
    return {row["esp_id"]: (row["total"] or 0) / 1000 for row in rows}


class DeviceViewSet(viewsets.ModelViewSet):
    serializer_class = DeviceSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "device_id"
    pagination_class = None

    def get_queryset(self):
        return Device.objects.filter(owner=self.request.user).order_by("device_id")

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        device_ids = _registered_device_ids(self.request.user)
        latest = _latest_readings(device_ids)
        for device in getattr(self, "_prefetched_devices", []):
            device.latest_reading = latest.get(device.device_id)
        context["energy_by_device"] = _energy_by_device(device_ids)
        return context

    def list(self, request, *args, **kwargs):
        queryset = list(self.get_queryset())
        latest = _latest_readings([device.device_id for device in queryset])
        for device in queryset:
            device.latest_reading = latest.get(device.device_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.latest_reading = _latest_readings([instance.device_id]).get(instance.device_id)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


@api_view(["POST"])
def register(request):
    User = get_user_model()
    email = request.data.get("email", "").strip().lower()
    password = request.data.get("password", "")
    name = request.data.get("name", "").strip()

    if not email or not password:
        return Response({"detail": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)

    user, created = User.objects.get_or_create(username=email, defaults={"email": email, "first_name": name})
    if not created and user.has_usable_password():
        return Response({"detail": "A user with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)

    user.email = email
    user.first_name = name or user.first_name
    user.set_password(password)
    user.save()

    return Response({"token": _signed_token(user), "user": _frontend_user(user)}, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def login(request):
    email = request.data.get("email", "").strip().lower()
    password = request.data.get("password", "")
    user = authenticate(username=email, password=password)

    if user is None:
        return Response({"detail": "Invalid email or password."}, status=status.HTTP_400_BAD_REQUEST)

    return Response({"token": _signed_token(user), "user": _frontend_user(user)})


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def profile(request):
    user = request.user
    devices_count = Device.objects.filter(owner=user).count()
    name = user.get_full_name() or user.first_name or user.username
    email = user.email
    created_at = user.date_joined

    return Response(
        {
            "name": name,
            "email": email,
            "devices_count": devices_count,
            "cfe_rate": "Domestica 1C",
            "bimonthly_limit_kwh": 280,
            "created_at": created_at,
        }
    )


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def analytics_history(request):
    range_key = request.query_params.get("range", "24h")
    trunc, delta, label_format = {
        "1h": (TruncHour, timedelta(hours=1), "%H:%M"),
        "8h": (TruncHour, timedelta(hours=8), "%H:%M"),
        "24h": (TruncHour, timedelta(hours=24), "%H:%M"),
        "7d": (TruncDate, timedelta(days=7), "%d %b"),
        "30d": (TruncDate, timedelta(days=30), "%d %b"),
        "3m": (TruncDate, timedelta(days=90), "%d %b"),
        "6m": (TruncMonth, timedelta(days=180), "%b %y"),
        "12m": (TruncMonth, timedelta(days=365), "%b %y"),
    }.get(range_key, (TruncHour, timedelta(hours=24), "%H:%M"))

    since = timezone.now() - delta
    device_ids = _registered_device_ids(request.user)
    rows = (
        Messages.objects.filter(date__gte=since, esp_id__in=device_ids)
        .annotate(bucket=trunc("date"))
        .values("bucket")
        .annotate(power=Sum("p_active"))
        .order_by("bucket")
    )
    data = [
        {"label": row["bucket"].strftime(label_format), "power": round(row["power"] or 0, 2)}
        for row in rows
        if row["bucket"]
    ]
    return Response(data)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def cfe_summary(request):
    accumulated = round(sum(_energy_by_device(_registered_device_ids(request.user)).values()), 2)
    configured_limit = 280
    usage_percent = round((accumulated / configured_limit) * 100, 2) if configured_limit else 0
    return Response(
        {
            "accumulated_kwh": accumulated,
            "configured_limit": configured_limit,
            "usage_percent": usage_percent,
            "remaining_kwh": round(max(configured_limit - accumulated, 0), 2),
        }
    )


@api_view(["GET"])
def cfe_tariffs(request):
    tariff = request.query_params.get("tariff", "domestic_1c")
    return Response(TARIFFS.get(tariff, TARIFFS["domestic_1c"]))
