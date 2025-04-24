# users/models.py
import os
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class UserProfile(models.Model):

    def validate_resume_file_type(value):
        valid_extensions = ['.pdf', '.doc', '.docx']
        ext = os.path.splitext(value.name)[1].lower()

        if ext not in valid_extensions:
            raise ValidationError(f"Unsupported file extension: {ext}. Allowed extensions are: {', '.join(valid_extensions)}.")

    USER_TYPE_CHOICES = [
        ('admin', 'Admin'),
        ('employee', 'Employee'),
        ('freelancer', 'Freelancer'),
    ]

    ROLE_CHOICES = [
        ('writer', 'Writer'),
        ('producer', 'Producer'),
        ('compiler', 'Compiler'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='employee')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, null=True, blank=True, default=None)
    resume = models.FileField(upload_to='resumes/', validators=[validate_resume_file_type], null=True, blank=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def clean(self):
        super().clean()

        if self.user_type == 'admin':

            if self.role is not None:
                raise ValidationError("Admins should not have a role.")
            
        elif self.user_type in ('employee', 'freelancer'):

            if self.role is None:
                raise ValidationError("Employees and freelancers must have a role.")
        else:
            raise ValidationError("Invalid user type.")

    def approve(self):
        self.is_approved = True
        self.save()
