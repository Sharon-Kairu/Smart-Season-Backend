from django.urls import path,include
from .views import LoginView, RefreshTokenView,MeView,RegisterView,LogoutView,Agents
from dj_rest_auth.jwt_auth import get_refresh_view

urlpatterns = [
    path('auth/login/',LoginView.as_view(),name='login'),
    path('auth/logout/',LogoutView.as_view(),name='logout'),
    path('auth/token/refresh/', get_refresh_view().as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='Register'),
    path('me/',MeView.as_view(),name='me'),
    path('agents/', Agents.as_view(), name='agents'),
  
]
