from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from users.models import UserProfile
from projects.models import Project
from users.models import UserProfile

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required
def redirect_to_dashboard(request):
    if request.user.userprofile.user_type == 'admin':
        return redirect('main:admin_dashboard')
    elif request.user.userprofile.user_type == 'employee':
        return redirect('main:employee_dashboard')
    elif request.user.userprofile.user_type == 'freelancer':
        return redirect('main:freelancer_dashboard')
    else:
        return redirect('/')

@login_required
def admin_dashboard(request):
    projects = Project.objects.all()
    freelancers = UserProfile.objects.filter(user_type='freelancer', is_approved=False)
    employees = UserProfile.objects.filter(user_type='employee')
    freelancers_list = UserProfile.objects.filter(user_type='freelancer', is_approved=True)

    return render(request, 'main/admin_dashboard.html', {
        'projects': projects,
        'freelancers': freelancers,
        'employees': employees,
        'freelancers_list': freelancers_list,
    })

@login_required
def employee_dashboard(request):
    profile = request.user.userprofile
    tasks = []

    if profile.role == 'writer':
        tasks = Project.objects.filter(assigned_writer=profile)
    elif profile.role == 'producer':
        tasks = Project.objects.filter(assigned_producer=profile)
    elif profile.role == 'compiler':
        tasks = Project.objects.filter(assigned_compiler=profile)

    return render(request, 'main/employee_dashboard.html', {'tasks': tasks})

def freelancer_dashboard(request):
    profile = request.user.userprofile
    tasks = []

    if not profile.is_approved:
        return redirect('main:dashboard')

    if profile.role == 'writer':
        tasks = Project.objects.filter(assigned_writer=profile)
    elif profile.role == 'producer':
        tasks = Project.objects.filter(assigned_producer=profile)

    return render(request, 'main/freelancer_dashboard.html', {'tasks': tasks})

@login_required
def logout_user(request):
    logout(request)
    return redirect('/')
