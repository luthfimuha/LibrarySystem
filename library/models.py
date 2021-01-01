from django.db import models

# Create your models here.
class Student(models.Model):
    studentID = models.CharField(max_length=20)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    username = models.CharField(max_length=30, unique=True)
    password = models.CharField(max_length=30)
    major = models.CharField(max_length=30)
    gender = models.BooleanField(default=False)
    photo = models.ImageField(upload_to='images',null=True)


class Book(models.Model):
    name = models.CharField(max_length=200)
    desc = models.TextField()
    author = models.CharField(max_length=50)
    pub_date = models.DateField()
    type = models.CharField(max_length=50)
    stock = models.IntegerField()
    cover = models.ImageField(upload_to='images/cover',null=True)

class Borrow(models.Model):
    borrowed_date = models.DateField()
    due_date = models.DateField()
    status = models.CharField(max_length=50)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)


