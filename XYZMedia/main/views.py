from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.db import transaction
from users.models import UserProfile
from projects.models import Project
from projects.forms import ScriptUploadForm, VideoUploadForm, ThumbnailUploadForm

@login_required
def redirect_to_dashboard(request):
    ut = request.user.userprofile.user_type
    if ut == 'admin':
        return redirect('main:admin_dashboard')
    if ut == 'employee':
        return redirect('main:employee_dashboard')
    if ut == 'freelancer':
        return redirect('main:freelancer_dashboard')
    return redirect('/')

@login_required
def admin_dashboard(request):
    projects = Project.objects.exclude(status='done')
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

    if request.method == 'POST':
        task = get_object_or_404(Project, id=request.POST.get('task_id'))

        if profile.role == 'writer':
            form = ScriptUploadForm(request.POST, request.FILES, instance=task)
            next_status = 'writing_complete'

            if form.is_valid():
                form.save()
                task.status = next_status
                task.assigned_writer = None
                task.save()

        elif profile.role == 'producer':
            form = VideoUploadForm(request.POST, request.FILES, instance=task)
            next_status = 'producing_complete'

            if form.is_valid():
                form.save()
                task.status = next_status
                task.assigned_producer = None
                task.save()

        else:  # compiler
            form = ThumbnailUploadForm(request.POST, request.FILES, instance=task)

            if form.is_valid():
                project = form.save()
                send_back_to = form.cleaned_data.get('send_back_to')
                project.assigned_compiler = None

                if send_back_to == 'unassigned':
                    project.assigned_writer = None
                    project.assigned_producer = None
                elif send_back_to == 'writing_complete':
                    project.assigned_producer = None

                project.save()

        return redirect('main:employee_dashboard')

    task = None
    with transaction.atomic():
        if profile.role == 'writer':
            task = Project.objects.select_for_update(skip_locked=True).filter(
                assigned_writer=profile, status='writing_in_progress'
            ).first()
            if not task:
                task = Project.objects.select_for_update(skip_locked=True).filter(
                    status='unassigned', priority='high', assigned_writer__isnull=True
                ).first()
                if task:
                    task.assigned_writer = profile
                    task.status = 'writing_in_progress'
                    task.save()

        elif profile.role == 'producer':
            task = Project.objects.select_for_update(skip_locked=True).filter(
                assigned_producer=profile, status='producing_in_progress'
            ).first()
            if not task:
                task = Project.objects.select_for_update(skip_locked=True).filter(
                    status='writing_complete', priority='high', assigned_producer__isnull=True
                ).first()
                if task:
                    task.assigned_producer = profile
                    task.status = 'producing_in_progress'
                    task.save()

        else:  # compiler
            task = Project.objects.select_for_update(skip_locked=True).filter(
                assigned_compiler=profile, status='compiling_in_progress'
            ).first()
            if not task:
                task = Project.objects.select_for_update(skip_locked=True).filter(
                    status='producing_complete', priority='high', assigned_compiler__isnull=True
                ).first()
                if task:
                    task.assigned_compiler = profile
                    task.status = 'compiling_in_progress'
                    task.save()

    task_forms = []
    if task:
        if profile.role == 'writer':
            form = ScriptUploadForm(instance=task)
        elif profile.role == 'producer':
            form = VideoUploadForm(instance=task)
        else:
            form = ThumbnailUploadForm(instance=task)
        task_forms.append((task, form))

    return render(request, 'main/employee_dashboard.html', {
        'task_forms': task_forms
    })

@login_required
def freelancer_dashboard(request):
    profile = request.user.userprofile
    if not profile.is_approved:
        return render(request, 'main/freelancer_pending_dashboard.html')

    if request.method == 'POST':
        task = get_object_or_404(Project, id=request.POST.get('task_id'))

        # Upload case
        if request.FILES:
            if profile.role == 'writer' and 'script' in request.FILES:
                form = ScriptUploadForm(request.POST, request.FILES, instance=task)
                if form.is_valid():
                    form.save()
                    task.status = 'writing_complete'
                    task.assigned_writer = None
                    task.save()

            elif profile.role == 'producer' and 'video' in request.FILES:
                form = VideoUploadForm(request.POST, request.FILES, instance=task)
                if form.is_valid():
                    form.save()
                    task.status = 'producing_complete'
                    task.assigned_producer = None
                    task.save()

        # Claim case
        else:
            if profile.role == 'writer' and task.assigned_writer is None and task.status == 'unassigned':
                task.assigned_writer = profile
                task.status = 'writing_in_progress'
                task.save()

            elif profile.role == 'producer' and task.assigned_producer is None and task.status == 'writing_complete':
                task.assigned_producer = profile
                task.status = 'producing_in_progress'
                task.save()

        return redirect('main:freelancer_dashboard')

    task = Project.objects.filter(**{f'assigned_{profile.role}': profile}).first()
    available_tasks = []

    if not task:
        filters = {f'assigned_{profile.role}__isnull': True, 'priority': 'low'}

        if profile.role == 'writer':
            filters['status'] = 'unassigned'
        elif profile.role == 'producer':
            filters['status'] = 'writing_complete'

        available_tasks = Project.objects.filter(**filters)

    task_forms = []

    if task:
        if profile.role == 'writer':
            form = ScriptUploadForm(instance=task)
        elif profile.role == 'producer':
            form = VideoUploadForm(instance=task)
            
    task_forms.append((task, form))

    return render(request, 'main/freelancer_dashboard.html', {
        'task': task,
        'available_tasks': available_tasks,
        'task_forms': task_forms
    })

@login_required
def archives(request):  
    projects = Project.objects.filter(status='done')
    return render(request, 'main/archives.html', {'projects': projects})

@login_required
def logout_user(request):
    logout(request)
    return redirect('/')