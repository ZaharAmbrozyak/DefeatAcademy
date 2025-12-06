import os
import logging
from openai import OpenAI, OpenAIError, RateLimitError, APIConnectionError

# Налаштування логування для відстеження проблем у продакшн середовищі
logger = logging.getLogger(__name__)

# Спроба ініціалізації клієнта.
# Використання змінних середовища є критичним для безпеки.[7, 8]
# Рекомендується використовувати бібліотеку python-dotenv у manage.py або settings.py
try:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        logger.warning("OPENAI_API_KEY not found in environment variables.")
        client = None
    else:
        client = OpenAI(api_key=api_key)
except Exception as e:
    logger.error(f"Failed to initialize OpenAI client: {e}")
    client = None


def calculate_confidence_score(is_correct: bool, difficulty: int = 1) -> int:
    """
    Розраховує бал 'Confidence Score' за відповідь.

    Ця функція інкапсулює логіку нарахування балів, дозволяючи легко
    змінювати алгоритм (наприклад, додавати бонуси за складність)
    без змін у views.py.

    Args:
        is_correct (bool): Чи є відповідь правильною.
        difficulty (int): Рівень складності питання (за замовчуванням 1).

    Returns:
        int: Кількість нарахованих балів.
    """
    if not is_correct:
        return 0

    # Базова логіка: 10 балів за правильну відповідь * коефіцієнт складності
    base_points = 10
    return base_points * difficulty


def get_ai_tutor_feedback(question_text: str, user_answer: str, correct_answer: str) -> str:
    """
    Викликає OpenAI API (gpt-4o-mini) для отримання пояснення помилки.

    Використовує chat completions API для генерації короткого
    педагогічного коментаря.

    Args:
        question_text (str): Текст питання.
        user_answer (str): Текст відповіді, яку обрав користувач.
        correct_answer (str): Текст правильної відповіді.

    Returns:
        str: Пояснення від AI або повідомлення про помилку сервісу.
    """
    if not client:
        return "AI Tutor недоступний (відсутній API ключ)."

    # Формування контексту для моделі.
    # Використовуємо роль 'system' для налаштування тону.
    messages = [
        {
            "role": "system",
            "content": "Ти досвідчений ментор з програмування. Користувач помилився у тесті. "
                       "Поясни коротко (максимум 2-3 речення), чому його відповідь неправильна, "
                       "і натякни на правильну логіку. Не давай прямої відповіді, якщо це можливо."
        },
        {
            "role": "user",
            "content": f"Питання: {question_text}\n"
                       f"Відповідь користувача: {user_answer}\n"
                       f"Правильна відповідь: {correct_answer}"
        }
    ]

    try:
        # Виклик gpt-4o-mini як найбільш ефективної моделі для цього завдання [3]
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=150,  # Обмеження довжини відповіді для економії токенів
            temperature=0.7,  # Баланс між креативністю та точністю
        )
        return response.choices.message.content.strip()

    except RateLimitError:
        logger.error("OpenAI Rate Limit exceeded.")
        return "AI Tutor перевантажений. Спробуйте пізніше."
    except APIConnectionError:
        logger.error("OpenAI Network Error.")
        return "Проблема з підключенням до AI сервісу."
    except OpenAIError as e:
        # Загальний перехоплювач помилок бібліотеки OpenAI [9]
        logger.error(f"OpenAI General Error: {e}")
        return "Виникла помилка при генерації пояснення."
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return "Невідома помилка сервісу."