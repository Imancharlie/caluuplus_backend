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
    path('students/profile/create/', views.student_profile_create, name='student-profile-create'),
    path('students/data/', views.student_data, name='student-data'),
    path('students/profile/options/', views.student_profile_options, name='student-profile-options'),
    
    # Course Management endpoints
    path('students/courses/', views.student_courses, name='student-courses'),
    path('students/courses/batch/', views.save_courses_batch, name='save-courses-batch'),
    path('students/courses/semester/<int:semester>/year/<int:year>/', views.get_student_courses_by_semester, name='get-courses-by-semester'),
    path('students/courses/filter/', views.get_student_courses_filtered, name='get-courses-filtered'),
    path('students/courses/<uuid:course_id>/', views.remove_course, name='remove-course'),
    
    # GPA Calculation endpoints
    path('students/gpa/', views.calculate_gpa, name='calculate-gpa'),
    path('students/gpa/target/', views.generate_target_gpa, name='generate-target-gpa'),
    path('students/gpa/reset/', views.reset_grades, name='reset-grades'),
]
