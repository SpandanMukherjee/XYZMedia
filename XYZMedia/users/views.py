from django.shortcuts import render, redirect, get_object_or_404
from .forms import SignupForm
from django.contrib import messages
from users.models import UserProfile

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

def approve_freelancer(request, id):
    profile = get_object_or_404(UserProfile, id=id)
    profile.is_approved = True
    profile.save()
    return redirect('main:admin_dashboard')
