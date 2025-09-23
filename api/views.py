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
    GPABreakdownSerializer, TargetGPASerializer, CourseAddSerializer, StudentCourseUpdateSerializer
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
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def student_data(request):
    """
    Get student data directly (without wrapper)
    Returns: university, college, program, year, semester, courses
    """
    try:
        student = Student.objects.get(user=request.user)
        serializer = StudentSerializer(student)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Student.DoesNotExist:
        return Response({'error': 'Student profile not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def student_profile_create(request):
    """
    Create student profile (POST-only)
    - Creates a new profile for the authenticated user if one does not exist
    - Returns 400 if profile already exists
    - Response payload matches StudentSerializer (includes courses array)
    """
    try:
        existing = Student.objects.get(user=request.user)
        return Response({
            'error': 'Student profile already exists',
            'has_profile': True,
            'profile': StudentSerializer(existing).data
        }, status=status.HTTP_400_BAD_REQUEST)
    except Student.DoesNotExist:
        pass

    serializer = StudentCreateUpdateSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        student = serializer.save()
        return Response({
            'message': 'Student profile created successfully',
            'has_profile': True,
            'profile': StudentSerializer(student).data
        }, status=status.HTTP_201_CREATED)

    return Response({
        'error': 'Validation failed',
        'details': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)
@api_view(['GET', 'POST', 'PUT', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def student_profile(request):
    """
    Student Profile Management
    
    GET: Retrieve student profile
    POST: Create new student profile (only if doesn't exist)
    PUT: Update entire student profile (replace all fields)
    PATCH: Partial update student profile (update only provided fields)
    """
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        student = None
    
    if request.method == 'GET':
        if not student:
            return Response({
                'error': 'Student profile not found',
                'message': 'Please create your student profile first',
                'has_profile': False
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = StudentSerializer(student)
        return Response({
            'has_profile': True,
            'profile': serializer.data
        }, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        if student:
            return Response({
                'error': 'Student profile already exists',
                'message': 'Use PUT or PATCH to update your existing profile',
                'has_profile': True,
                'profile': StudentSerializer(student).data
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = StudentCreateUpdateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            student = serializer.save()
            return Response({
                'message': 'Student profile created successfully',
                'has_profile': True,
                'profile': StudentSerializer(student).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'error': 'Validation failed',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'PUT':
        if not student:
            return Response({
                'error': 'Student profile not found',
                'message': 'Please create your student profile first using POST',
                'has_profile': False
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = StudentCreateUpdateSerializer(student, data=request.data, context={'request': request})
        if serializer.is_valid():
            student = serializer.save()
            return Response({
                'message': 'Student profile updated successfully',
                'has_profile': True,
                'profile': StudentSerializer(student).data
            }, status=status.HTTP_200_OK)
        
        return Response({
            'error': 'Validation failed',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'PATCH':
        if not student:
            return Response({
                'error': 'Student profile not found',
                'message': 'Please create your student profile first using POST',
                'has_profile': False
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = StudentCreateUpdateSerializer(student, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            student = serializer.save()
            return Response({
                'message': 'Student profile updated successfully',
                'has_profile': True,
                'profile': StudentSerializer(student).data
            }, status=status.HTTP_200_OK)
        
        return Response({
            'error': 'Validation failed',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def student_profile_options(request):
    """Get available options for creating/updating student profile"""
    try:
        universities = University.objects.all()
        colleges = College.objects.all()
        programs = Program.objects.all()
        
        return Response({
            'universities': UniversitySerializer(universities, many=True).data,
            'colleges': CollegeSerializer(colleges, many=True).data,
            'programs': ProgramSerializer(programs, many=True).data,
            'year_choices': [1, 2, 3, 4, 5],  # Common academic years
            'semester_choices': [1, 2]  # Common semesters
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Failed to fetch profile options',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Course Management Views

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_student_courses_by_semester(request, semester, year):
    """Get courses for a specific semester and year for the authenticated student"""
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        return Response({'error': 'Student profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        student_course = StudentCourse.objects.get(student=student)
        courses = student_course.courses or []
        
        # Filter courses by semester and year
        filtered_courses = [
            course for course in courses 
            if course.get('semester') == semester and course.get('year') == year
        ]
        
        return Response({
            'semester': semester,
            'year': year,
            'courses': filtered_courses,
            'total_courses': len(filtered_courses)
        }, status=status.HTTP_200_OK)
        
    except StudentCourse.DoesNotExist:
        return Response({
            'semester': semester,
            'year': year,
            'courses': [],
            'total_courses': 0,
            'message': 'No courses found for this student'
        }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_student_courses_filtered(request):
    """Get courses for the authenticated student with optional semester/year filtering"""
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        return Response({'error': 'Student profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        student_course = StudentCourse.objects.get(student=student)
        courses = student_course.courses or []
        
        # Get filter parameters from query string
        semester = request.query_params.get('semester')
        year = request.query_params.get('year')
        course_type = request.query_params.get('type')  # 'core' or 'elective'
        
        # Apply filters
        filtered_courses = courses
        
        if semester is not None:
            semester = int(semester)
            filtered_courses = [
                course for course in filtered_courses 
                if course.get('semester') == semester
            ]
        
        if year is not None:
            year = int(year)
            filtered_courses = [
                course for course in filtered_courses 
                if course.get('year') == year
            ]
        
        if course_type:
            filtered_courses = [
                course for course in filtered_courses 
                if course.get('type') == course_type
            ]
        
        return Response({
            'filters': {
                'semester': semester,
                'year': year,
                'type': course_type
            },
            'courses': filtered_courses,
            'total_courses': len(filtered_courses)
        }, status=status.HTTP_200_OK)
        
    except StudentCourse.DoesNotExist:
        return Response({
            'filters': {
                'semester': semester,
                'year': year,
                'type': course_type
            },
            'courses': [],
            'total_courses': 0,
            'message': 'No courses found for this student'
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def save_courses_batch(request):
    """Save multiple courses for the authenticated student in the JSON field"""
    try:
        courses_data = request.data.get('courses', [])
        
        if not courses_data:
            return Response(
                {'error': 'No courses provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or create student profile
        try:
            student = Student.objects.get(user=request.user)
        except Student.DoesNotExist:
            return Response(
                {'error': 'Student profile not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get or create StudentCourse record
        student_course, created = StudentCourse.objects.get_or_create(student=student)
        
        # Format courses data for storage in JSON field
        formatted_courses = []
        for course_data in courses_data:
            formatted_course = {
                'id': course_data.get('course_id'),
                'code': course_data.get('course_code'),
                'name': course_data.get('course_name'),
                'credits': course_data.get('credit_hour'),
                'type': 'elective' if course_data.get('is_elective') else 'core',
                'semester': course_data.get('semester'),
                'year': course_data.get('year'),
                'added_at': None  # Will be set when saved
            }
            formatted_courses.append(formatted_course)
        
        # Store all courses in the JSON field
        student_course.courses = formatted_courses
        student_course.save()
        
        return Response({
            'message': f'Successfully saved {len(formatted_courses)} courses',
            'courses': formatted_courses
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def remove_course(request, course_id):
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        return Response({'error': 'Student profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        student_course = StudentCourse.objects.get(student=student)
        if student_course.remove_course(course_id):
            return Response({'message': 'Course removed successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
    except StudentCourse.DoesNotExist:
        return Response({'error': 'No courses found'}, status=status.HTTP_404_NOT_FOUND)




@api_view(['GET', 'POST', 'PUT'])
@permission_classes([permissions.IsAuthenticated])
def student_courses(request):
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        return Response({'error': 'Student profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Get or create StudentCourse record
    student_course, created = StudentCourse.objects.get_or_create(student=student)
    
    if request.method == 'GET':
        serializer = StudentCourseSerializer(student_course)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # Add single course
        serializer = CourseAddSerializer(data=request.data)
        if serializer.is_valid():
            course_id = serializer.validated_data['course_id']
            course = get_object_or_404(Course, id=course_id)
            
            # Prepare course data
            course_data = {
                'id': str(course.id),
                'code': course.code,
                'name': course.name,
                'credits': course.credits,
                'type': course.type,
                'semester': course.semester,
                'year': course.year,
                'added_at': None
            }
            
            # Add course to JSON field
            if student_course.add_course(course_data):
                return Response({
                    'message': 'Course added successfully',
                    'course': course_data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'Course already added'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'PUT':
        # Update all courses (bulk update)
        serializer = StudentCourseUpdateSerializer(data=request.data)
        if serializer.is_valid():
            courses_data = serializer.validated_data['courses']
            
            # Convert to the format expected by the model
            formatted_courses = []
            for course in courses_data:
                formatted_course = {
                    'id': course['id'],
                    'code': course['code'],
                    'name': course['name'],
                    'credits': course['credits'],
                    'type': course['type'],
                    'semester': course['semester'],
                    'year': course['year'],
                    'added_at': course.get('added_at')
                }
                formatted_courses.append(formatted_course)
            
            # Update the JSON field
            student_course.courses = formatted_courses
            student_course.save()
            
            return Response({
                'message': 'Courses updated successfully',
                'courses': formatted_courses
            }, status=status.HTTP_200_OK)
        
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