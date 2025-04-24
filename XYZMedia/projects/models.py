from django.db import models
from users.models import UserProfile
from datetime import date

class Project(models.Model):

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
        ('ready', 'Ready'),
        ('done', 'Done'),
    ]

    title = models.CharField(max_length=255, default='Untitled Project')
    topic = models.CharField(max_length=255)
    due_date = models.DateField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='low')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='unassigned')

    assigned_writer = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, related_name='assigned_writer', null=True, blank=True)
    assigned_producer = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, related_name='assigned_producer', null=True, blank=True)
    assigned_compiler = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, related_name='assigned_compiler', null=True, blank=True)
    revision_reason = models.TextField(null=True, blank=True)

    script = models.FileField(upload_to='scripts/', null=True, blank=True)
    video = models.FileField(upload_to='videos/', null=True, blank=True)
    thumbnail = models.ImageField(upload_to='thumbnails/', null=True, blank=True)

    def save(self, *args, **kwargs):
        
        if self.priority == 'low':
            days_left = (self.due_date - date.today()).days
            
            if days_left <= 2:
                self.priority = 'high'
            else:
                self.priority = 'low'

        super().save(*args, **kwargs)

    def __str__(self):
        return self.topic