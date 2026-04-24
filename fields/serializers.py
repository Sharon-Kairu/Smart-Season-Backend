from rest_framework import serializers
from .models import Field, FieldNote, FieldHistory
from users.models import User


class UserBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'role', 'phone_number']
        read_only_fields = ['id']


class FieldNoteSerializer(serializers.ModelSerializer):
    author = UserBriefSerializer(read_only=True)
    author_name = serializers.SerializerMethodField()
    
    class Meta:
        model = FieldNote
        fields = ['id', 'field', 'author', 'author_name', 'note', 'created_at', 'updated_at']
        read_only_fields = ['id', 'field', 'author', 'created_at', 'updated_at']
    
    def get_author_name(self, obj):
        return obj.author.full_name if obj.author else 'Unknown'


class FieldHistorySerializer(serializers.ModelSerializer):
    changed_by_name = serializers.SerializerMethodField()
    field_name_display = serializers.SerializerMethodField()
    
    class Meta:
        model = FieldHistory
        fields = [
            'id', 'field', 'changed_by', 'changed_by_name', 
            'field_name', 'field_name_display', 'old_value', 
            'new_value', 'changed_at'
        ]
        read_only_fields = ['id', 'changed_at']
    
    def get_changed_by_name(self, obj):
        return obj.changed_by.full_name if obj.changed_by else 'System'
    
    def get_field_name_display(self, obj):
        return obj.field_name.replace('_', ' ').title()


class FieldSerializer(serializers.ModelSerializer):
    assigned_to = UserBriefSerializer(read_only=True)
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='agent'),
        write_only=True,
        required=False,
        allow_null=True,
        source='assigned_to'
    )
    created_by = UserBriefSerializer(read_only=True)
    
    days_since_planting = serializers.SerializerMethodField()
    estimated_status = serializers.SerializerMethodField()
    updates_count = serializers.SerializerMethodField()
    notes_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Field
        fields = [
            'id', 'name', 'location', 'crop_type', 'planting_date',
            'size_in_acres', 'stage', 'status', 'assigned_to',
            'assigned_to_id', 'created_by', 'notes', 'created_at',
            'updated_at', 'days_since_planting', 'estimated_status',
            'updates_count', 'notes_count'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
    
    def get_days_since_planting(self, obj):
        return obj.get_days_since_planting()
    
    def get_estimated_status(self, obj):
        return obj.estimate_status()
    
    def get_updates_count(self, obj):
        return obj.updates.count()
    
    def get_notes_count(self, obj):
        return obj.field_notes.count()
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class FieldListSerializer(serializers.ModelSerializer):
    assigned_to = UserBriefSerializer(read_only=True)
    days_since_planting = serializers.SerializerMethodField()
    updates_count = serializers.SerializerMethodField()
    notes_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Field
        fields = [
            'id', 'name', 'location', 'crop_type', 'planting_date',
            'size_in_acres', 'stage', 'status', 'assigned_to',
            'days_since_planting', 'updates_count', 'notes_count', 'created_at'
        ]
    
    def get_days_since_planting(self, obj):
        return obj.get_days_since_planting()
    
    def get_updates_count(self, obj):
        return obj.updates.count()
    
    def get_notes_count(self, obj):
        return obj.field_notes.count()


class FieldUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Field
        fields = ['stage', 'status', 'notes', 'assigned_to']
    
    def update(self, instance, validated_data):
        from .models import FieldHistory
        
        request = self.context.get('request')
        user = request.user if request else None
        
        tracked_fields = ['stage', 'status', 'assigned_to']
        
        for field_name in tracked_fields:
            if field_name in validated_data:
                old_value = getattr(instance, field_name)
                new_value = validated_data[field_name]
                
                old_str = str(old_value) if old_value else ''
                new_str = str(new_value) if new_value else ''
                
                if old_str != new_str:
                    FieldHistory.objects.create(
                        field=instance,
                        changed_by=user,
                        field_name=field_name,
                        old_value=old_str,
                        new_value=new_str
                    )
        
        return super().update(instance, validated_data)