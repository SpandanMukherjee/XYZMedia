from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

@login_required
def dashboard(response):
    return render(response, 'dashboard.html', {})

@login_required
def logout_user(response):
    logout(response)
    return redirect('/')