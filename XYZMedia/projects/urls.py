from django.urls import path
from projects import views

app_name = 'projects'

urlpatterns = [
    path('create/', views.create_project, name='create_project'),
]
