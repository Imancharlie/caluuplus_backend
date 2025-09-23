from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, University, College, Program, Course, Student, StudentCourse


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('email', 'password', 'password_confirm', 'display_name')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        # Set username to email for compatibility
        validated_data['username'] = validated_data['email']
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include email and password')
        
        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'display_name')


class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = ('id', 'name', 'country')


class CollegeSerializer(serializers.ModelSerializer):
    university_name = serializers.CharField(source='university.name', read_only=True)
    
    class Meta:
        model = College
        fields = ('id', 'name', 'university', 'university_name')


class ProgramSerializer(serializers.ModelSerializer):
    college_name = serializers.CharField(source='college.name', read_only=True)
    university_name = serializers.CharField(source='college.university.name', read_only=True)
    
    class Meta:
        model = Program
        fields = ('id', 'name', 'college', 'college_name', 'university_name', 'duration')


class CourseSerializer(serializers.ModelSerializer):
    program_name = serializers.CharField(source='program.name', read_only=True)
    
    class Meta:
        model = Course
        fields = ('id', 'code', 'name', 'credits', 'type', 'semester', 'year', 'program', 'program_name')


class StudentCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentCourse
        fields = ('id', 'courses', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

class CourseDataSerializer(serializers.Serializer):
    id = serializers.CharField()
    code = serializers.CharField()
    name = serializers.CharField()
    credits = serializers.IntegerField()
    type = serializers.CharField()
    semester = serializers.IntegerField()
    year = serializers.IntegerField()
    added_at = serializers.DateTimeField(required=False, allow_null=True)

class StudentCourseUpdateSerializer(serializers.Serializer):
    courses = CourseDataSerializer(many=True)


class StudentSerializer(serializers.ModelSerializer):
    university = UniversitySerializer(read_only=True)
    college = CollegeSerializer(read_only=True)
    program = ProgramSerializer(read_only=True)
    courses = serializers.JSONField(source='student_courses.courses', read_only=True)
    has_courses = serializers.BooleanField(read_only=True)
    class Meta:
        model = Student
        fields = ('id', 'university', 'college', 'program', 'year', 'semester', 'courses', 'has_courses')


class StudentCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ('university', 'college', 'program', 'year', 'semester')
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class GPABreakdownSerializer(serializers.Serializer):
    gpa = serializers.FloatField()
    total_credits = serializers.IntegerField()
    total_points = serializers.FloatField()
    graded_courses = serializers.IntegerField()
    breakdown = serializers.ListField()


class TargetGPASerializer(serializers.Serializer):
    target_gpa = serializers.FloatField(min_value=0.0, max_value=5.0)




class CourseAddSerializer(serializers.Serializer):
    course_id = serializers.UUIDField()
