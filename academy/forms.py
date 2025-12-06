from django import forms
from django.contrib.auth.models import User
from .models import Profile

# Форма для зміни даних користувача (ім'я, прізвище, email)
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

# Форма для зміни даних профілю (аватар, біографія, дата народження)
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'bio', 'birth_date']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}) # Щоб був календарик
        }