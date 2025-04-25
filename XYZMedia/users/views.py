from django.shortcuts import render, redirect, get_object_or_404
from users.forms import SignupForm, EmployeeCreationForm
from django.contrib import messages
from users.models import UserProfile
from main.views import admin_dashboard
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User

def register_user(request):
    
    if request.method == 'POST':
        form = SignupForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            messages.success(request, "Account creation successful. Admin will review your request.")
            return redirect('/accounts/auth/login/')
    else:
        form = SignupForm()

    return render(request, 'register.html', {'form': form})

@user_passes_test(lambda u: u.is_superuser)
def approve_freelancer(request, id):
    profile = get_object_or_404(UserProfile, id=id)
    profile.is_approved = True
    profile.save()
    return redirect('main:admin_dashboard')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def reject_freelancer(request, id):
    user = get_object_or_404(User, id=id)

    if hasattr(user, 'userprofile') and user.userprofile.user_type == 'freelancer' and not user.userprofile.is_approved:
        user.delete()
        messages.success(request, "Freelancer rejected and account deleted.")
    else:
        messages.error(request, "Invalid rejection attempt.")

    return redirect('main:admin_dashboard')

@login_required
def create_employee(request):
    if request.method == 'POST':
        form = EmployeeCreationForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Employee account created successfully.")
            return redirect('main:admin_dashboard')
    else:
        form = EmployeeCreationForm()

    return render(request, 'users/create_employee.html', {'form': form})
