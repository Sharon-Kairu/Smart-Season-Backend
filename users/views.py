from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from .serializer import LoginSerializer

class LoginView(APIView):
    permission_classes = [] 
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['authenticated_user']
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        response = Response(
            {
                "message": "Login successful",
                "user": {
                    "id": user.id,
                    "role": user.role,
                    "email": user.email,
                    "full_name": user.full_name,
                },
            },
            status=status.HTTP_200_OK,
        )

        # Set the access token cookie
        response.set_cookie(
        key=settings.ACCESS_TOKEN_COOKIE_NAME,
        value=access_token,
        httponly=settings.ACCESS_TOKEN_COOKIE_HTTPONLY,
        secure=settings.ACCESS_TOKEN_COOKIE_SECURE,
        samesite=settings.ACCESS_TOKEN_COOKIE_SAMESITE,
        max_age=settings.ACCESS_TOKEN_COOKIE_AGE
        )


        response.set_cookie(
        key=settings.REFRESH_TOKEN_COOKIE_NAME,
        value=refresh_token,
        httponly=settings.REFRESH_TOKEN_COOKIE_HTTPONLY,
        secure=settings.REFRESH_TOKEN_COOKIE_SECURE,
        samesite=settings.REFRESH_TOKEN_COOKIE_SAMESITE,
        max_age=settings.REFRESH_TOKEN_COOKIE_AGE
        )
        response.set_cookie(
        key="user_role",
        value=user.role,
        httponly=False,  # Set to False so the Next.js middleware can read it easily
        secure=settings.ACCESS_TOKEN_COOKIE_SECURE,
        samesite=settings.ACCESS_TOKEN_COOKIE_SAMESITE,
        max_age=settings.ACCESS_TOKEN_COOKIE_AGE
)

        return response
    
class RefreshTokenView(APIView):
    permission_classes = []

    def post(self, request):
        refresh_token = request.COOKIES.get(settings.REFRESH_TOKEN_COOKIE_NAME)
        if not refresh_token:
            return Response({"detail": "Refresh token not found."}, status=status.HTTP_401_UNAUTHORIZED)
        try:
                refresh = RefreshToken(refresh_token)
                new_access_token = str(refresh.access_token)
        except Exception as e:
                return Response({"detail": "Invalid refresh token."}, status=status.HTTP_401_UNAUTHORIZED)


        response = Response({"message": "Token refreshed"})
        response.set_cookie(
        key=settings.ACCESS_TOKEN_COOKIE_NAME,
        value=new_access_token,
        httponly=settings.ACCESS_TOKEN_COOKIE_HTTPONLY,
        secure=settings.ACCESS_TOKEN_COOKIE_SECURE,
        samesite=settings.ACCESS_TOKEN_COOKIE_SAMESITE,
        max_age=settings.ACCESS_TOKEN_COOKIE_AGE
        )
        return response

class MeView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "full_name": user.full_name,
           
        })

class LogoutView(APIView):
    permission_classes = []
    
    def post(self, request):
        response = Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
        
        response.delete_cookie(
            key=settings.ACCESS_TOKEN_COOKIE_NAME,
            samesite=settings.ACCESS_TOKEN_COOKIE_SAMESITE
        )
        response.delete_cookie(
            key=settings.REFRESH_TOKEN_COOKIE_NAME,
            samesite=settings.REFRESH_TOKEN_COOKIE_SAMESITE
        )
        response.delete_cookie(
            key="user_role",
            samesite=settings.ACCESS_TOKEN_COOKIE_SAMESITE
        )
        
        return response