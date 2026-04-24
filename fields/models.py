from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Field(models.Model):

    STAGE_CHOICES = [
        ('planted', 'Planted'),
        ('growing', 'Growing'),
        ('ready', 'Ready'),
        ('harvested', 'Harvested'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('at_risk', 'At Risk'),
        ('completed', 'Completed'),
    ]
    
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    crop_type = models.CharField(max_length=100)
    planting_date = models.DateField()
    size_in_acres = models.DecimalField(max_digits=8, decimal_places=2)
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default='planted')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_fields',
        limit_choices_to={'role': 'agent'}
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_fields'
    )
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'fields_field'
        verbose_name = 'Field'
        verbose_name_plural = 'Fields'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['assigned_to', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['stage']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.crop_type} ({self.location})"
    
    def get_days_since_planting(self):
        return (timezone.now().date() - self.planting_date).days
    
    def estimate_status(self):
        if self.stage == 'harvested':
            return 'completed'
        
        days_since_planting = self.get_days_since_planting()
        
        if self.stage == 'planted':
            return 'active'
        elif self.stage == 'growing':
            return 'at_risk' if days_since_planting > 45 else 'active'
        elif self.stage == 'ready':
            return 'active'
        
        return 'active'


class FieldNote(models.Model):
    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name='field_notes')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='authored_notes')
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'fields_fieldnote'
        verbose_name = 'Field Note'
        verbose_name_plural = 'Field Notes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['field', '-created_at']),
        ]
    
    def __str__(self):
        return f"Note on {self.field.name} by {self.author.email if self.author else 'Unknown'}"


class FieldHistory(models.Model):
    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name='history')
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='field_changes')
    field_name = models.CharField(max_length=100)
    old_value = models.CharField(max_length=255, blank=True)
    new_value = models.CharField(max_length=255)
    changed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'fields_fieldhistory'
        verbose_name = 'Field History'
        verbose_name_plural = 'Field Histories'
        ordering = ['-changed_at']
        indexes = [
            models.Index(fields=['field', '-changed_at']),
        ]
    
    def __str__(self):
        return f"{self.field.name}: {self.field_name} changed from '{self.old_value}' to '{self.new_value}'"
