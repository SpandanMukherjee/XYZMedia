import os
from django.db import models
from users.models import UserProfile
from datetime import date
from django.core.exceptions import ValidationError
from django.utils import timezone

class Project(models.Model):

    def validate_script_file_type(value):
        valid_extensions = ['.pdf', '.doc', '.docx']
        ext = os.path.splitext(value.name)[1].lower()

        if ext not in valid_extensions:
            raise ValidationError(f"Unsupported file extension: {ext}. Allowed extensions are: {', '.join(valid_extensions)}.")
        
    def validate_video_file_type(value):
        valid_extensions = ['.mp4', '.avi', '.mov']
        ext = os.path.splitext(value.name)[1].lower()

        if ext not in valid_extensions:
            raise ValidationError(f"Unsupported file extension: {ext}. Allowed extensions are: {', '.join(valid_extensions)}.")
        
    def validate_thumbnail_file_type(value):
        valid_extensions = ['.jpg', '.jpeg', '.png']
        ext = os.path.splitext(value.name)[1].lower()

        if ext not in valid_extensions:
            raise ValidationError(f"Unsupported file extension: {ext}. Allowed extensions are: {', '.join(valid_extensions)}.")

    PRIORITY_CHOICES = [
        ('high', 'High'),
        ('low', 'Low'),        
    ]

    STATUS_CHOICES = [
        ('unassigned', 'Unassigned'),
        ('writing_in_progress', 'Writing in Progress'),
        ('writing_complete', 'Writing Complete'),
        ('producing_in_progress', 'Producing in Progress'),
        ('producing_complete', 'Producing Complete'),
        ('compiling_in_progress', 'Compiling in Progress'),
        ('done', 'Done'),
    ]

    title = models.CharField(max_length=255, default='Untitled Project')
    topic = models.CharField(max_length=255)
    due_date = models.DateField()
    completion_date = models.DateField(null=True, blank=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='low')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='unassigned')

    assigned_writer = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, related_name='assigned_writer', null=True, blank=True)
    assigned_producer = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, related_name='assigned_producer', null=True, blank=True)
    assigned_compiler = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, related_name='assigned_compiler', null=True, blank=True)
    revision_reason = models.TextField(null=True, blank=True)

    script = models.FileField(upload_to='scripts/', validators=[validate_script_file_type], null=True, blank=True)
    video = models.FileField(upload_to='videos/', validators=[validate_video_file_type], null=True, blank=True)
    thumbnail = models.ImageField(upload_to='thumbnails/', validators=[validate_thumbnail_file_type], null=True, blank=True)

    def save(self, *args, **kwargs):
        
        if self.priority == 'low':
            days_left = (self.due_date - date.today()).days
            
            if days_left <= 2:
                self.priority = 'high'

                
        if self.status == 'done' and self.completion_date is None:
            self.completion_date = timezone.now().date()
                
        super().save(*args, **kwargs)

    def __str__(self):
        return self.topic