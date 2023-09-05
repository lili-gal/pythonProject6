from django.contrib.auth.views import LoginView, LogoutView
from django.urls import  path
from django.views.generic import TemplateView

from users.views import RegisterView, EmailVerify, MyLoginView

app_name = 'users'

urlpatterns = [
    path('login/', MyLoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('register/', RegisterView.as_view(template_name='users/register.html'), name='register'),
    path('confirm_email/', TemplateView.as_view(template_name='users/confirm.html'), name='confirm_email'),
    path('verify_email/<uidb64>/<token>/', EmailVerify.as_view(), name='verify_email'),
    path('invalid_verify/', TemplateView.as_view(template_name='users/invalid_verify.html'), name='invalid_verify')
]