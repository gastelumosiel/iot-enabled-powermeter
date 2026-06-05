from datetime import datetime, time, timedelta

from django.contrib.auth import authenticate, get_user_model
from django.core import signing
from django.db.models import Min
from django.utils.dateparse import parse_date
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from pahomqtt.models import Device, Messages, UserCfeSettings
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


def _user_cfe_settings(user):
    settings, _ = UserCfeSettings.objects.get_or_create(user=user)
    if settings.rate not in TARIFFS:
        settings.rate = "domestic_1c"
        settings.save(update_fields=["rate", "updated_at"])
    return settings


def _cfe_settings_payload(settings):
    tariff = TARIFFS.get(settings.rate, TARIFFS["domestic_1c"])
    return {
        "rate": settings.rate,
        "period_start": settings.period_start,
        "label": tariff["label"],
        "monthly_limit": tariff["monthlyLimit"],
        "bimonthly_limit_kwh": tariff["monthlyLimit"] * 2,
    }


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


def _energy_by_device(device_ids=None, since=None, until=None):
    readings = Messages.objects.order_by("esp_id", "date")
    if device_ids is not None:
        readings = readings.filter(esp_id__in=device_ids)
    if since is not None:
        readings = readings.filter(date__gte=since)
    if until is not None:
        readings = readings.filter(date__lt=until)

    energy = {}
    previous_by_device = {}
    max_gap_seconds = 5 * 60

    for reading in readings:
        previous = previous_by_device.get(reading.esp_id)
        if previous is not None:
            elapsed_seconds = (reading.date - previous.date).total_seconds()
            if 0 < elapsed_seconds <= max_gap_seconds:
                average_power_watts = (previous.p_active + reading.p_active) / 2
                energy[reading.esp_id] = energy.get(reading.esp_id, 0) + (average_power_watts * elapsed_seconds) / 3600000

        previous_by_device[reading.esp_id] = reading

    return energy


def _parse_local_date_boundary(value, default=None, end_of_day=False):
    parsed = parse_date(value or "")
    if parsed is None:
        return default

    boundary_time = time.max if end_of_day else time.min
    local_value = timezone.make_aware(datetime.combine(parsed, boundary_time), timezone.get_current_timezone())
    return local_value


def _history_bucket(value, range_key):
    local_value = timezone.localtime(value)
    if range_key in ("1h", "8h"):
        return local_value.replace(second=0, microsecond=0)
    if range_key == "24h":
        return local_value.replace(minute=0, second=0, microsecond=0)
    if range_key == "7d":
        return local_value.replace(minute=0, second=0, microsecond=0)
    if range_key in ("30d", "3m"):
        return local_value.replace(hour=0, minute=0, second=0, microsecond=0)
    return local_value.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


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
    cfe_settings = _cfe_settings_payload(_user_cfe_settings(user))

    return Response(
        {
            "name": name,
            "email": email,
            "devices_count": devices_count,
            "cfe_rate": cfe_settings["label"],
            "cfe_rate_code": cfe_settings["rate"],
            "cfe_period_start": cfe_settings["period_start"],
            "bimonthly_limit_kwh": cfe_settings["bimonthly_limit_kwh"],
            "created_at": created_at,
        }
    )


@api_view(["GET", "PATCH"])
@permission_classes([permissions.IsAuthenticated])
def cfe_settings(request):
    settings = _user_cfe_settings(request.user)

    if request.method == "PATCH":
        rate = request.data.get("rate")
        period_start = request.data.get("period_start")

        if rate is not None:
            if rate not in TARIFFS:
                return Response({"detail": "Unsupported CFE rate."}, status=status.HTTP_400_BAD_REQUEST)
            settings.rate = rate

        if "period_start" in request.data:
            parsed_period_start = parse_date(period_start or "")
            if period_start and parsed_period_start is None:
                return Response({"detail": "period_start must be YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)
            settings.period_start = parsed_period_start

        settings.save()

    return Response(_cfe_settings_payload(settings))


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def analytics_history(request):
    range_key = request.query_params.get("range", "24h")
    parameter = request.query_params.get("parameter", "active_power")
    field_by_parameter = {
        "active_power": "p_active",
        "reactive_power": "p_reactive",
        "apparent_power": "p_apparent",
        "vrms": "voltage",
        "irms": "current",
        "power_factor": "power_factor",
        "frequency": "frequency",
        "phase": "phase",
    }
    metric_field = field_by_parameter.get(parameter, "p_active")
    delta, label_format = {
        "1h": (timedelta(hours=1), "%H:%M"),
        "8h": (timedelta(hours=8), "%H:%M"),
        "24h": (timedelta(hours=24), "%H:%M"),
        "7d": (timedelta(days=7), "%d %b %H:%M"),
        "30d": (timedelta(days=30), "%d %b"),
        "3m": (timedelta(days=90), "%d %b"),
        "6m": (timedelta(days=180), "%b %y"),
        "12m": (timedelta(days=365), "%b %y"),
    }.get(range_key, (timedelta(hours=24), "%H:%M"))

    since = timezone.now() - delta
    owned_device_ids = _registered_device_ids(request.user)
    requested_device_ids = [
        device_id.strip()
        for device_id in request.query_params.get("device_ids", "").split(",")
        if device_id.strip()
    ]
    device_ids = [device_id for device_id in requested_device_ids if device_id in owned_device_ids] or owned_device_ids
    devices = Device.objects.filter(owner=request.user, device_id__in=device_ids)
    device_names = {device.device_id: device.name for device in devices}
    readings = (
        Messages.objects.filter(date__gte=since, esp_id__in=device_ids)
        .only("esp_id", "date", metric_field)
        .order_by("esp_id", "date")
    )
    series_by_device = {
        device_id: {"id": device_id, "name": device_names.get(device_id, device_id), "points": []}
        for device_id in device_ids
    }
    bucket_totals = {}

    for reading in readings:
        bucket = _history_bucket(reading.date, range_key)
        value = getattr(reading, metric_field, None)
        if value is None:
            continue

        key = (reading.esp_id, bucket)
        total, count = bucket_totals.get(key, (0, 0))
        bucket_totals[key] = (total + float(value), count + 1)

    for (device_id, bucket), (total, count) in bucket_totals.items():
        value = round(total / max(count, 1), 2)
        series_by_device.setdefault(
            device_id,
            {"id": device_id, "name": device_names.get(device_id, device_id), "points": []},
        )["points"].append(
            {
                "label": bucket.strftime(label_format),
                "timestamp": bucket,
                "value": value,
                "power": value,
            }
        )

    for series in series_by_device.values():
        series["points"].sort(key=lambda point: point["timestamp"])

    return Response([series for series in series_by_device.values() if series["points"]])


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def analytics_availability(request):
    owned_device_ids = _registered_device_ids(request.user)
    requested_device_ids = [
        device_id.strip()
        for device_id in request.query_params.get("device_ids", "").split(",")
        if device_id.strip()
    ]
    device_ids = [device_id for device_id in requested_device_ids if device_id in owned_device_ids] or owned_device_ids
    oldest_by_device = (
        Messages.objects.filter(esp_id__in=device_ids)
        .values("esp_id")
        .annotate(oldest=Min("date"))
    )
    oldest_dates = [row["oldest"] for row in oldest_by_device if row["oldest"]]

    if not oldest_dates:
        return Response({"oldest_timestamp": None, "max_age_seconds": 0})

    oldest = max(oldest_dates)
    max_age_seconds = max(0, int((timezone.now() - oldest).total_seconds()))
    return Response({"oldest_timestamp": oldest, "max_age_seconds": max_age_seconds})


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def cfe_summary(request):
    device_ids = _registered_device_ids(request.user)
    since = _parse_local_date_boundary(request.query_params.get("period_start"))
    until = _parse_local_date_boundary(request.query_params.get("period_end"))
    energy_by_device = _energy_by_device(device_ids, since=since, until=until)
    devices = Device.objects.filter(owner=request.user, device_id__in=device_ids)
    device_names = {device.device_id: device.name for device in devices}

    accumulated = round(sum(energy_by_device.values()), 3)
    configured_limit = float(request.query_params.get("configured_limit") or 280)
    usage_percent = round((accumulated / configured_limit) * 100, 2) if configured_limit else 0
    return Response(
        {
            "accumulated_kwh": accumulated,
            "configured_limit": configured_limit,
            "usage_percent": usage_percent,
            "remaining_kwh": round(max(configured_limit - accumulated, 0), 2),
            "devices": [
                {
                    "device_id": device_id,
                    "name": device_names.get(device_id, device_id),
                    "energy_kwh": round(kwh, 3),
                }
                for device_id, kwh in energy_by_device.items()
            ],
        }
    )


@api_view(["GET"])
def cfe_tariffs(request):
    tariff = request.query_params.get("tariff", "domestic_1c")
    return Response(TARIFFS.get(tariff, TARIFFS["domestic_1c"]))
