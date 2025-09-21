from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import User, University, College, Program, Course, Student, StudentCourse
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserSerializer,
    UniversitySerializer, CollegeSerializer, ProgramSerializer, CourseSerializer,
    StudentSerializer, StudentCreateUpdateSerializer, StudentCourseSerializer,
    GPABreakdownSerializer, TargetGPASerializer, GradeUpdateSerializer, CourseAddSerializer
)


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


# Authentication Views
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token = get_tokens_for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token['access']
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login(request):
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        token = get_tokens_for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token['access']
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# University & Academic Structure Views
class UniversityListView(generics.ListAPIView):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    permission_classes = [permissions.AllowAny]


class CollegeListView(generics.ListAPIView):
    serializer_class = CollegeSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        university_id = self.kwargs['university_id']
        return College.objects.filter(university_id=university_id)


class ProgramListView(generics.ListAPIView):
    serializer_class = ProgramSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        college_id = self.kwargs['college_id']
        return Program.objects.filter(college_id=college_id)


class CourseListView(generics.ListAPIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        program_id = self.kwargs['program_id']
        year = self.request.query_params.get('year')
        semester = self.request.query_params.get('semester')
        
        queryset = Course.objects.filter(program_id=program_id)
        
        if year:
            queryset = queryset.filter(year=int(year))
        if semester:
            queryset = queryset.filter(semester=int(semester))
        
        return queryset


# Student Management Views
@api_view(['GET', 'POST', 'PUT'])
@permission_classes([permissions.IsAuthenticated])
def student_profile(request):
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        student = None
    
    if request.method == 'GET':
        if not student:
            return Response({'error': 'Student profile not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = StudentSerializer(student)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        if student:
            return Response({'error': 'Student profile already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = StudentCreateUpdateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            student = serializer.save()
            return Response(StudentSerializer(student).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'PUT':
        if not student:
            return Response({'error': 'Student profile not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = StudentCreateUpdateSerializer(student, data=request.data, context={'request': request})
        if serializer.is_valid():
            student = serializer.save()
            return Response(StudentSerializer(student).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Course Management Views


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def remove_course(request, course_id):
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        return Response({'error': 'Student profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        student_course = StudentCourse.objects.get(student=student, course_id=course_id)
        student_course.delete()
        return Response({'message': 'Course removed successfully'}, status=status.HTTP_200_OK)
    except StudentCourse.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def update_grade(request, course_id):
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        return Response({'error': 'Student profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        student_course = StudentCourse.objects.get(student=student, course_id=course_id)
    except StudentCourse.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = GradeUpdateSerializer(data=request.data)
    if serializer.is_valid():
        student_course.grade = serializer.validated_data['grade']
        student_course.save()
        return Response({
            'message': 'Grade updated successfully',
            'course': StudentCourseSerializer(student_course).data
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def student_courses(request):
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        return Response({'error': 'Student profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        student_courses = StudentCourse.objects.filter(student=student)
        serializer = StudentCourseSerializer(student_courses, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = CourseAddSerializer(data=request.data)
        if serializer.is_valid():
            course_id = serializer.validated_data['course_id']
            course = get_object_or_404(Course, id=course_id)
            
            # Check if course is already added
            if StudentCourse.objects.filter(student=student, course=course).exists():
                return Response({'error': 'Course already added'}, status=status.HTTP_400_BAD_REQUEST)
            
            student_course = StudentCourse.objects.create(student=student, course=course)
            return Response({
                'message': 'Course added successfully',
                'course': StudentCourseSerializer(student_course).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# GPA Calculation Views
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def calculate_gpa(request):
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        return Response({'error': 'Student profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    gpa_data = student.get_gpa_breakdown()
    return Response(gpa_data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_target_gpa(request):
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        return Response({'error': 'Student profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = TargetGPASerializer(data=request.data)
    if serializer.is_valid():
        target_gpa = serializer.validated_data['target_gpa']
        
        # Get current GPA
        current_gpa = student.get_gpa()
        
        # Simple target GPA calculation - set all ungraded courses to required grade
        student_courses = StudentCourse.objects.filter(student=student)
        grades = []
        
        for student_course in student_courses:
            if not student_course.grade:
                # Calculate required grade for target GPA
                # This is a simplified calculation
                required_grade = 'A' if target_gpa >= 4.5 else 'B+' if target_gpa >= 4.0 else 'B'
                required_points = StudentCourse.GRADE_POINTS[required_grade]
                
                grades.append({
                    'course_id': str(student_course.course.id),
                    'course_code': student_course.course.code,
                    'course_name': student_course.course.name,
                    'credits': student_course.course.credits,
                    'required_grade': required_grade,
                    'required_points': required_points
                })
        
        # Calculate accuracy
        accuracy = "excellent" if abs(current_gpa - target_gpa) < 0.1 else "good" if abs(current_gpa - target_gpa) < 0.3 else "needs_improvement"
        
        return Response({
            'message': 'Target grades generated successfully',
            'target_gpa': target_gpa,
            'actual_gpa': current_gpa,
            'accuracy': accuracy,
            'grades': grades
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def reset_grades(request):
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        return Response({'error': 'Student profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Reset all grades to A
    student_courses = StudentCourse.objects.filter(student=student)
    updated_count = 0
    
    for student_course in student_courses:
        student_course.grade = 'A'
        student_course.save()
        updated_count += 1
    
    return Response({
        'message': 'All grades reset to A',
        'courses_updated': updated_count
    }, status=status.HTTP_200_OK)