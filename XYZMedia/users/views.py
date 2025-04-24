from django.shortcuts import render, redirect
from .forms import SignupForm
from django.contrib import messages

def register_user(response):
    form = SignupForm()
    if response.method == 'POST':
        form = SignupForm(response.POST)
        if form.is_valid():
            form.save()
            messages.success(response, "Account creation successful. Admin will review your request")
            return redirect('/')

    return render(response, 'register.html', {'form':form})