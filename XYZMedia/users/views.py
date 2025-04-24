from django.shortcuts import render, redirect
from .forms import SignupForm
from django.contrib import messages

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
