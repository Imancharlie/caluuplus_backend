from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, University, College, Program, Course, Student, StudentCourse


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'display_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    search_fields = ('email', 'display_name')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('display_name', 'first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'display_name', 'password1', 'password2'),
        }),
    )


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'created_at')
    list_filter = ('country', 'created_at')
    search_fields = ('name', 'country')


@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
    list_display = ('name', 'university', 'created_at')
    list_filter = ('university', 'created_at')
    search_fields = ('name', 'university__name')


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'college', 'duration', 'created_at')
    list_filter = ('college', 'duration', 'created_at')
    search_fields = ('name', 'college__name')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'credits', 'type', 'semester', 'year', 'program')
    list_filter = ('type', 'semester', 'year', 'program')
    search_fields = ('code', 'name', 'program__name')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'university', 'college', 'program', 'year', 'semester')
    list_filter = ('university', 'college', 'program', 'year', 'semester')
    search_fields = ('user__display_name', 'user__email', 'program__name')


@admin.register(StudentCourse)
class StudentCourseAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'grade', 'points', 'created_at')
    list_filter = ('grade', 'created_at')
    search_fields = ('student__user__display_name', 'course__code', 'course__name')