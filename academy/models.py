from django.db import models
from django.contrib.auth.models import User  # <-- Додано для зв'язку з User
from django.db.models.signals import post_save  # <-- Додано для сигналів
from django.dispatch import receiver  # <-- Додано для сигналів



# --- Твої існуючі моделі ---

class Course(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=1000)

    def __str__(self):
        return self.name


class Test(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    max_score = models.PositiveIntegerField(default=100)

    def __str__(self):
        return self.name


class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField(max_length=200)

    def __str__(self):
        return self.text


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


# --- НОВА ЧАСТИНА: ПРОФІЛЬ ---

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    avatar = models.ImageField(default='default.png', upload_to='profile_avatars', verbose_name="Аватар")
    bio = models.TextField(max_length=500, blank=True, verbose_name="Про себе")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Дата народження")

    level = models.PositiveIntegerField(default=0, verbose_name="Рівень")
    xp = models.PositiveIntegerField(default=0, verbose_name="XP")  # Поточний досвід на цьому рівні
    currency = models.PositiveIntegerField(default=0, verbose_name="Монети")
    status = models.CharField(max_length=100, default="Новонароджений", verbose_name="Статус")

    courses = models.ManyToManyField('Course', blank=True, related_name='students')

    # --- ЛОГІКА ЛЕВЕЛІНГА ---

    def get_next_level_threshold(self):
        """
        Формула: скільки XP треба для наступного рівня.
        Наприклад: 100 * (рівень + 1).
        0 рівень -> треба 100 xp
        1 рівень -> треба 200 xp
        """
        return (self.level + 1) * 100

    def add_xp(self, amount):
        """
        Метод для додавання досвіду з автоматичним підвищенням рівня
        """
        self.xp += amount

        while True:
            threshold = self.get_next_level_threshold()
            if self.xp >= threshold:
                self.xp -= threshold  # Віднімаємо витрачений досвід
                self.level += 1  # Піднімаємо рівень
                # Тут можна додати бонус валюти за левел-ап, наприклад:
                # self.currency += 50
            else:
                break

        self.save()  # Зберігаємо зміни (це автоматично оновить статус)

    @property
    def xp_percentage(self):
        """
        Рахує відсоток заповнення для Progress Bar
        """
        threshold = self.get_next_level_threshold()
        if threshold == 0: return 0
        return (self.xp / threshold) * 100

    # --- ЛОГІКА СТАТУСІВ (Твоя стара) ---

    def save(self, *args, **kwargs):
        LEVEL_MAP = {
            99: "Випускник КШЕ",
            80: "4 курс КШЕ",
            60: "3 курс КШЕ",
            45: "2 курс КШЕ",
            30: "1 курс КШЕ",
            10: "Абітурієнт КШЕ",
            5: "Відрахований з КПІ",
            4: "Абітурієнт КПІ",
            3: "Випускник школи",
            2: "Школяр",
            1: "Дитина",
            0: "Новонароджений",
        }

        for threshold, label in LEVEL_MAP.items():
            if self.level >= threshold:
                self.status = label
                break

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Профіль {self.user.username}"

# Автоматичне створення профілю при реєстрації User
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


# Автоматичне збереження профілю при зміні User
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()