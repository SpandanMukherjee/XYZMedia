from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
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

    if request.method == 'POST':
        task = get_object_or_404(Project, id=request.POST.get('task_id'))
        if profile.role == 'writer':
            form = ScriptUploadForm(request.POST, request.FILES, instance=task)
            next_status = 'writing_complete'
        elif profile.role == 'producer':
            form = VideoUploadForm(request.POST, request.FILES, instance=task)
            next_status = 'producing_complete'
        else:
            form = ThumbnailUploadForm(request.POST, request.FILES, instance=task)
            next_status = 'done'
        if form.is_valid():
            form.save()
            task.status = next_status
            task.save()
        return redirect('main:employee_dashboard')

    task = None
    if profile.role == 'writer':
        task = Project.objects.filter(assigned_writer=profile, status='writing_in_progress').first()
        if not task:
            task = Project.objects.filter(status='unassigned', priority='high', assigned_writer__isnull=True).first()
            if task:
                task.assigned_writer = profile
                task.status = 'writing_in_progress'
                task.save()
    elif profile.role == 'producer':
        task = Project.objects.filter(assigned_producer=profile, status='producing_in_progress').first()
        if not task:
            task = Project.objects.filter(status='writing_complete', priority='high', assigned_producer__isnull=True).first()
            if task:
                task.assigned_producer = profile
                task.status = 'producing_in_progress'
                task.save()
    else:  # compiler
        task = Project.objects.filter(assigned_compiler=profile, status='compiling_in_progress').first()
        if not task:
            task = Project.objects.filter(status='producing_complete', priority='high', assigned_compiler__isnull=True).first()
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
        if profile.role == 'writer' and task.assigned_writer is None:
            task.assigned_writer = profile
            task.status = 'writing_in_progress'
            task.save()
        elif profile.role == 'producer' and task.assigned_producer is None and task.status == 'writing_complete':
            task.assigned_producer = profile
            task.status = 'producing_in_progress'
            task.save()
        elif profile.role == 'compiler' and task.assigned_compiler is None and task.status == 'producing_complete':
            task.assigned_compiler = profile
            task.status = 'compiling_in_progress'
            task.save()
        return redirect('main:freelancer_dashboard')

    task = None
    available_tasks = []
    if profile.role == 'writer':
        task = Project.objects.filter(assigned_writer=profile).first()
        if not task:
            available_tasks = Project.objects.filter(assigned_writer__isnull=True, priority='low')
    elif profile.role == 'producer':
        task = Project.objects.filter(assigned_producer=profile).first()
        if not task:
            available_tasks = Project.objects.filter(
                assigned_producer__isnull=True, priority='low', status='writing_complete'
            )
    else:  # compiler
        task = Project.objects.filter(assigned_compiler=profile).first()
        if not task:
            available_tasks = Project.objects.filter(
                assigned_compiler__isnull=True, priority='low', status='producing_complete'
            )

    task_forms = []
    if task:
        if profile.role == 'writer':
            form = ScriptUploadForm(instance=task)
        elif profile.role == 'producer':
            form = VideoUploadForm(instance=task)
        else:
            form = ThumbnailUploadForm(instance=task)
        task_forms.append((task, form))

    return render(request, 'main/freelancer_dashboard.html', {
        'task': task,
        'available_tasks': available_tasks,
        'task_forms': task_forms
    })

@login_required
def logout_user(request):
    logout(request)
    return redirect('/')
