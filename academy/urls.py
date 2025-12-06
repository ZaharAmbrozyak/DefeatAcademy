from django.urls import path

from . import views

app_name = 'academy'
urlpatterns = [
    path('', views.index, name='index'),
    path('courses/', views.courses, name='courses'),
    path('courses/<int:course_id>/', views.course, name='course'),
    path('test/<int:course_id>/<int:test_id>/', views.test, name='test'),
    path('profile/', views.profile, name='profile'),
    # path('training/', views.training_mode_view, name='training_mode'),

    path('create-course/', views.create_course, name='create_course'),
    path('course/<int:course_id>/create-test/', views.create_test, name='create_test'),
    path('test/<int:test_id>/add-question/', views.add_question, name='add_question'),
]