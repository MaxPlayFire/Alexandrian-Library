# urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "Library"

urlpatterns = [
    path("", views.menu, name="home"),
    
    # Auth
    path("login/", auth_views.LoginView.as_view(template_name="Library/auth/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="Library:home"), name="logout"),
    path("register/", views.register, name="register"),
    
    # Courses
    path("courses/", views.course_list, name="course_list"),
    path("courses/my/", views.my_courses, name="my_courses"),
    path("courses/create/", views.create_course, name="create_course"),
    path("courses/<int:course_id>/", views.course_detail, name="course_detail"),
    path("courses/<int:course_id>/edit/", views.edit_course, name="edit_course"),
    path("courses/<int:course_id>/enroll/", views.enroll_course, name="enroll_course"),
    path("courses/<int:course_id>/unenroll/", views.unenroll_course, name="unenroll_course"),
    
    # Create content
    path("courses/<int:course_id>/module/add/", views.create_module, name="create_module"),
    path("modules/<int:module_id>/lesson/add/", views.create_lesson, name="create_lesson"),
    path("lessons/<int:lesson_id>/group/add/", views.create_exercise_group, name="create_exercise_group"),
    path("groups/<int:group_id>/question/add/", views.add_question, name="add_question"),
    path("groups/<int:group_id>/code/add/", views.add_code, name="add_code"),
    path("groups/<int:group_id>/video/add/", views.add_video, name="add_video"),
    
    # Exercises
    path("exercises/<int:group_id>/", views.exercise_group_view, name="exercise_group_view"),
    path("exercises/<int:exercise_group_id>/complete/", views.mark_exercise_complete, name="mark_exercise_complete"),
    path("questions/<int:question_id>/answer/", views.answer_question, name="answer_question"),
    
    # Grading
    path("courses/<int:course_id>/students/", views.students_list, name="students_list"),
    path("courses/<int:course_id>/students/<int:user_id>/", views.student_work, name="student_progress"),
    path("groups/<int:group_id>/grade/<int:user_id>/", views.grade_student, name="grade_student"),
    path("courses/<int:course_id>/grade/<int:user_id>/", views.grade_course, name="grade_course"),
    
    # Certificates
    path("certificates/<int:certificate_id>/", views.view_certificate, name="view_certificate"),
    path("certificates/<int:cert_id>/toggle/", views.toggle_certificate, name="toggle_certificate"),
    
    # Profile
    path("profile/", views.profile_view, name="profile"),
    path("profile/edit/", views.profile_edit, name="profile_edit"),
    path("profile/<str:username>/", views.profile_view, name="profile_view"),
    
    path("modules/<int:module_id>/toggle/", views.toggle_module, name="toggle_module"),
    path("lessons/<int:lesson_id>/toggle/", views.toggle_lesson, name="toggle_lesson"),
    
    # Портфоліо
    path("profile/portfolio/add/", views.add_portfolio_project, name="add_portfolio_project"),
    path("profile/portfolio/<int:project_id>/delete/", views.delete_portfolio_project, name="delete_portfolio_project"),
]