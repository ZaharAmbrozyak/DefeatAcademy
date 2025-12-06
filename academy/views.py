import time
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Avg
from .models import Course, Test, Choice, Result, Question
from django.contrib import messages
# from .services import calculate_confidence_score, get_ai_tutor_feedback
from .forms import CourseForm, TestForm, QuestionForm

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

# SESSION_QUEUE = 'training_queue'
# SESSION_INDEX = 'current_question_index'
# SESSION_SCORE = 'current_score'
# SESSION_FEEDBACK = 'ai_feedback_context'


# @require_http_methods
# def training_mode_view(request):
#     """
#     Основне представлення для режиму тренування.
#     Керує життєвим циклом сесії тестування.
#     """
#
#     # 1. Ініціалізація сесії (Якщо це перший захід або рестарт)
#     if SESSION_QUEUE not in request.session:
#         # Вибираємо 10 випадкових питань.
#         # Зверніть увагу: ми беремо лише ID, щоб уникнути проблем серіалізації.[5]
#         questions_queryset = Question.objects.all().order_by('?')[:10]
#         if not questions_queryset.exists():
#             messages.error(request, "У базі даних відсутні питання.")
#             return redirect('home')  # Припускаємо наявність url 'home'
#
#         request.session = list(questions_queryset.values_list('id', flat=True))
#         request.session = 0
#         request.session = 0
#         request.session = None  # Для збереження стану між POST і GET
#
#     # Отримання даних з сесії
#     queue = request.session.get(SESSION_QUEUE, )
#     index = request.session.get(SESSION_INDEX, 0)
#     score = request.session.get(SESSION_SCORE, 0)
#
#     # Перевірка завершення тесту
#     if index >= len(queue):
#         # Очищення сесії після завершення
#         final_score = score
#         total_questions = len(queue)
#         request.session.flush()  # Або видалити конкретні ключі
#         return render(request, 'training_complete.html', {
#             'score': final_score,
#             'total': total_questions
#         })
#
#     # Завантаження об'єкта поточного питання
#     current_question_id = queue[index]
#     question = get_object_or_404(Question, id=current_question_id)
#     choices = question.choice_set.all()  # Припускаємо related_name за замовчуванням
#
#     # 2. Обробка POST запиту (Дії користувача)
#     if request.method == "POST":
#
#         # Сценарій А: Користувач натиснув "Підтвердити відповідь"
#         if 'submit_answer' in request.POST:
#             selected_choice_id = request.POST.get('choice')
#
#             # Валідація вибору
#             if not selected_choice_id:
#                 messages.warning(request, "Будь ласка, оберіть варіант відповіді.")
#                 # Повертаємо сторінку без змін
#                 return render(request, 'training_card.html', {
#                     'question': question,
#                     'choices': choices,
#                     'score': score,
#                     'index': index + 1,
#                     'total': len(queue)
#                 })
#
#             choice = get_object_or_404(Choice, id=selected_choice_id)
#
#             if choice.is_correct:
#                 # Правильна відповідь
#                 points = calculate_confidence_score(is_correct=True)
#                 request.session += points
#                 messages.success(request, f"Правильно! +{points} балів.")
#
#                 # Перехід до наступного питання
#                 request.session += 1
#                 request.session = None
#                 return redirect('training_mode')  # PRG Pattern [14]
#
#             else:
#                 # Неправильна відповідь -> Виклик AI Tutor
#                 messages.error(request, "Неправильно. Див. пояснення нижче.")
#
#                 correct_choice = choices.filter(is_correct=True).first()
#                 correct_text = correct_choice.text if correct_choice else "Невідомо"
#
#                 # Виклик сервісу
#                 feedback = get_ai_tutor_feedback(
#                     question_text=question.text,
#                     user_answer=choice.text,
#                     correct_answer=correct_text
#                 )
#
#                 # Зберігаємо фідбек в сесії, щоб відобразити його при рендері
#                 # Індекс питання НЕ збільшуємо, даємо користувачу прочитати
#                 request.session = feedback
#                 return redirect('training_mode')  # Перезавантаження для відображення стану
#
#         # Сценарій Б: Користувач натиснув "Наступне питання" (або "Пропустити")
#         elif 'next_question' in request.POST:
#             request.session += 1
#             request.session = None  # Очищуємо старий фідбек
#             return redirect('training_mode')
#
#     # 3. Обробка GET запиту (Рендеринг сторінки)
#     # Перевіряємо, чи є збережений AI-фідбек з попереднього кроку
#     ai_feedback = request.session.get(SESSION_FEEDBACK)
#
#     context = {
#         'question': question,
#         'choices': choices,
#         'score': score,
#         'index': index + 1,
#         'total': len(queue),
#         'ai_feedback': ai_feedback,  # Передаємо в шаблон
#     }
#
#     return render(request, 'training_card.html', context)


@login_required
def create_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.author = request.user  # Прив'язуємо до автора
            course.save()
            return redirect('academy:course', course_id=course.id)
    else:
        form = CourseForm()
    return render(request, 'academy/create_course.html', {'form': form})


@login_required
def create_test(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    # Перевірка: тільки автор може додавати тести
    if course.author != request.user:
        return redirect('academy:course', course_id=course.id)

    if request.method == 'POST':
        form = TestForm(request.POST)
        if form.is_valid():
            test = form.save(commit=False)
            test.course = course
            test.max_score = 0  # Поки що 0, будемо збільшувати при додаванні питань
            test.save()
            # Одразу йдемо додавати питання
            return redirect('academy:add_question', test_id=test.id)
    else:
        form = TestForm()
    return render(request, 'academy/create_test.html', {'form': form, 'course': course})


@login_required
def add_question(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    if test.course.author != request.user:
        return redirect('academy:index')

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            # 1. Створюємо питання
            q_text = form.cleaned_data['question_text']
            question = Question.objects.create(test=test, text=q_text)

            # 2. Збільшуємо макс. бал тесту
            test.max_score += 1
            test.save()

            # 3. Створюємо варіанти відповідей
            correct_num = form.cleaned_data['correct_answer']  # '1', '2', '3' або '4'

            options = [
                form.cleaned_data['option_1'],
                form.cleaned_data['option_2'],
                form.cleaned_data['option_3'],
                form.cleaned_data['option_4']
            ]

            for i, text in enumerate(options, start=1):
                Choice.objects.create(
                    question=question,
                    text=text,
                    is_correct=(str(i) == correct_num)
                )

            # Перезавантажуємо сторінку, щоб додати ще одне питання
            return redirect('academy:add_question', test_id=test.id)
    else:
        form = QuestionForm()

    return render(request, 'academy/add_question.html', {'form': form, 'test': test})
