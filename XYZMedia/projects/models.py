from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):

    PRIORITY_CHOICES = [
        ('High', 'High'), 
        ('Low', 'Low'), 
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    topic = models.CharField(max_length=100)
    due_date = models.DateField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='Low')
    auto_assign = models.BooleanField(default=False) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Assignment(models.Model):

    class Status(models.TextChoices):
        UNASSIGNED = 'Unassigned', 'Unassigned'
        ASSIGNED = 'Assigned', 'Assigned'
        IN_PROGRESS = 'In Progress', 'In Progress'
        COMPLETED = 'Completed', 'Completed'
        FREELANCER_SELECTED = 'Freelancer Selected', 'Freelancer Selected'

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.OneToOneField(Project, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=Status.choices, default=Status.UNASSIGNED)

    def __str__(self):
        return f"{self.project.title} - {self.user.username} ({self.status})"
