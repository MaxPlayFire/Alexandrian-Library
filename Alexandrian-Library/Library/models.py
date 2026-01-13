from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_teacher = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
    
class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="courses"
    )

    def __str__(self):
        return self.title


class Module(models.Model):
    title = models.CharField(max_length=200)



    def __str__(self):
        return f"{self.hero.name} - {self.ability.title}"


class Lesson(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="lessons"
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.course.title} — {self.title}"


class ExerciseCode(models.Model):
    hero = models.ForeignKey(Hero, on_delete=models.CASCADE, related_name="hero_abilities")
    ability = models.ForeignKey(Ability, on_delete=models.CASCADE, related_name="ability_links")

    class Meta:
        unique_together = ("hero", "ability")

    def __str__(self):
        return f"{self.hero.name} - {self.ability.title}"
class ExerciseTest(models.Model):
    hero = models.ForeignKey(Hero, on_delete=models.CASCADE, related_name="hero_abilities")
    ability = models.ForeignKey(Ability, on_delete=models.CASCADE, related_name="ability_links")

    class Meta:
        unique_together = ("hero", "ability")

    def __str__(self):
        return f"{self.hero.name} - {self.ability.title}"
class ExerciseGroup(models.Model):
    hero = models.ForeignKey(Hero, on_delete=models.CASCADE, related_name="hero_abilities")
    ability = models.ForeignKey(Ability, on_delete=models.CASCADE, related_name="ability_links")

    class Meta:
        unique_together = ("hero", "ability")

    def __str__(self):
        return f"{self.hero.name} - {self.ability.title}"
class ExerciseVideo(models.Model):
    hero = models.ForeignKey(Hero, on_delete=models.CASCADE, related_name="hero_abilities")
    ability = models.ForeignKey(Ability, on_delete=models.CASCADE, related_name="ability_links")

    class Meta:
        unique_together = ("hero", "ability")

    def __str__(self):
        return f"{self.hero.name} - {self.ability.title}"
