from django.urls import path
from main import views

app_name = 'main'

urlpatterns = [
    path('', views.redirect_to_dashboard, name="redirect_to_dashboard"),
    path('admin_dashboard/', views.admin_dashboard, name="admin_dashboard"),
    path('employee_dashboard/', views.employee_dashboard, name="employee_dashboard"),
    path('freelancer_dashboard/', views.freelancer_dashboard, name="freelancer_dashboard"),
    path('archives', views.archives, name="archives"),
    path('logout/', views.logout_user, name="logout")
]