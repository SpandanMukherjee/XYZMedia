from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from users.models import UserProfile
from projects.models import Project
from projects.forms import ScriptUploadForm, VideoUploadForm, ThumbnailUploadForm

@login_required
def redirect_to_dashboard(request):
    if request.user.userprofile.user_type == 'admin':
        return admin_dashboard(request)
    elif request.user.userprofile.user_type == 'employee':
        return employee_dashboard(request)
    elif request.user.userprofile.user_type == 'freelancer':
        return freelancer_dashboard(request)
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
    task = None

    if profile.role == 'writer':
        task = Project.objects.filter(status='unassigned', priority='high', assigned_writer__isnull=True).first()

        if task:
            task.assigned_writer = profile
            task.status = 'writing_in_progress'
            task.save()

    elif profile.role == 'producer':
        task = Project.objects.filter(status='writing_complete', priority='high', assigned_producer__isnull=True).first()

        if task:
            task.assigned_producer = profile
            task.status = 'producing_in_progress'
            task.save()

    elif profile.role == 'compiler':
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
        elif profile.role == 'compiler':
            form = ThumbnailUploadForm(instance=task)

        task_forms.append((task, form))

    if request.method == 'POST' and task:

        if profile.role == 'writer':
            form = ScriptUploadForm(request.POST, request.FILES, instance=task)
        elif profile.role == 'producer':
            form = VideoUploadForm(request.POST, request.FILES, instance=task)
        elif profile.role == 'compiler':
            form = ThumbnailUploadForm(request.POST, request.FILES, instance=task)

        if form.is_valid():
            form.save()

            # Update task status after form submission
            if profile.role == 'writer':
                task.status = 'writing_complete'  # Change to 'writing_complete' after script upload
            elif profile.role == 'producer':
                task.status = 'producing_complete'  # Change to 'producing_complete' after video upload
            elif profile.role == 'compiler':
                task.status = 'done'  # Change to 'done' after thumbnail upload

            task.save()

            return employee_dashboard(request)

    return render(request, 'main/employee_dashboard.html', {
        'task_forms': task_forms
    })

def freelancer_dashboard(request):
    profile = request.user.userprofile
    tasks = []

    if not profile.is_approved:
        return render(request, 'main/freelancer_pending_dashboard.html')

    if profile.role == 'writer':
        tasks = Project.objects.filter(assigned_writer=profile)
    elif profile.role == 'producer':
        tasks = Project.objects.filter(assigned_producer=profile)

    return render(request, 'main/freelancer_dashboard.html', {'tasks': tasks})

@login_required
def logout_user(request):
    logout(request)
    return redirect('/')
