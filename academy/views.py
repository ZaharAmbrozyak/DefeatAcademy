from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Course, Test, Choice
from .forms import UserUpdateForm, ProfileUpdateForm


def index(request):
    return render(request, 'academy/index.html')


def courses(request):
    courses = Course.objects.all()
    context = {'courses': courses}
    return render(request, 'academy/courses.html', context)


def course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    tests = course.test_set.all()
    context = {'course': course, 'tests': tests}
    return render(request, 'academy/course.html', context)


@login_required
def test(request, course_id, test_id):
    test = get_object_or_404(Test, id=test_id, course__id=course_id)
    profile = request.user.profile

    result_message = None
    winnings = 0
    # Перевіряємо статус
    is_on_leave = (profile.status == "Академка")

    if request.method == 'POST':
        try:
            bet_amount = int(request.POST.get('bet_amount', 0))
        except (ValueError, TypeError):
            bet_amount = 0

        # Ми дозволяємо ставити більше, ніж є (щоб йти в мінус).
        # Єдиний захист: не можна ставити мінусові числа (чітерство).
        if bet_amount < 0:
            messages.error(request, "Ставка не може бути від'ємною!")
            return redirect('academy:test', course_id=course_id, test_id=test_id)

        # Перевірка відповідей
        questions = test.questions.all()
        all_correct = True

        if not questions.exists():
            all_correct = False

        for question in questions:
            selected_choice_id = request.POST.get(f'question_{question.id}')
            if selected_choice_id:
                choice = Choice.objects.get(id=selected_choice_id)
                if not choice.is_correct:
                    all_correct = False
                    break
            else:
                all_correct = False
                break

        # Нарахування
        if all_correct:
            winnings = bet_amount
            profile.currency += winnings
            result_message = "win"
        else:
            profile.currency -= bet_amount  # Дозволяємо йти в мінус
            result_message = "loss"

        profile.save()  # Оновлюємо статус

        if profile.currency < 0:
            is_on_leave = True

    context = {
        'test': test,
        'result_message': result_message,
        'winnings': winnings,
        'is_on_leave': is_on_leave,
    }

    return render(request, 'academy/test.html', context)


@login_required
def profile(request):
    return render(request, 'academy/profile.html')


@login_required
def edit_profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Ваші налаштування збережено!')
            return redirect('academy:profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'academy/edit_profile.html', context)