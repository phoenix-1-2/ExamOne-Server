from django.db import models
import uuid

from django.db.models.fields import URLField

# Create your models here.


class Teacher(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=200)
    password = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    image_url = models.URLField(max_length=200)
    date_of_birth = models.DateField()
    education_qualification = models.JSONField()


class Student(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=200)
    password = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    batch = models.CharField(max_length=10)
    image_url = models.URLField(max_length=200)
    date_of_birth = models.DateField()
    education_qualification = models.JSONField()


class Exam(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    examination_name = models.CharField(max_length=200)
    batch = models.CharField(max_length=10)
    questions_and_solutions = models.JSONField()
    total_marks = models.DecimalField(max_digits=5, decimal_places=2)
    exam_period = models.TimeField()
    expiry_date = models.DateTimeField()


class Result(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exam_start_date_time = models.DateTimeField()
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    student_solutions = models.JSONField(default=dict)
    total_marks = models.DecimalField(max_digits=5, decimal_places=2)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    grade = models.CharField(max_length=10)
