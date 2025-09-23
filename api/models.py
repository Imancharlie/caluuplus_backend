from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
import uuid


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    display_name = models.CharField(max_length=100)
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['display_name']
    
    def __str__(self):
        return self.display_name
    
    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)
    
    def get_full_name(self):
        return self.display_name
    
    def get_short_name(self):
        return self.display_name


class University(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    country = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name


class College(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='colleges')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.university.name}"


class Program(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='programs')
    duration = models.IntegerField()  # in years
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.college.name}"


class Course(models.Model):
    COURSE_TYPES = [
        ('core', 'Core'),
        ('elective', 'Elective'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=200)
    credits = models.IntegerField()
    type = models.CharField(max_length=10, choices=COURSE_TYPES)
    semester = models.IntegerField()
    year = models.IntegerField()
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='courses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['code', 'program']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Student(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='students')
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='students')
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='students')
    year = models.IntegerField()
    semester = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    has_courses = models.BooleanField(default=False,blank=True)
    def __str__(self):
        return f"{self.user.display_name} - {self.program.name}"



class StudentCourse(models.Model): 
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='student_courses')
    courses = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.student.user.display_name} - {len(self.courses)} courses"

    def save(self, *args, **kwargs):
        """
        Ensure the related student's has_courses flag stays in sync with
        whether there are any courses stored for the student.
        """
        super().save(*args, **kwargs)
        has_any_courses = bool(self.courses)
        if self.student.has_courses != has_any_courses:
            self.student.has_courses = has_any_courses
            # Save only the field that changed to avoid unnecessary writes
            self.student.save(update_fields=['has_courses'])

    def add_course(self, course_data):
        """
        Add a course dict to the JSON list if not already present by id.
        Returns True if added, False if it already existed.
        """
        course_id = str(course_data.get('id')) if course_data.get('id') is not None else None
        existing_ids = {str(c.get('id')) for c in (self.courses or [])}
        if course_id and course_id in existing_ids:
            return False
        courses_list = list(self.courses or [])
        courses_list.append(course_data)
        self.courses = courses_list
        self.save()
        return True

    def remove_course(self, course_id):
        """
        Remove a course from the JSON list by its id. Returns True if removed.
        """
        target_id = str(course_id)
        original_len = len(self.courses or [])
        filtered = [c for c in (self.courses or []) if str(c.get('id')) != target_id]
        if len(filtered) == original_len:
            return False
        self.courses = filtered
        self.save()
        return True
