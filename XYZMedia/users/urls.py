from django.urls import path
from users import views
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy

app_name = 'users'

class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'users/change_password.html'
    success_url = '/'

urlpatterns = [
    path('register/', views.register_user, name="register"),
    path('create_employee/', views.create_employee, name="create_employee"),
    path('approve/<int:id>', views.approve_freelancer, name='approve_freelancer'),
    path('reject_freelancer/<int:id>', views.reject_freelancer, name='reject_freelancer'),
    path('change_password/', CustomPasswordChangeView.as_view(), name='change_password'),
]