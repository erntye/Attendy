from django.contrib.auth.models import User
from django.db import models


class Classroom(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=10)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.name) + " (" + self.code + ")"


class Student(models.Model):
    email = models.CharField(max_length=200)
    studentID = models.CharField(max_length=100)

    def __str__(self):
        return str(self.studentID)

class ClassList(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, null=True)

class ClassTime(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    day = models.CharField(max_length=100)
    semester = models.CharField(max_length=100)
    year = models.CharField(max_length=100)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    session = models.IntegerField(default=0)
    confidence_score = models.IntegerField(default=0)
    status = models.CharField(max_length=10, default=None)
    ip = models.CharField(max_length=100, default=None)
    offset = models.CharField(max_length=100, default=None)
    song_name = models.CharField(max_length=100, default=None)
    offset_seconds = models.CharField(max_length=100, default=None)
    match_time = models.CharField(max_length=100, default=None)
    time_in = models.DateTimeField(null=True)
    dejavu_log = models.TextField(default=None)

class StudentInbound(models.Model):
    studentID =  models.CharField(max_length=100)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    session = models.IntegerField(default=0)
    time_in = models.DateTimeField(null=True)

class InstructorInbound(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    session = models.IntegerField(default=0)
    time_in = models.DateTimeField(null=True)