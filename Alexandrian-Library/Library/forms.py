# forms.py
from django import forms
from django.contrib.auth.models import User
from .models import Profile, Course, Module, Lesson, ExerciseGroup, Question, QuestionOption, ExerciseCode, ExerciseVideo, Grade, CourseGrade, PortfolioProject


class ProfileForm(forms.ModelForm):
    username = forms.CharField(max_length=150, label='Нікнейм')
    
    class Meta:
        model = Profile
        fields = ['avatar', 'bio', 'role']
        labels = {'avatar': 'Аватар', 'bio': 'Опис', 'role': 'Роль'}
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['username'].initial = self.user.username
        if not (self.user and self.user.profile.is_admin):
            self.fields['role'].disabled = True
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.user:
            self.user.username = self.cleaned_data['username']
            if commit:
                self.user.save()
        if commit:
            profile.save()
        return profile


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'is_published']
        labels = {'title': 'Назва', 'description': 'Опис', 'is_published': 'Опублікувати'}


class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['title', 'description', 'order']
        labels = {'title': 'Назва', 'description': 'Опис', 'order': 'Порядок'}


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'content', 'order']
        labels = {'title': 'Назва', 'content': 'Матеріал', 'order': 'Порядок'}
        widgets = {'content': forms.Textarea(attrs={'rows': 6})}


class ExerciseGroupForm(forms.ModelForm):
    class Meta:
        model = ExerciseGroup
        fields = ['title', 'description', 'order']
        labels = {'title': 'Назва', 'description': 'Опис', 'order': 'Порядок'}


class QuestionForm(forms.ModelForm):
    option_1 = forms.CharField(max_length=500, label='Варіант 1')
    option_2 = forms.CharField(max_length=500, label='Варіант 2')
    option_3 = forms.CharField(max_length=500, required=False, label='Варіант 3')
    option_4 = forms.CharField(max_length=500, required=False, label='Варіант 4')
    correct_option = forms.ChoiceField(choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4')], label='Правильна')
    
    class Meta:
        model = Question
        fields = ['text', 'explanation', 'order']
        labels = {'text': 'Питання', 'explanation': 'Пояснення', 'order': 'Порядок'}
    
    def save(self, commit=True):
        question = super().save(commit=commit)
        if commit:
            QuestionOption.objects.filter(question=question).delete()
            for i in range(1, 5):
                opt_text = self.cleaned_data.get(f'option_{i}')
                if opt_text:
                    QuestionOption.objects.create(
                        question=question,
                        text=opt_text,
                        is_correct=(str(i) == self.cleaned_data['correct_option']),
                        order=i
                    )
        return question


class ExerciseCodeForm(forms.ModelForm):
    class Meta:
        model = ExerciseCode
        fields = ['title', 'content', 'order']
        labels = {'title': 'Назва', 'content': 'Код/Опис', 'order': 'Порядок'}
        widgets = {'content': forms.Textarea(attrs={'rows': 4})}


class ExerciseVideoForm(forms.ModelForm):
    class Meta:
        model = ExerciseVideo
        fields = ['title', 'url', 'order']
        labels = {'title': 'Назва', 'url': 'Посилання', 'order': 'Порядок'}


class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['score', 'feedback']
        labels = {'score': 'Оцінка (0-100)', 'feedback': 'Коментар'}
        widgets = {'feedback': forms.Textarea(attrs={'rows': 3})}


class CourseGradeForm(forms.ModelForm):
    class Meta:
        model = CourseGrade
        fields = ['grade', 'comment']
        labels = {'grade': 'Оцінка (0-100)', 'comment': 'Коментар'}
        widgets = {'comment': forms.Textarea(attrs={'rows': 4})}

class PortfolioProjectForm(forms.ModelForm):
    class Meta:
        model = PortfolioProject
        fields = ['title', 'url', 'description']
        labels = {
            'title': 'Назва проєкту',
            'url': 'Посилання (GitHub)',
            'description': 'Опис'
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3})
        }