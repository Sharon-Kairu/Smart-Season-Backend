from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import FieldUpdate
from .serializers import FieldUpdateSerializer, FieldUpdateListSerializer
from fields.models import Field


class FieldUpdateViewSet(viewsets.ModelViewSet):

    permission_classes = [IsAuthenticated]
    queryset = FieldUpdate.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return FieldUpdateListSerializer
        return FieldUpdateSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        # Admins see all updates
        if user.role == 'admin':
            return FieldUpdate.objects.select_related(
                'field', 'agent'
            ).order_by('-created_at')
        
        # Agents see only updates for their assigned fields
        return FieldUpdate.objects.filter(
            agent=user
        ).select_related('field').order_by('-created_at')
    
    def create(self, request, *args, **kwargs):
        """
        Create a new field update.
        Agents can only create updates for fields assigned to them.
        """
        field_id = request.data.get('field')
        
        # Validate that the field exists and is assigned to the agent (if agent role)
        try:
            field = Field.objects.get(id=field_id)
        except Field.DoesNotExist:
            return Response(
                {"detail": "Field not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check permissions
        if request.user.role == 'agent' and field.assigned_to != request.user:
            return Response(
                {"detail": "You can only update fields assigned to you"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        """Automatically set agent to current user"""
        serializer.save(agent=self.request.user)
    
    def perform_update(self, serializer):
        """Only the agent who created the update can edit it"""
        if self.request.user != serializer.instance.agent:
            return Response(
                {"detail": "You can only edit your own updates"},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save()
    
    def perform_destroy(self, instance):
        """Only the agent who created the update can delete it, or admins"""
        if self.request.user.role != 'admin' and self.request.user != instance.agent:
            return Response(
                {"detail": "You can only delete your own updates"},
                status=status.HTTP_403_FORBIDDEN
            )
        instance.delete()
    
    @action(detail=False, methods=['get'])
    def field_updates(self, request):
        """Get all updates for a specific field"""
        field_id = request.query_params.get('field_id')
        
        if not field_id:
            return Response(
                {"detail": "field_id query parameter required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            field = Field.objects.get(id=field_id)
        except Field.DoesNotExist:
            return Response(
                {"detail": "Field not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check permissions
        if request.user.role == 'agent' and field.assigned_to != request.user:
            return Response(
                {"detail": "You don't have permission to view this field's updates"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        updates = FieldUpdate.objects.filter(field=field).order_by('-created_at')
        serializer = FieldUpdateListSerializer(updates, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent_updates(self, request):
        """Get recent updates (last 7 days)"""
        from django.utils import timezone
        from datetime import timedelta
        
        seven_days_ago = timezone.now() - timedelta(days=7)
        recent = self.get_queryset().filter(created_at__gte=seven_days_ago)
        
        serializer = self.get_serializer(recent, many=True)
        return Response({
            'count': recent.count(),
            'updates': serializer.data
        })
