from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Course, Test
from .forms import UserUpdateForm, ProfileUpdateForm


# Create your views here.
def index(request):
    return render(request, 'academy/index.html')


def courses(request):
    courses = Course.objects.all()
    context = {'courses': courses}
    return render(request, 'academy/courses.html', context)


def course(request, course_id):
    course = Course.objects.get(id=course_id)
    tests = course.test_set.all()
    context = {'course': course, 'tests': tests}
    return render(request, 'academy/course.html', context)


def test(request, course_id, test_id):
    test = Test.objects.get(id=test_id, course__id=course_id)
    context = {'test': test}
    return render(request, 'academy/test.html', context)


# --- 1. ТІЛЬКИ ПЕРЕГЛЯД ---
@login_required
def profile(request):
    # Тут ми нічого не зберігаємо, просто показуємо сторінку
    return render(request, 'academy/profile.html')


# --- 2. РЕДАГУВАННЯ (НАЛАШТУВАННЯ) ---
@login_required
def edit_profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Ваші налаштування збережено!')
            # Після збереження повертаємо користувача на сторінку перегляду профілю
            return redirect('academy:profile')

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'academy/edit_profile.html', context)