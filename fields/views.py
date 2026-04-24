from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count
from .models import Field, FieldNote, FieldHistory
from .serializers import (
    FieldSerializer, FieldListSerializer, FieldUpdateSerializer,
    FieldNoteSerializer, FieldHistorySerializer
)


class IsAdminOrAssignedAgent(IsAuthenticated):

    def has_object_permission(self, request, view, obj):
        if request.user.role in ['admin', 'superadmin']:
            return True
        return obj.assigned_to == request.user


class FieldViewSet(viewsets.ModelViewSet):

    permission_classes = [IsAuthenticated]
    queryset = Field.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return FieldListSerializer
        elif self.action in ['partial_update', 'update']:
            return FieldUpdateSerializer
        return FieldSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role in ['admin', 'superadmin']:
            return Field.objects.prefetch_related('updates', 'field_notes')
        
        return Field.objects.filter(
            assigned_to=user
        ).prefetch_related('updates', 'field_notes')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        if self.request.user.role not in ['admin', 'superadmin']:
            field = self.get_object()
            if field.assigned_to != self.request.user:
                return Response(
                    {"detail": "You can only update fields assigned to you"},
                    status=status.HTTP_403_FORBIDDEN
                )
        serializer.save()
    
    def perform_destroy(self, instance):
        if self.request.user.role not in ['admin', 'superadmin']:
            return Response(
                {"detail": "Only admins can delete fields"},
                status=status.HTTP_403_FORBIDDEN
            )
        instance.delete()
    
    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        user = request.user
        
        if user.role in ['admin', 'superadmin']:
            fields = Field.objects.all()
        else:
            fields = Field.objects.filter(assigned_to=user)
        
        total_fields = fields.count()
        status_breakdown = fields.values('status').annotate(count=Count('status'))
        stage_breakdown = fields.values('stage').annotate(count=Count('stage'))
        
        status_dict = {item['status']: item['count'] for item in status_breakdown}
        stage_dict = {item['stage']: item['count'] for item in stage_breakdown}
        
        return Response({
            'total_fields': total_fields,
            'status_breakdown': {
                'active': status_dict.get('active', 0),
                'at_risk': status_dict.get('at_risk', 0),
                'completed': status_dict.get('completed', 0),
            },
            'stage_breakdown': {
                'planted': stage_dict.get('planted', 0),
                'growing': stage_dict.get('growing', 0),
                'ready': stage_dict.get('ready', 0),
                'harvested': stage_dict.get('harvested', 0),
            }
        })
    
    @action(detail=False, methods=['get'])
    def agents(self, request):
       
        if request.user.role not in ['admin', 'superadmin']:
            return Response(
                {"detail": "Only admins can view agent list"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        from users.models import User
        agents = User.objects.filter(
            role='agent',
            is_active=True
        ).annotate(
            fields_count=Count('assigned_fields')
        ).values(
            'id', 'email', 'full_name', 'phone_number', 'fields_count'
        )
        
        return Response(list(agents))
    
    @action(detail=False, methods=['get'])
    def at_risk_fields(self, request):
        at_risk = self.get_queryset().filter(status='at_risk')
        serializer = self.get_serializer(at_risk, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get', 'post'])
    def notes(self, request, pk=None):
        field = self.get_object()
        
        if request.method == 'GET':
            notes = FieldNote.objects.filter(field=field).order_by('-created_at')
            serializer = FieldNoteSerializer(notes, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            serializer = FieldNoteSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save(field=field, author=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        field = self.get_object()
        history = FieldHistory.objects.filter(field=field).order_by('-changed_at')
        serializer = FieldHistorySerializer(history, many=True)
        return Response(serializer.data)


class FieldNoteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = FieldNote.objects.all()
    serializer_class = FieldNoteSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role in ['admin', 'superadmin']:
            return FieldNote.objects.select_related('field', 'author').order_by('-created_at')
        
        return FieldNote.objects.filter(
            field__assigned_to=user
        ).select_related('field', 'author').order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    def perform_update(self, serializer):
        if self.request.user.role not in ['admin', 'superadmin'] and self.request.user != serializer.instance.author:
            return Response(
                {"detail": "You can only edit your own notes"},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save()
    
    def perform_destroy(self, instance):
        if self.request.user.role not in ['admin', 'superadmin'] and self.request.user != instance.author:
            return Response(
                {"detail": "You can only delete your own notes"},
                status=status.HTTP_403_FORBIDDEN
            )
        instance.delete()
