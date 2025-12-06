import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from academy.models import Course, Test, Question, Choice

# Кількість питань в одному тесті
QUESTIONS_PER_TEST = 10


class Command(BaseCommand):
    help = 'Imports questions from a JSON file'

    def add_arguments(self, parser):
        # Шлях до файлу є обов'язковим аргументом
        parser.add_argument('path', type=str, help='Path to the JSON file')

        # ID курсу - необов'язковий. Якщо не вказати, створить новий курс.
        parser.add_argument('--course-id', type=int, help='ID of an existing course')

    def handle(self, *args, **options):
        file_path = options['path']
        course_id = options.get('course_id')

        # 1. Знаходимо або створюємо курс
        if course_id:
            try:
                course = Course.objects.get(id=course_id)
                self.stdout.write(f"Додаємо тести до курсу: {course.name}")
            except Course.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Курс з ID {course_id} не знайдено."))
                return
        else:
            course, created = Course.objects.get_or_create(
                name="General Quiz",
                defaults={"description": "Автоматично імпортований курс з JSON"}
            )
            if created:
                self.stdout.write(f"Створено новий курс: {course.name}")

        # 2. Відкриваємо файл
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"Файл не знайдено: {file_path}"))
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        total_questions = len(data)
        self.stdout.write(f"Знайдено {total_questions} питань. Починаємо імпорт...")

        # 3. Розбиваємо на тести
        test_number = 1
        # Рахуємо, скільки тестів вже є в цьому курсі, щоб продовжити нумерацію (Test 1, Test 2...)
        existing_tests_count = Test.objects.filter(course=course).count()
        test_number = existing_tests_count + 1

        for start in range(0, total_questions, QUESTIONS_PER_TEST):
            end = start + QUESTIONS_PER_TEST
            chunk = data[start:end]

            # Створюємо тест
            # ВАЖЛИВО: max_score ставимо рівним кількості питань (наприклад, 10)
            test = Test.objects.create(
                course=course,
                name=f"Test {test_number}",
                max_score=len(chunk),
                duration=15  # Можна задати час за замовчуванням
            )

            self.stdout.write(f"  -> Створено {test.name} ({len(chunk)} питань)")

            # Додаємо питання
            for item in chunk:
                question_text = item["question"]

                # Перевірка на довжину тексту, щоб не було крашу
                if len(question_text) > 200:
                    self.stdout.write(self.style.WARNING(f"    ⚠️ Питання задовге, обрізаємо: {question_text[:50]}..."))
                    # Якщо ви не збільшили моделі, це врятує від крашу, але краще збільшити моделі!
                    # question_text = question_text[:200]

                question = Question.objects.create(
                    test=test,
                    text=question_text
                )

                for letter in ["A", "B", "C", "D"]:
                    choice_text = item.get(letter, "")
                    if choice_text:
                        Choice.objects.create(
                            question=question,
                            text=choice_text,
                            is_correct=(letter == item["answer"])
                        )

            test_number += 1

        self.stdout.write(self.style.SUCCESS("✅ Імпорт завершено успішно!"))