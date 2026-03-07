# admin.py
from django.contrib import admin
from .models import (
    Profile, Course, Enrollment, Module, Lesson,
    ExerciseGroup, ExerciseGroupCompletion,
    ExerciseCode, ExerciseTest, ExerciseVideo,
    Question, QuestionOption, UserAnswer,
    Grade, Certificate, CourseGrade
)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'bio']
    list_filter = ['role']
    search_fields = ['user__username', 'user__email']


class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1
    fields = ['title', 'description', 'order']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'teacher', 'is_published', 'created_at', 'enrolled_students_count']
    list_filter = ['is_published', 'created_at']
    search_fields = ['title', 'description', 'teacher__username']
    inlines = [ModuleInline]


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'status', 'enrolled_at']
    list_filter = ['status', 'enrolled_at']
    search_fields = ['user__username', 'course__title']


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ['title', 'order']


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order']
    list_filter = ['course']
    search_fields = ['title', 'course__title']
    inlines = [LessonInline]


class ExerciseGroupInline(admin.TabularInline):
    model = ExerciseGroup
    extra = 1
    fields = ['title', 'order']


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'module', 'order']
    list_filter = ['module__course']
    search_fields = ['title', 'module__title']
    inlines = [ExerciseGroupInline]


@admin.register(ExerciseGroup)
class ExerciseGroupAdmin(admin.ModelAdmin):
    list_display = ['title', 'lesson', 'order']
    list_filter = ['lesson__module__course']
    search_fields = ['title', 'lesson__title']


@admin.register(ExerciseGroupCompletion)
class ExerciseGroupCompletionAdmin(admin.ModelAdmin):
    list_display = ['user', 'exercise_group', 'completed_at']
    list_filter = ['completed_at']
    search_fields = ['user__username', 'exercise_group__title']


@admin.register(ExerciseCode)
class ExerciseCodeAdmin(admin.ModelAdmin):
    list_display = ['title', 'exercise_group', 'order']
    list_filter = ['exercise_group']
    search_fields = ['title', 'content']


@admin.register(ExerciseTest)
class ExerciseTestAdmin(admin.ModelAdmin):
    list_display = ['title', 'exercise_group', 'order']
    list_filter = ['exercise_group']
    search_fields = ['title', 'content']


@admin.register(ExerciseVideo)
class ExerciseVideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'exercise_group', 'url', 'order']
    list_filter = ['exercise_group']
    search_fields = ['title', 'url']


class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption
    extra = 4
    fields = ['text', 'is_correct', 'order']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'exercise_group', 'order']
    list_filter = ['exercise_group']
    search_fields = ['text']
    inlines = [QuestionOptionInline]


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ['user', 'question', 'selected_option', 'is_correct', 'answered_at']
    list_filter = ['answered_at']
    search_fields = ['user__username', 'question__text']
    
    def is_correct(self, obj):
        return obj.is_correct
    is_correct.boolean = True
    is_correct.short_description = 'Правильна'


@admin.register(CourseGrade)
class CourseGradeAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'grade', 'certificate_issued', 'graded_at']
    list_filter = ['certificate_issued', 'graded_at', 'course']
    search_fields = ['user__username', 'course__title']
    readonly_fields = ['graded_at']


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['user', 'exercise_group', 'score', 'graded_by', 'graded_at']
    list_filter = ['graded_at', 'score']
    search_fields = ['user__username', 'exercise_group__title']


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['certificate_id', 'user', 'course', 'total_score', 'issued_at', 'is_visible']
    list_filter = ['issued_at']
    search_fields = ['user__username', 'course__title', 'certificate_id']
    readonly_fields = ['certificate_id', 'issued_at']