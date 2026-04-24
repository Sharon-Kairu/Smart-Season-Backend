from django.contrib import admin
from .models import FieldUpdate


@admin.register(FieldUpdate)
class FieldUpdateAdmin(admin.ModelAdmin):
    list_display = ['id', 'field', 'agent', 'new_stage', 'created_at']
    list_filter = ['new_stage', 'agent', 'created_at']
    search_fields = ['field__name', 'agent__email', 'notes']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Update Details', {
            'fields': ('field', 'agent', 'new_stage')
        }),
        ('Notes & Photos', {
            'fields': ('notes', 'photos')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_delete_permission(self, request, obj=None):
        """Only allow superusers or the agent who created the update to delete"""
        if request.user.is_superuser:
            return True
        if obj and obj.agent == request.user:
            return True
        return False
