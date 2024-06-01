from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from datetime import datetime, timedelta

def now_plus_time(time):
    return datetime.now() + timedelta(days=time)

# Create your models here.
class Student(AbstractUser):
    studentId = models.CharField(max_length=20, unique=True, null=True)
    fullname = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=30, default='student')
    courses = models.ManyToManyField('Course', related_name='students')
    username = None
    
    USERNAME_FIELD = 'studentId'
    REQUIRED_FIELDS = []
    
    
class Assignment(models.Model):
    title = models.CharField(max_length=255)
    key = models.TextField(default='', null=True)
    question = ArrayField(models.TextField(), blank=True, null=True)
    answer = ArrayField(models.TextField(), blank=True, null=True)
    user_answer = ArrayField(models.TextField(), blank=True, null=True)
    result = ArrayField(models.TextField(), blank=True, null=True)
    status = models.TextField(default='Pending', null=True)
    url = models.TextField(default='', null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    due_date = models.DateTimeField(default=now_plus_time(10))
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='questions', null=True)
    courses = models.ManyToManyField('Course', related_name='assignments')
    
    def __str__(self):
        return self.title

class Course(models.Model):
    title = models.CharField(max_length=255)
    course_code = models.CharField(max_length=20, unique=True, default='')
    
    def __str__(self):
        return self.title
    