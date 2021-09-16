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
    # Authentication APIs
    path("teacher/login", views_auth.teacher_login),
    path("teacher/register", views_auth.teacher_registeration),
    path("teacher/verify/<secret_code>/<teacher_id>", views_auth.teacher_verify_email),
    path("student/login", views_auth.student_login),
    path("student/register", views_auth.student_registeration),
    path("student/verify/<secret_code>/<student_id>", views_auth.student_verify_email),
    # Teacher APIs
    path("teacher/profile", views_teacher.get_teacher_profile),
    path("teacher/exam", views_teacher.create_exam),
    path("teacher/exam/_all", views_teacher.get_all_exams),
    path("teacher/exam/<exam_id>", views_teacher.delete_exam),
    path("teacher/results/<exam_id>", views_teacher.get_batch_result),
    path("teacher/results/<exam_id>/<student_id>", views_teacher.get_student_result),
    # Student APIs
    path("student/profile", views_student.get_student_profile),
    path("student/exam/undone_exams", views_student.get_undone_exams),
    path("student/exam/<exam_id>", views_student.get_exam_questions),
    path("student/exam/<exam_id>/_info", views_student.get_exam_info),
    path("student/results/<exam_id>", views_student.get_student_result),
    path("student/exam/<exam_id>/evaluate", views_student.evaluate_exams),
]
