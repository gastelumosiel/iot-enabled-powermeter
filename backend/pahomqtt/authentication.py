from django.contrib.auth import get_user_model
from django.core import signing
from rest_framework import authentication, exceptions


class SignedTokenAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        header = authentication.get_authorization_header(request).decode("utf-8")
        if not header:
            return None

        parts = header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return None

        try:
            payload = signing.loads(parts[1], salt="powerlytix-api")
        except signing.BadSignature as exc:
            raise exceptions.AuthenticationFailed("Invalid token.") from exc

        User = get_user_model()
        try:
            user = User.objects.get(pk=payload.get("user_id"), is_active=True)
        except User.DoesNotExist as exc:
            raise exceptions.AuthenticationFailed("User not found.") from exc

        return (user, None)
