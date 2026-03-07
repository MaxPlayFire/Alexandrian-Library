# models.py
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Count
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid


class Profile(models.Model):
    ROLE_CHOICES = [
        ('student', 'Учень'),
        ('teacher', 'Вчитель'),
        ('admin', 'Адміністратор'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    bio = models.TextField(blank=True, null=True, verbose_name='Опис')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Аватар')
    
    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"
    
    @property
    def is_teacher(self):
        return self.role in ['teacher', 'admin']
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def avatar_letter(self):
        return self.user.username[0].upper() if self.user.username else '?'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()


class Course(models.Model):
    title = models.CharField(max_length=200, verbose_name='Назва курсу')
    description = models.TextField(verbose_name='Опис')
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_courses",
        verbose_name='Викладач'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата створення')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата оновлення')
    is_published = models.BooleanField(default=True, verbose_name='Опубліковано')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Курс'
        verbose_name_plural = 'Курси'
    
    def __str__(self):
        return self.title
    
    @property
    def enrolled_students_count(self):
        return self.enrollments.filter(status='enrolled').count()


class Enrollment(models.Model):
    STATUS_CHOICES = [
        ('enrolled', 'Записаний'),
        ('completed', 'Завершений'),
        ('dropped', 'Відписаний'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments', verbose_name='Студент')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments', verbose_name='Курс')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='enrolled', verbose_name='Статус')
    enrolled_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата запису')
    
    class Meta:
        unique_together = ['user', 'course']
        verbose_name = 'Запис на курс'
        verbose_name_plural = 'Записи на курси'
    
    def __str__(self):
        return f"{self.user.username} - {self.course.title}"


class Module(models.Model):
    title = models.CharField(max_length=200, verbose_name='Назва модуля')
    description = models.TextField(blank=True, verbose_name='Опис')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules', verbose_name='Курс')
    order = models.PositiveIntegerField(default=1, verbose_name='Порядок')
    
    class Meta:
        ordering = ['order']
        verbose_name = 'Модуль'
        verbose_name_plural = 'Модулі'
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"
    
    def get_completion_for_user(self, user):
        total_groups = self.lessons.aggregate(total=Count('exercise_groups'))['total']
        if total_groups == 0:
            return 0
        completed = ExerciseGroupCompletion.objects.filter(user=user, exercise_group__lesson__module=self).count()
        return int((completed / total_groups) * 100)


class Lesson(models.Model):
    title = models.CharField(max_length=200, verbose_name='Назва уроку')
    content = models.TextField(blank=True, verbose_name='Матеріал уроку')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons', verbose_name='Модуль')
    order = models.PositiveIntegerField(default=1, verbose_name='Порядок')
    
    class Meta:
        ordering = ['order']
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'
    
    def __str__(self):
        return f"{self.module.title} - {self.title}"
    
    def get_completion_for_user(self, user):
        total_groups = self.exercise_groups.count()
        if total_groups == 0:
            return 0
        completed = ExerciseGroupCompletion.objects.filter(user=user, exercise_group__lesson=self).count()
        return int((completed / total_groups) * 100)


class ExerciseGroup(models.Model):
    title = models.CharField(max_length=200, verbose_name='Назва групи вправ')
    description = models.TextField(blank=True, verbose_name='Опис')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='exercise_groups', verbose_name='Урок')
    order = models.PositiveIntegerField(default=1, verbose_name='Порядок')
    
    class Meta:
        ordering = ['order']
        verbose_name = 'Група вправ'
        verbose_name_plural = 'Групи вправ'
    
    def __str__(self):
        return f"{self.lesson.title} - {self.title}"
    
    def is_completed_by_user(self, user):
        return ExerciseGroupCompletion.objects.filter(user=user, exercise_group=self).exists()


class ExerciseGroupCompletion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='completions', verbose_name='Студент')
    exercise_group = models.ForeignKey(ExerciseGroup, on_delete=models.CASCADE, related_name='completions', verbose_name='Група вправ')
    completed_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата завершення')
    
    class Meta:
        unique_together = ['user', 'exercise_group']
        verbose_name = 'Завершення вправи'
        verbose_name_plural = 'Завершення вправ'
    
    def __str__(self):
        return f"{self.user.username} - {self.exercise_group.title}"


class ExerciseCode(models.Model):
    title = models.CharField(max_length=200, verbose_name='Назва кодової вправи')
    content = models.TextField(verbose_name='Код/Опис завдання')
    exercise_group = models.ForeignKey(ExerciseGroup, on_delete=models.CASCADE, related_name='code_exercises', verbose_name='Група вправ')
    order = models.PositiveIntegerField(default=1, verbose_name='Порядок')
    
    class Meta:
        ordering = ['order']
        verbose_name = 'Кодова вправа'
        verbose_name_plural = 'Кодові вправи'
    
    def __str__(self):
        return self.title


class ExerciseTest(models.Model):
    title = models.CharField(max_length=200, verbose_name='Назва тесту')
    content = models.TextField(verbose_name='Тестовий код')
    exercise_group = models.ForeignKey(ExerciseGroup, on_delete=models.CASCADE, related_name='test_exercises', verbose_name='Група вправ')
    order = models.PositiveIntegerField(default=1, verbose_name='Порядок')
    
    class Meta:
        ordering = ['order']
        verbose_name = 'Тестова вправа'
        verbose_name_plural = 'Тестові вправи'
    
    def __str__(self):
        return self.title


class ExerciseVideo(models.Model):
    title = models.CharField(max_length=200, verbose_name='Назва відео')
    url = models.URLField(verbose_name='Посилання на відео')
    exercise_group = models.ForeignKey(ExerciseGroup, on_delete=models.CASCADE, related_name='video_exercises', verbose_name='Група вправ')
    order = models.PositiveIntegerField(default=1, verbose_name='Порядок')
    
    class Meta:
        ordering = ['order']
        verbose_name = 'Відео вправа'
        verbose_name_plural = 'Відео вправи'
    
    def __str__(self):
        return self.title


class Question(models.Model):
    text = models.TextField(verbose_name='Текст питання')
    explanation = models.TextField(blank=True, verbose_name='Пояснення')
    exercise_group = models.ForeignKey(ExerciseGroup, on_delete=models.CASCADE, related_name='questions', verbose_name='Група вправ')
    order = models.PositiveIntegerField(default=1, verbose_name='Порядок')
    
    class Meta:
        ordering = ['order']
        verbose_name = 'Питання'
        verbose_name_plural = 'Питання'
    
    def __str__(self):
        return self.text[:50]


class QuestionOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options', verbose_name='Питання')
    text = models.CharField(max_length=500, verbose_name='Текст варіанту')
    is_correct = models.BooleanField(default=False, verbose_name='Правильний')
    order = models.PositiveIntegerField(default=1, verbose_name='Порядок')
    
    class Meta:
        ordering = ['order']
        verbose_name = 'Варіант відповіді'
        verbose_name_plural = 'Варіанти відповідей'
    
    def __str__(self):
        return self.text[:50]


class UserAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers', verbose_name='Студент')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='user_answers', verbose_name='Питання')
    selected_option = models.ForeignKey(QuestionOption, on_delete=models.CASCADE, verbose_name='Вибраний варіант')
    answered_at = models.DateTimeField(auto_now=True, verbose_name='Дата відповіді')
    
    class Meta:
        unique_together = ['user', 'question']
        verbose_name = 'Відповідь користувача'
        verbose_name_plural = 'Відповіді користувачів'
    
    def __str__(self):
        return f"{self.user.username} - {self.question.text[:20]}"
    
    @property
    def is_correct(self):
        return self.selected_option.is_correct


class Certificate(models.Model):
    certificate_id = models.CharField(max_length=20, unique=True, editable=False, verbose_name='ID Сертифіката')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificates', verbose_name='Студент')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_certificates', verbose_name='Курс')
    issued_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата видачі')
    total_score = models.FloatField(default=0, verbose_name='Загальний бал')
    is_visible = models.BooleanField(default=True, verbose_name='Відображати в портфоліо')
    
    class Meta:
        unique_together = ['user', 'course']
        verbose_name = 'Сертифікат'
        verbose_name_plural = 'Сертифікати'
    
    def __str__(self):
        return f"{self.user.username} - {self.course.title} - {self.total_score:.1f}"
    
    def save(self, *args, **kwargs):
        if not self.certificate_id:
            self.certificate_id = f"CERT-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class CourseGrade(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='grades', verbose_name='Студент')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='grades', verbose_name='Курс')
    grade = models.IntegerField(default=0, verbose_name='Оцінка (0-100)')
    comment = models.TextField(blank=True, verbose_name='Коментар викладача')
    graded_at = models.DateTimeField(auto_now=True, verbose_name='Дата оцінювання')
    certificate_issued = models.BooleanField(default=False, verbose_name='Сертифікат виданий')
    
    class Meta:
        unique_together = ['user', 'course']
        verbose_name = 'Оцінка за курс'
        verbose_name_plural = 'Оцінки за курси'
    
    def __str__(self):
        return f"{self.user.username} - {self.course.title}: {self.grade}%"
    
    def auto_calculate_grade(self):
        total_groups = ExerciseGroup.objects.filter(lesson__module__course=self.course).count()
        if total_groups == 0:
            return 0
        completed_groups = ExerciseGroupCompletion.objects.filter(
            user=self.user,
            exercise_group__lesson__module__course=self.course
        ).count()
        return int((completed_groups / total_groups) * 100)


class Grade(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exercise_grades', verbose_name='Студент')
    exercise_group = models.ForeignKey(ExerciseGroup, on_delete=models.CASCADE, related_name='grades', verbose_name='Група вправ')
    score = models.IntegerField(default=0, verbose_name='Оцінка (0-100)')
    feedback = models.TextField(blank=True, verbose_name='Зворотний зв\'язок')
    graded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='given_grades', verbose_name='Оцінив')
    graded_at = models.DateTimeField(auto_now=True, verbose_name='Дата оцінювання')
    
    class Meta:
        unique_together = ['user', 'exercise_group']
        verbose_name = 'Оцінка за вправу'
        verbose_name_plural = 'Оцінки за вправи'
    
    def __str__(self):
        return f"{self.user.username} - {self.exercise_group.title}: {self.score}"