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
