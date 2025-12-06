from django import forms
from .models import Course, Test


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Назва курсу'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Опис курсу'}),
        }


class TestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = ['name', 'duration']  # max_score порахуємо самі
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Назва тесту'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Хвилин'}),
        }


# Форма для питання + 4 варіанти відповідей
class QuestionForm(forms.Form):
    question_text = forms.CharField(
        max_length=500,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Текст питання'})
    )

    option_1 = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Варіант А'}))
    option_2 = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Варіант B'}))
    option_3 = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Варіант C'}))
    option_4 = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Варіант D'}))

    CORRECT_CHOICES = [('1', 'А'), ('2', 'B'), ('3', 'C'), ('4', 'D')]
    correct_answer = forms.ChoiceField(
        choices=CORRECT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )