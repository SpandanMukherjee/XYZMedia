from django.urls import path
from users import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register_user, name="register"),
    path('create_employee/', views.create_employee, name="create_employee"),
    path('approve/<int:id>', views.approve_freelancer, name='approve_freelancer'),
    path('reject_freelancer/<int:id>', views.reject_freelancer, name='reject_freelancer'),
]