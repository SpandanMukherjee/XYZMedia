# projects/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .forms import ProjectForm

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