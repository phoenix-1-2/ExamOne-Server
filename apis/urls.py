"""examone URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from .views import views_auth, views_student, views_teacher

urlpatterns = [
    path("teacher/login", views_auth.teacher_login),
    path("teacher/register", views_auth.teacher_registeration),
    path("teacher/verify/<secret_code>/<teacher_id>", views_auth.teacher_verify_email),
    path("student/login", views_auth.student_login),
    path("student/register", views_auth.student_registeration),
    path("student/verify/<secret_code>/<student_id>", views_auth.student_verify_email),
]
