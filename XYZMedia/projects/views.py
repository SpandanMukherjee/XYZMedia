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
        return redirect('/')

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
