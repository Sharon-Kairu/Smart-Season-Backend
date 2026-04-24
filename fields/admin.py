from django.contrib import admin
from .models import Field


@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = ['name', 'crop_type', 'location', 'assigned_to', 'stage', 'status', 'planting_date', 'created_at']
    list_filter = ['stage', 'status', 'assigned_to', 'created_at']
    search_fields = ['name', 'location', 'crop_type']
    readonly_fields = ['created_by', 'created_at', 'updated_at', 'get_days_since_planting']
    fieldsets = (
        ('Field Information', {
            'fields': ('name', 'location', 'crop_type', 'size_in_acres')
        }),
        ('Planting & Status', {
            'fields': ('planting_date', 'stage', 'status', 'get_days_since_planting')
        }),
        ('Assignment', {
            'fields': ('assigned_to', 'created_by')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_days_since_planting(self, obj):
        return f"{obj.get_days_since_planting()} days"
    get_days_since_planting.short_description = "Days Since Planting"
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
