from django import forms
from django.contrib.auth.models import User
from users.models import UserProfile

class SignupForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput, required=True, label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput, required=True, label="Password Confirmation")
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES[:2], required=True)
    resume = forms.FileField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])

        if commit:
            user.save()

            resume = self.cleaned_data.get('resume')
            role = self.cleaned_data.get('role')

            if resume and role:
                UserProfile.objects.create(
                    user=user,
                    user_type='freelancer',
                    role=role,
                    resume=resume,
                    is_approved=False
                )
            else:
                raise forms.ValidationError("Missing resume or role for user profile.")

class EmployeeCreationForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput, required=True, label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput, required=True, label="Confirm Password")
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES, required=True)

    class Meta:
        model = User
        fields = ['username']

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])

        if commit:
            user.save()

            UserProfile.objects.create(
                user=user,
                user_type='employee',
                role=self.cleaned_data['role'],
                is_approved=True  # Employees are approved by default
            )

        return user