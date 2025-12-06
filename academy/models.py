from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Course(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=1000)

    def __str__(self):
        return self.name

class Test(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    max_score = models.PositiveIntegerField(default=100)

    duration = models.PositiveIntegerField(default=20, help_text='Хв')
    def __str__(self):
        return self.name

class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField(max_length=200)

    def __str__(self):
        return self.text

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text

class Result(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.FloatField()      # Кількість правильних відповідей
    percentage = models.FloatField() # Відсоток успішності
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.test.name}: {self.percentage}%"
