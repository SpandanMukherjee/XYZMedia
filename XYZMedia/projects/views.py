# projects/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.db import models
from .models import Project
from .forms import ScriptUploadForm, VideoUploadForm, ThumbnailUploadForm, ProjectForm

@login_required
def create_project(request):
    profile = request.user.userprofile

    if profile.user_type != 'admin':
        return HttpResponseForbidden("Only admins can create projects.")

    form = ProjectForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('main:admin_dashboard')

    return render(request, 'projects/create_project.html', {'form': form})

@login_required
def writer_upload(request, pk):
    project = get_object_or_404(Project, pk=pk)
    profile = request.user.userprofile

    if profile.role != 'writer':
        return HttpResponseForbidden("You do not have permission to upload scripts.")

    if profile.user_type == 'freelancer' and not profile.is_approved:
        return HttpResponseForbidden("You are not approved to work on tasks yet.")

    if project.assigned_writer != profile:
        return HttpResponseForbidden("You must claim or be assigned this task before uploading.")

    form = ScriptUploadForm(request.POST or None, request.FILES or None, instance=project)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('projects:dashboard')

    return render(request, 'projects/writer_upload.html', {'form': form, 'project': project})

@login_required
def producer_upload(request, pk):
    project = get_object_or_404(Project, pk=pk)
    profile = request.user.userprofile

    if profile.role != 'producer':
        return HttpResponseForbidden("You do not have permission to upload videos.")

    if profile.user_type == 'freelancer' and not profile.is_approved:
        return HttpResponseForbidden("You are not approved to work on tasks yet.")

    if project.assigned_producer != profile:
        return HttpResponseForbidden("You must claim or be assigned this task before uploading.")

    form = VideoUploadForm(request.POST or None, request.FILES or None, instance=project)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('projects:dashboard')

    return render(request, 'projects/producer_upload.html', {'form': form, 'project': project})

@login_required
def compiler_upload(request, pk):
    project = get_object_or_404(Project, pk=pk)
    profile = request.user.userprofile

    if profile.user_type != 'employee' or profile.role != 'compiler':
        return HttpResponseForbidden("You do not have permission to compile projects.")

    if project.assigned_compiler != profile:
        return HttpResponseForbidden("This project is not assigned to you.")

    form = ThumbnailUploadForm(request.POST or None, request.FILES or None, instance=project)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('projects:dashboard')

    return render(request, 'projects/compiler_upload.html', {'form': form, 'project': project})

@login_required
def available_tasks(request):
    profile = request.user.userprofile

    if profile.user_type != 'freelancer':
        return HttpResponseForbidden("You do not have permission to view available tasks.")

    if not profile.is_approved:
        return HttpResponseForbidden("You are not approved to work on tasks yet.")

    if profile.role == 'writer':
        tasks = Project.objects.filter(status='unassigned', priority='low')
    elif profile.role == 'producer':
        tasks = Project.objects.filter(status='writing_complete', priority='low')
    else:
        tasks = Project.objects.none()

    return render(request, 'projects/available_tasks.html', {'tasks': tasks})

@login_required
def claim_task(request, pk):
    project = get_object_or_404(Project, pk=pk)
    profile = request.user.userprofile

    if profile.user_type != 'freelancer':
        return HttpResponseForbidden("You do not have permission to claim tasks.")

    if not profile.is_approved:
        return HttpResponseForbidden("You are not approved to work on tasks yet.")

    if Project.objects.filter(
        (models.Q(assigned_writer=profile) & models.Q(status__icontains='writing')) |
        (models.Q(assigned_producer=profile) & models.Q(status__icontains='producing'))
    ).exists():
        return HttpResponseForbidden("You already have an ongoing task.")

    if profile.role == 'writer' and project.status == 'unassigned' and project.priority == 'low':
        project.assigned_writer = profile
        project.status = 'writing_in_progress'
        project.save()
    elif profile.role == 'producer' and project.status == 'writing_complete' and project.priority == 'low':
        project.assigned_producer = profile
        project.status = 'producing_in_progress'
        project.save()
    else:
        return HttpResponseForbidden("This task cannot be claimed by you.")

    return redirect('projects:available_tasks')

@login_required
def dashboard(request):
    profile = request.user.userprofile

    if profile.user_type == 'admin':
        projects = Project.objects.all()
        return render(request, 'projects/admin_dashboard.html', {'projects': projects})

    elif profile.user_type == 'employee':

        if profile.role == 'writer':
            tasks = Project.objects.filter(assigned_writer=profile)
        elif profile.role == 'producer':
            tasks = Project.objects.filter(assigned_producer=profile)
        elif profile.role == 'compiler':
            tasks = Project.objects.filter(assigned_compiler=profile)
        else:
            tasks = Project.objects.none()

        return render(request, 'projects/employee_dashboard.html', {'tasks': tasks})

    elif profile.user_type == 'freelancer':
        
        if not profile.is_approved:
            return HttpResponseForbidden("You are not approved to work on tasks yet.")

        if profile.role == 'writer':
            tasks = Project.objects.filter(assigned_writer=profile)
        elif profile.role == 'producer':
            tasks = Project.objects.filter(assigned_producer=profile)
        else:
            tasks = Project.objects.none()

        return render(request, 'projects/freelancer_dashboard.html', {'tasks': tasks})

    return HttpResponseForbidden()