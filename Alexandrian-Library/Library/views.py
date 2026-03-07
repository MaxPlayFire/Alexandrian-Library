# views.py
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Avg
from .models import *
from .forms import *


def course_list(request):
    courses = Course.objects.filter(is_published=True).select_related('teacher__profile')
    enrolled_ids = []
    if request.user.is_authenticated:
        enrolled_ids = Enrollment.objects.filter(user=request.user, status='enrolled').values_list('course_id', flat=True)
    return render(request, 'Library/courses/course_list.html', {'courses': courses, 'enrolled_course_ids': enrolled_ids})

def menu(request):
    return render(request, 'Library/menu.html')


@login_required
def my_courses(request):
    enrollments = Enrollment.objects.filter(user=request.user, status='enrolled').select_related('course__teacher__profile')
    return render(request, 'Library/courses/my_courses.html', {'enrollments': enrollments})


@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id, is_published=True)
    is_enrolled = Enrollment.objects.filter(user=request.user, course=course, status='enrolled').exists()
    is_teacher = course.teacher == request.user
    modules = course.modules.prefetch_related('lessons__exercise_groups')
    return render(request, 'Library/courses/course_detail.html', {
        'course': course, 'is_enrolled': is_enrolled, 'is_teacher': is_teacher, 'modules': modules
    })


@login_required
def create_course(request):
    if not request.user.profile.is_teacher:
        messages.error(request, 'Тільки викладачі можуть створювати курси')
        return redirect('Library:home')
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user
            course.save()
            messages.success(request, 'Курс створено')
            return redirect('Library:course_detail', course_id=course.id)
    else:
        form = CourseForm()
    return render(request, 'Library/courses/form.html', {'form': form, 'title': 'Створити Курс'})


@login_required
def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id, teacher=request.user)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Курс оновлено')
            return redirect('Library:course_detail', course_id=course.id)
    else:
        form = CourseForm(instance=course)
    return render(request, 'Library/courses/form.html', {'form': form, 'title': 'Редагувати Курс'})


@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id, is_published=True)
    Enrollment.objects.get_or_create(user=request.user, course=course, defaults={'status': 'enrolled'})
    messages.success(request, 'Ви записалися на курс')
    return redirect('Library/courses:course_detail', course_id=course.id)


@login_required
def unenroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    Enrollment.objects.filter(user=request.user, course=course).delete()
    messages.success(request, 'Ви відписалися від курсу')
    return redirect('Library/courses:my_courses')


@login_required
def create_module(request, course_id):
    course = get_object_or_404(Course, id=course_id, teacher=request.user)
    if request.method == 'POST':
        form = ModuleForm(request.POST)
        if form.is_valid():
            module = form.save(commit=False)
            module.course = course
            module.save()
            messages.success(request, 'Модуль створено')
            return redirect('Library/courses:course_detail', course_id=course.id)
    else:
        form = ModuleForm()
    return render(request, 'Library/courses/form.html', {'form': form, 'title': 'Додати Модуль'})


@login_required
def create_lesson(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    if module.course.teacher != request.user:
        messages.error(request, 'Доступ заборонено')
        return redirect('Library:home')
    if request.method == 'POST':
        form = LessonForm(request.POST)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.module = module
            lesson.save()
            messages.success(request, 'Урок створено')
            return redirect('Library/courses:course_detail', course_id=module.course.id)
    else:
        form = LessonForm()
    return render(request, 'Library/courses/form.html', {'form': form, 'title': 'Додати Урок'})


@login_required
def create_exercise_group(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if lesson.module.course.teacher != request.user:
        messages.error(request, 'Доступ заборонено')
        return redirect('Library:home')
    if request.method == 'POST':
        form = ExerciseGroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.lesson = lesson
            group.save()
            messages.success(request, 'Групу вправ створено')
            return redirect('Library/courses:course_detail', course_id=lesson.module.course.id)
    else:
        form = ExerciseGroupForm()
    return render(request, 'Library/courses/form.html', {'form': form, 'title': 'Додати Групу Вправ'})


@login_required
def add_question(request, group_id):
    group = get_object_or_404(ExerciseGroup, id=group_id)
    if group.lesson.module.course.teacher != request.user:
        messages.error(request, 'Доступ заборонено')
        return redirect('Library:home')
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.exercise_group = group
            question.save()
            form.save_m2m() 
            messages.success(request, 'Питання додано')
            return redirect('Library/courses:exercise_group_view', group_id=group.id)
    else:
        form = QuestionForm()
    return render(request, 'Library/form.html', {'form': form, 'title': 'Додати Питання'})


@login_required
def add_code(request, group_id):
    group = get_object_or_404(ExerciseGroup, id=group_id)
    if group.lesson.module.course.teacher != request.user:
        messages.error(request, 'Доступ заборонено')
        return redirect('Library:home')
    if request.method == 'POST':
        form = ExerciseCodeForm(request.POST)
        if form.is_valid():
            code = form.save(commit=False)
            code.exercise_group = group
            code.save()
            messages.success(request, 'Код вправу додано')
            return redirect('Library/courses:exercise_group_view', group_id=group.id)
    else:
        form = ExerciseCodeForm()
    return render(request, 'Library/courses/form.html', {'form': form, 'title': 'Додати Код Вправу'})


@login_required
def add_video(request, group_id):
    group = get_object_or_404(ExerciseGroup, id=group_id)
    if group.lesson.module.course.teacher != request.user:
        messages.error(request, 'Доступ заборонено')
        return redirect('Library/courses:home')
    if request.method == 'POST':
        form = ExerciseVideoForm(request.POST)
        if form.is_valid():
            video = form.save(commit=False)
            video.exercise_group = group
            video.save()
            messages.success(request, 'Відео додано')
            return redirect('Library/courses:exercise_group_view', group_id=group.id)
    else:
        form = ExerciseVideoForm()
    return render(request, 'Library/courses/form.html', {'form': form, 'title': 'Додати Відео'})


@login_required
def exercise_group_view(request, group_id):
    group = get_object_or_404(ExerciseGroup, id=group_id)
    course = group.lesson.module.course
    is_teacher = course.teacher == request.user
    if not is_teacher:
        if not Enrollment.objects.filter(user=request.user, course=course, status='enrolled').exists():
            messages.error(request, 'Ви не записані на цей курс')
            return redirect('Library:home')
    user_answers = {ans.question.id: ans for ans in UserAnswer.objects.filter(user=request.user, question__exercise_group=group)}
    prev_group = ExerciseGroup.objects.filter(lesson=group.lesson, order__lt=group.order).order_by('-order').first()
    next_group = ExerciseGroup.objects.filter(lesson=group.lesson, order__gt=group.order).order_by('order').first()
    return render(request, 'Library/courses/exercise_group_view.html', {
        'group': group, 'course': course, 'is_teacher': is_teacher,
        'user_answers': user_answers, 'prev_group': prev_group, 'next_group': next_group
    })


@login_required
def mark_exercise_complete(request, exercise_group_id):
    group = get_object_or_404(ExerciseGroup, id=exercise_group_id)
    course = group.lesson.module.course
    if Enrollment.objects.filter(user=request.user, course=course, status='enrolled').exists():
        ExerciseGroupCompletion.objects.get_or_create(user=request.user, exercise_group=group)
        messages.success(request, 'Вправу позначено як виконану')
        # Check if course completed
        total_groups = ExerciseGroup.objects.filter(lesson__module__course=course).count()
        completed_groups = ExerciseGroupCompletion.objects.filter(user=request.user, exercise_group__lesson__module__course=course).count()
        if completed_groups == total_groups:
            course_grade, created = CourseGrade.objects.get_or_create(user=request.user, course=course)
            course_grade.grade = course_grade.auto_calculate_grade()
            course_grade.save()
            messages.success(request, 'Курс завершено! Чекайте на оцінку від викладача.')
    return redirect('Library/courses:exercise_group_view', group_id=group.id)


@login_required
def answer_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    option_id = request.POST.get('option_id')
    if not option_id:
        return redirect('Library/courses:exercise_group_view', group_id=question.exercise_group.id)
    
    option = get_object_or_404(QuestionOption, id=option_id, question=question)
    if not Enrollment.objects.filter(user=request.user, course=question.exercise_group.lesson.module.course, status='enrolled').exists():
        return redirect('Library:home')
    
    UserAnswer.objects.update_or_create(user=request.user, question=question, defaults={'selected_option': option})
    messages.success(request, '✓ Правильно!' if option.is_correct else '✗ Неправильно')
    return redirect('Library/courses:exercise_group_view', group_id=question.exercise_group.id)


@login_required
def profile_view(request, username=None):
    user = get_object_or_404(User, username=username) if username else request.user
    profile = user.profile
    created_courses = Course.objects.filter(teacher=user) if profile.is_teacher else []
    enrolled_courses = Enrollment.objects.filter(user=user, status='enrolled').select_related('course')
    certificates = Certificate.objects.filter(user=user).select_related('course')
    return render(request, 'Library/profile/profile_view.html', {
        'profile_user': user, 'profile': profile, 'created_courses': created_courses, 
        'enrolled_courses': enrolled_courses, 'is_own_profile': request.user == user, 'certificates': certificates
    })


@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Оновлено')
            return redirect('Library:profile_view', username=request.user.username)
    else:
        form = ProfileForm(instance=request.user.profile, user=request.user)
    return render(request, 'Library/profile/profile_edit.html', {'form': form, 'profile': request.user.profile})


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Зареєстровано!')
            return redirect('Library:home')
    else:
        form = UserCreationForm()
    return render(request, 'Library/auth/register.html', {'form': form})


@login_required
def students_list(request, course_id):
    course = get_object_or_404(Course, id=course_id, teacher=request.user)
    enrollments = Enrollment.objects.filter(course=course, status='enrolled')
    students = []
    for enr in enrollments:
        user = enr.user
        total_groups = ExerciseGroup.objects.filter(lesson__module__course=course).count()
        completed = ExerciseGroupCompletion.objects.filter(user=user, exercise_group__lesson__module__course=course).count()
        progress = (completed / total_groups * 100) if total_groups else 0
        avg_score = Grade.objects.filter(user=user, exercise_group__lesson__module__course=course).aggregate(Avg('score'))['score__avg'] or 0
        course_grade = CourseGrade.objects.filter(user=user, course=course).first()
        students.append({
            'user': user,
            'progress': int(progress),
            'completed': completed,
            'total': total_groups,
            'avg_score': int(avg_score),
            'course_grade': course_grade
        })
    return render(request, 'Library/students.html', {'course': course, 'students': students})


@login_required
def student_work(request, course_id, user_id):
    course = get_object_or_404(Course, id=course_id, teacher=request.user)
    student = get_object_or_404(User, id=user_id)
    Enrollment.objects.get(user=student, course=course)  # check enrolled
    modules = []
    for module in Module.objects.filter(course=course):
        lessons = []
        for lesson in Lesson.objects.filter(module=module):
            groups = []
            for group in ExerciseGroup.objects.filter(lesson=lesson):
                completion = ExerciseGroupCompletion.objects.filter(user=student, exercise_group=group).first()
                answers = UserAnswer.objects.filter(user=student, question__exercise_group=group).select_related('question', 'selected_option')
                grade = Grade.objects.filter(user=student, exercise_group=group).first()
                groups.append({
                    'group': group,
                    'is_completed': bool(completion),
                    'answers': answers,
                    'grade': grade
                })
            lessons.append({'lesson': lesson, 'groups': groups})
        modules.append({'module': module, 'lessons': lessons})
    return render(request, 'Library/student_progress.html', {'course': course, 'student': student, 'modules': modules})


@login_required
def grade_student(request, group_id, user_id):
    group = get_object_or_404(ExerciseGroup, id=group_id)
    course = group.lesson.module.course
    if course.teacher != request.user:
        messages.error(request, 'Доступ заборонено')
        return redirect('Library:home')
    student = get_object_or_404(User, id=user_id)
    grade, created = Grade.objects.get_or_create(user=student, exercise_group=group, defaults={'graded_by': request.user})
    if request.method == 'POST':
        form = GradeForm(request.POST, instance=grade)
        if form.is_valid():
            form.save()
            messages.success(request, 'Оцінку збережено')
            return redirect('Library:student_progress', course_id=course.id, user_id=student.id)
    else:
        form = GradeForm(instance=grade)
    return render(request, 'Library/form.html', {'form': form, 'title': f'Оцінити: {group.title}'})


@login_required
def grade_course(request, course_id, user_id):
    course = get_object_or_404(Course, id=course_id, teacher=request.user)
    student = get_object_or_404(User, id=user_id)
    course_grade, created = CourseGrade.objects.get_or_create(user=student, course=course)
    if request.method == 'POST':
        form = CourseGradeForm(request.POST, instance=course_grade)
        if form.is_valid():
            form.save()
            avg = Grade.objects.filter(user=student, exercise_group__lesson__module__course=course).aggregate(Avg('score'))['score__avg'] or 0
            course_grade.grade = form.cleaned_data['grade'] or int(avg)
            course_grade.save()
            if not course_grade.certificate_issued:
                cert = Certificate.objects.create(user=student, course=course, total_score=course_grade.grade)
                course_grade.certificate_issued = True
                course_grade.save()
            messages.success(request, 'Оцінку за курс збережено. Сертифікат видано.')
            return redirect('Library:students_list', course_id=course.id)
    else:
        form = CourseGradeForm(instance=course_grade)
    return render(request, 'Library/form.html', {'form': form, 'title': 'Оцінити курс'})


@login_required
def view_certificate(request, certificate_id):
    cert = get_object_or_404(Certificate, id=certificate_id)
    if cert.user != request.user and not request.user.profile.is_teacher:
        messages.error(request, 'Доступ заборонено')
        return redirect('Library:home')
    return render(request, 'Library/certificate.html', {'cert': cert})


@login_required
def toggle_certificate(request, cert_id):
    cert = get_object_or_404(Certificate, id=cert_id, user=request.user)
    if request.method == 'POST':
        cert.is_visible = 'visible' in request.POST
        cert.save()
    return redirect('Library:profile')