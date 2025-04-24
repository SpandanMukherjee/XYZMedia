from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

@login_required
def logout_user(request):
    logout(request)
    return redirect('/')  # You can change '/' to your desired URL after logout
