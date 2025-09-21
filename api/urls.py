from django.urls import path
from . import views

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', views.register, name='register'),
    path('auth/login/', views.login, name='login'),
    
    # University & Academic Structure endpoints
    path('universities/', views.UniversityListView.as_view(), name='university-list'),
    path('universities/<uuid:university_id>/colleges/', views.CollegeListView.as_view(), name='college-list'),
    path('colleges/<uuid:college_id>/programs/', views.ProgramListView.as_view(), name='program-list'),
    path('programs/<uuid:program_id>/courses/', views.CourseListView.as_view(), name='course-list'),
    
    # Student Management endpoints
    path('students/profile/', views.student_profile, name='student-profile'),
    
    # Course Management endpoints
    path('students/courses/', views.get_student_courses, name='get-student-courses'),
    path('students/courses/add/', views.add_course, name='add-course'),
    path('students/courses/<uuid:course_id>/', views.remove_course, name='remove-course'),
    path('students/courses/<uuid:course_id>/grade/', views.update_grade, name='update-grade'),
    
    # GPA Calculation endpoints
    path('students/gpa/', views.calculate_gpa, name='calculate-gpa'),
    path('students/gpa/target/', views.generate_target_gpa, name='generate-target-gpa'),
    path('students/gpa/reset/', views.reset_grades, name='reset-grades'),
]
