import os
from openai import OpenAI
from dotenv import load_dotenv

# Завантаження змінних середовища (рекомендований спосіб)
# Переконайтеся, що у вас є файл.env з рядком: GROQ_API_KEY=gsk_...
load_dotenv()

# Ініціалізація клієнта
# Ми використовуємо клас OpenAI, але перенаправляємо його на сервери Groq
client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),  # Ваш ключ gsk_...
    base_url="https://api.groq.com/openai/v1"  # Ключовий елемент: адреса API Groq
)


def get_groq_response(user_query):
    try:
        completion = client.chat.completions.create(
            # Вибір моделі. Список актуальних моделей:
            # - llama-3.3-70b-versatile (баланс інтелекту та швидкості)
            # - llama-3.1-8b-instant (максимальна швидкість)
            # - mixtral-8x7b-32768 (велике контекстне вікно)
            model="llama-3.3-70b-versatile",

            messages=[
                {
                    "role": "system",
                    "content": "Ти - корисний асистент, що відповідає українською мовою."
                },
                {
                    "role": "user",
                    "content": user_query
                }
            ],
            temperature=0.7,  # Креативність відповіді (0.0 - точна, 1.0 - творча)
        )
        return completion.choices.message.content
    except Exception as e:
        return f"Помилка API: {str(e)}"


# Тестовий виклик
if __name__ == "__main__":
    print(get_groq_response("Поясни, що таке LPU простими словами?"))