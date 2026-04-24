from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.tokens import AccessToken
from django.conf import settings


class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that reads tokens from HTTP-only cookies
    instead of Authorization headers.
    """
    
    def authenticate(self, request):
        """
        Extract JWT token from cookies and authenticate the user.
        """
        raw_token = request.COOKIES.get(settings.ACCESS_TOKEN_COOKIE_NAME)
        
        if raw_token is None:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
        except InvalidToken:
            return None

        return self.get_user(validated_token), validated_token
    
    def get_validated_token(self, raw_token):
        """
        Validate the raw token and return a validated token instance.
        """
        try:
            return AccessToken(raw_token)
        except InvalidToken as e:
            raise InvalidToken({
                'detail': 'Given token not valid',
                'messages': [str(e)],
            })
