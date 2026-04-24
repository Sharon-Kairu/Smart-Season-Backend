from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken
from django.conf import settings


class CookieJWTAuthentication(JWTAuthentication):
    
    def authenticate(self, request):
        raw_token = request.COOKIES.get(settings.ACCESS_TOKEN_COOKIE_NAME)
        
        if raw_token is None:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
            user = self.get_user(validated_token)
            return (user, validated_token)
        except (InvalidToken, TokenError):
            return None
    
    def get_validated_token(self, raw_token):
        try:
            return AccessToken(raw_token)
        except TokenError:
            return None