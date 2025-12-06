from django.contrib import admin
from .models import Course, Test, Choice, Question
# Register your models here.

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4

class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]

admin.site.register(Course)
admin.site.register(Test)
admin.site.register(Question, QuestionAdmin)