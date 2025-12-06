from django.contrib import admin
from .models import Course, Test, Choice, Question, Profile # <-- Додали Profile в імпорт

# --- Налаштування для Тестів та Питань (Твій код) ---
class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4

class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]

# --- Налаштування для Профілю (Нове) ---
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'bio', 'birth_date'] # Що показувати в таблиці списку
    search_fields = ['user__username', 'user__email'] # Пошук по юзернейму
    filter_horizontal = ['courses'] # <-- Зручне вікно для вибору курсів (ліво-право)

# --- Реєстрація моделей ---
admin.site.register(Course)
admin.site.register(Test)
admin.site.register(Question, QuestionAdmin)
# Profile ми вже зареєстрували через декоратор @admin.register вище