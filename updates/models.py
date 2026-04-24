from django.db import models
from django.contrib.auth import get_user_model
from fields.models import Field

User = get_user_model()


class FieldUpdate(models.Model):
    """
    Represents an update to a field's status/stage by a field agent.
    """
    STAGE_CHOICES = [
        ('planted', 'Planted'),
        ('growing', 'Growing'),
        ('ready', 'Ready'),
        ('harvested', 'Harvested'),
    ]
    
    field = models.ForeignKey(
        Field,
        on_delete=models.CASCADE,
        related_name='updates',
        help_text="Field being updated"
    )
    agent = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='field_updates',
        limit_choices_to={'role': 'agent'},
        help_text="Agent who submitted the update"
    )
    
    # Update details
    new_stage = models.CharField(
        max_length=20,
        choices=STAGE_CHOICES,
        help_text="Updated stage of the crop"
    )
    notes = models.TextField(
        blank=True,
        help_text="Observations or notes from the agent"
    )
    
    # Image support for future extensions
    photos = models.TextField(
        blank=True,
        help_text="JSON array of photo URLs or base64 encoded images"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'updates_fieldupdate'
        verbose_name = 'Field Update'
        verbose_name_plural = 'Field Updates'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['field', '-created_at']),
            models.Index(fields=['agent', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.field.name} - {self.new_stage} by {self.agent.email}"
    
    def save(self, *args, **kwargs):
        """
        When an update is saved, update the field's stage and auto-update status.
        """
        super().save(*args, **kwargs)
        
        # Update the field's stage
        self.field.stage = self.new_stage
        self.field.status = self.field.estimate_status()
        self.field.save(update_fields=['stage', 'status', 'updated_at'])
