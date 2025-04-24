# projects/forms.py

from django import forms
from projects.models import Project
from datetime import date

class ProjectForm(forms.ModelForm):
    
    class Meta:
        model = Project
        fields = ['topic', 'due_date', 'priority']

    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')

        if due_date and due_date <= date.today():
            raise forms.ValidationError("Due date must be in the future.")
        
        return due_date

class ScriptUploadForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = ['script']

    def save(self, commit=True):
        project = super().save(commit=False)
        project.status = 'writing_complete'

        if commit:
            project.save()

        return project

class VideoUploadForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = ['video']

    def save(self, commit=True):
        project = super().save(commit=False)
        project.status = 'producing_complete'

        if commit:
            project.save()

        return project


class ThumbnailUploadForm(forms.ModelForm):

    SEND_BACK_CHOICES = [
        ('unassigned', 'Send back to Writers (unassigned)'),
        ('writing_complete', 'Send back to Producers (writing complete)'),
    ]

    send_back_to = forms.ChoiceField(
        choices=SEND_BACK_CHOICES,
        required=False,
        label="Revisions - send back to"
    )

    revision_reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3}),
        help_text="Provide reason for sending back if requesting revisions."
    )

    class Meta:
        model = Project
        fields = ['thumbnail', 'send_back_to', 'revision_reason']

    def save(self, commit=True):
        project = super().save(commit=False)
        send_back_to = self.cleaned_data.get('send_back_to')
        reason = self.cleaned_data.get('revision_reason')   

        if send_back_to:
            project.status = send_back_to
            project.revision_reason = reason or ''
        else:
            project.status = 'ready'
            project.revision_reason = ''

        if commit:
            project.save()

        return project