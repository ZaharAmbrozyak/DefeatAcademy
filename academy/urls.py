from django.urls import path
from . import views

app_name = 'academy'
urlpatterns = [
    path('', views.index, name='index'),
    path('courses/', views.courses, name='courses'),
    path('courses/<int:course_id>/', views.course, name='course'),
    path('test/<int:course_id>/<int:test_id>/', views.test, name='test'),

    # --- НОВИЙ РЯДОК ---
    path('profile/', views.profile, name='profile'),
    path('profile/', views.profile, name='profile'),          # Тільки перегляд
    path('profile/edit/', views.edit_profile, name='edit_profile'),
]