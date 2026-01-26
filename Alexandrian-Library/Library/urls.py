from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "Library"

urlpatterns = [
    path("", views.course_list, name="home"),

    path("accounts/login/", auth_views.LoginView.as_view(template_name="Library/auth/login.html"), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(next_page="Library:home"), name="logout"),
    path("accounts/register/", views.register, name="register"),
]