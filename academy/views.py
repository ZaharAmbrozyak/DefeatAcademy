import time
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.db.models import Avg
from .models import Course, Test, Choice, Result

# Create your views here.
def index(request):
    return render(request, 'academy/index.html')

def courses(request):
    courses = Course.objects.all()
    context = {'courses': courses}
    return render(request, 'academy/courses.html', context)

def course(request, course_id):
    course = Course.objects.get(id=course_id)
    tests  = course.test_set.all()
    context = {'course': course, 'tests': tests}
    return render(request, 'academy/course.html', context)


@login_required
def test(request, course_id, test_id):
    test = get_object_or_404(Test, id=test_id, course__id=course_id)

    # КЛЮЧ СЕСІЇ: Унікальний для кожного юзера і кожного тесту
    session_key = f'test_start_time_{request.user.id}_{test.id}'

    # Якщо це POST (користувач відправляє відповіді)
    if request.method == 'POST':
        # 1. Видаляємо час початку з сесії (щоб можна було потім перездати)
        if session_key in request.session:
            del request.session[session_key]

        score = 0
        total_questions = test.questions.count()

        for question in test.questions.all():
            selected_choice_id = request.POST.get(f'question_{question.id}')
            if selected_choice_id:
                choice = Choice.objects.filter(id=selected_choice_id).first()
                if choice and choice.is_correct:
                    score += 1

        if total_questions > 0:
            percentage = (score / total_questions) * 100
        else:
            percentage = 0

        Result.objects.create(
            test=test, user=request.user, score=score, percentage=percentage
        )

        return render(request, 'academy/test.html', {
            'test': test,
            'score': score,
            'total_questions': total_questions,
            'percentage': round(percentage, 1),
            'show_results': True,
        })

    else:
        if session_key not in request.session:
            request.session[session_key] = time.time()

        start_time = request.session[session_key]
        elapsed_time = time.time() - start_time
        total_duration_seconds = test.duration * 60

        seconds_left = total_duration_seconds - elapsed_time

        if seconds_left < 0:
            seconds_left = 0

        context = {
            'test': test,
            'seconds_left': int(seconds_left)  # Передаємо це в шаблон
        }
        return render(request, 'academy/test.html', context)
@login_required
def profile(request):
    user = request.user

    user_results = Result.objects.filter(user=user).order_by('-created_at')

    total_tests_taken = user_results.count()

    stats = user_results.aggregate(Avg('percentage'))
    average_score = stats['percentage__avg']

    if average_score is None:
        average_score = 0

    context = {
        'results': user_results,
        'total_tests_taken': total_tests_taken,
        'average_score': round(average_score, 1),
    }

    return render(request, 'academy/profile.html', context)
