from django.urls import path
from main import views

app_name = 'main'

urlpatterns = [
    path('', views.redirect_to_dashboard, name="redirect_to_dashboard"),
    path('logout/', views.logout_user, name="logout")
]