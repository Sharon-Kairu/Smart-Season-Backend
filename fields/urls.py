from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FieldViewSet, FieldNoteViewSet

router = DefaultRouter()
router.register(r'fields', FieldViewSet, basename='field')
router.register(r'notes', FieldNoteViewSet, basename='fieldnote')

urlpatterns = [
    path('', include(router.urls)),
]
