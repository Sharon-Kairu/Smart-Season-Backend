from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from .serializers import LoginSerializer,RegisterSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role not in ['admin', 'superadmin']:
            return Response(
                {"detail": "Only admins can register new agents."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Agent registered successfully"},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
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

        response.set_cookie(
        key=settings.ACCESS_TOKEN_COOKIE_NAME,
        value=access_token,
        path='/',
        httponly=settings.ACCESS_TOKEN_COOKIE_HTTPONLY,
        secure=settings.ACCESS_TOKEN_COOKIE_SECURE,
        samesite=settings.ACCESS_TOKEN_COOKIE_SAMESITE,
        max_age=settings.ACCESS_TOKEN_COOKIE_AGE,
        domain=settings.ACCESS_TOKEN_COOKIE_DOMAIN
        )


        response.set_cookie(
        key=settings.REFRESH_TOKEN_COOKIE_NAME,
        value=refresh_token,
        path='/',
        httponly=settings.REFRESH_TOKEN_COOKIE_HTTPONLY,
        secure=settings.REFRESH_TOKEN_COOKIE_SECURE,
        samesite=settings.REFRESH_TOKEN_COOKIE_SAMESITE,
        max_age=settings.REFRESH_TOKEN_COOKIE_AGE,
        domain=settings.REFRESH_TOKEN_COOKIE_DOMAIN
        )
        response.set_cookie(
        key="user_role",
        value=user.role,
        path='/',
        httponly=False,
        secure=settings.ACCESS_TOKEN_COOKIE_SECURE,
        samesite=settings.ACCESS_TOKEN_COOKIE_SAMESITE,
        max_age=settings.ACCESS_TOKEN_COOKIE_AGE,
        domain=settings.ACCESS_TOKEN_COOKIE_DOMAIN
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
        path='/',
        httponly=settings.ACCESS_TOKEN_COOKIE_HTTPONLY,
        secure=settings.ACCESS_TOKEN_COOKIE_SECURE,
        samesite=settings.ACCESS_TOKEN_COOKIE_SAMESITE,
        max_age=settings.ACCESS_TOKEN_COOKIE_AGE,
        domain=settings.ACCESS_TOKEN_COOKIE_DOMAIN
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
    
class Agents(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role not in ['admin', 'superadmin']:
            return Response(
                {"detail": "Only admins can view agents."},
                status=status.HTTP_403_FORBIDDEN
            )

        agents = User.objects.filter(
            role='agent',
            is_active=True
        ).values(
            'id',
            'email',
            'full_name',
            'phone_number',
            'date_joined',
        )

        return Response(list(agents), status=status.HTTP_200_OK)
     

class LogoutView(APIView):
    permission_classes = []
    
    def post(self, request):
        response = Response(
            {"message": "Logged out successfully"}, 
            status=status.HTTP_200_OK
        )
        
        response.delete_cookie(
            key=settings.ACCESS_TOKEN_COOKIE_NAME,
            path='/',
            domain=None,
            samesite=settings.ACCESS_TOKEN_COOKIE_SAMESITE
        )
        
        response.delete_cookie(
            key=settings.REFRESH_TOKEN_COOKIE_NAME,
            path='/',
            domain=None,
            samesite=settings.REFRESH_TOKEN_COOKIE_SAMESITE
        )
        
        response.delete_cookie(
            key="user_role",
            path='/',
            domain=None,
            samesite=settings.ACCESS_TOKEN_COOKIE_SAMESITE
        )
        
        return response