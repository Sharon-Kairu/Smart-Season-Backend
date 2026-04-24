from rest_framework import serializers
from .models import FieldUpdate
from fields.models import Field
from fields.serializers import UserBriefSerializer


class FieldUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and retrieving field updates"""
    agent = UserBriefSerializer(read_only=True)
    field_name = serializers.CharField(source='field.name', read_only=True)
    
    class Meta:
        model = FieldUpdate
        fields = [
            'id', 'field', 'field_name', 'agent', 'new_stage',
            'notes', 'photos', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'agent', 'created_at', 'updated_at']
    
    def validate_field(self, value):
        """Ensure field exists and user has permission"""
        if not Field.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Field not found")
        return value
    
    def create(self, validated_data):
        """Set agent to the current user"""
        validated_data['agent'] = self.context['request'].user
        return super().create(validated_data)


class FieldUpdateListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for update list views"""
    agent = UserBriefSerializer(read_only=True)
    field_name = serializers.CharField(source='field.name', read_only=True)
    
    class Meta:
        model = FieldUpdate
        fields = [
            'id', 'field', 'field_name', 'agent', 'new_stage',
            'notes', 'created_at'
        ]