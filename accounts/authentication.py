# accounts/authentication.py
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


class CookieJWTAuthentication(JWTAuthentication):
    """
    توکن JWT رو اول از هدر Authorization می‌خونه،
    اگه نبود از کوکی access_token می‌خونه.
    """

    def authenticate(self, request):
        header = self.get_header(request)

        if header is None:
            raw_token = request.COOKIES.get("access_token")
        else:
            raw_token = self.get_raw_token(header)

        if raw_token is None:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
        except (InvalidToken, TokenError):
            # توکن منقضی یا نامعتبر → کاربر ناشناس
            return None

        return self.get_user(validated_token), validated_token