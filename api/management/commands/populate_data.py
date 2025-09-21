from django.core.management.base import BaseCommand
from api.models import University, College, Program, Course


class Command(BaseCommand):
    help = 'Populate database with sample academic data'

    def handle(self, *args, **options):
        # Create Universities
        university1 = University.objects.create(
            name="University of Technology",
            country="Nigeria"
        )
        
        university2 = University.objects.create(
            name="Federal University of Science and Technology",
            country="Nigeria"
        )
        
        # Create Colleges
        college1 = College.objects.create(
            name="College of Engineering and Technology",
            university=university1
        )
        
        college2 = College.objects.create(
            name="College of Computing and Information Technology",
            university=university1
        )
        
        college3 = College.objects.create(
            name="College of Engineering",
            university=university2
        )
        
        # Create Programs
        program1 = Program.objects.create(
            name="Bachelor of Science in Computer Science",
            college=college1,
            duration=4
        )
        
        program2 = Program.objects.create(
            name="Bachelor of Engineering in Software Engineering",
            college=college2,
            duration=4
        )
        
        program3 = Program.objects.create(
            name="Bachelor of Science in Information Technology",
            college=college2,
            duration=4
        )
        
        program4 = Program.objects.create(
            name="Bachelor of Engineering in Computer Engineering",
            college=college3,
            duration=5
        )
        
        # Create Courses for Computer Science Program
        courses_cs = [
            {"code": "CS101", "name": "Introduction to Programming", "credits": 3, "type": "core", "semester": 1, "year": 1},
            {"code": "CS102", "name": "Data Structures and Algorithms", "credits": 3, "type": "core", "semester": 2, "year": 1},
            {"code": "CS201", "name": "Object-Oriented Programming", "credits": 3, "type": "core", "semester": 1, "year": 2},
            {"code": "CS202", "name": "Database Systems", "credits": 3, "type": "core", "semester": 2, "year": 2},
            {"code": "CS301", "name": "Software Engineering", "credits": 3, "type": "core", "semester": 1, "year": 3},
            {"code": "CS302", "name": "Computer Networks", "credits": 3, "type": "core", "semester": 2, "year": 3},
            {"code": "CS401", "name": "Machine Learning", "credits": 3, "type": "elective", "semester": 1, "year": 4},
            {"code": "CS402", "name": "Final Year Project", "credits": 6, "type": "core", "semester": 2, "year": 4},
        ]
        
        for course_data in courses_cs:
            Course.objects.create(program=program1, **course_data)
        
        # Create Courses for Software Engineering Program
        courses_se = [
            {"code": "SE101", "name": "Programming Fundamentals", "credits": 3, "type": "core", "semester": 1, "year": 1},
            {"code": "SE102", "name": "Web Development", "credits": 3, "type": "core", "semester": 2, "year": 1},
            {"code": "SE201", "name": "Software Design Patterns", "credits": 3, "type": "core", "semester": 1, "year": 2},
            {"code": "SE202", "name": "Mobile App Development", "credits": 3, "type": "core", "semester": 2, "year": 2},
            {"code": "SE301", "name": "DevOps and Cloud Computing", "credits": 3, "type": "core", "semester": 1, "year": 3},
            {"code": "SE302", "name": "Software Testing", "credits": 3, "type": "core", "semester": 2, "year": 3},
            {"code": "SE401", "name": "Enterprise Software Development", "credits": 3, "type": "core", "semester": 1, "year": 4},
            {"code": "SE402", "name": "Capstone Project", "credits": 6, "type": "core", "semester": 2, "year": 4},
        ]
        
        for course_data in courses_se:
            Course.objects.create(program=program2, **course_data)
        
        # Create Courses for Information Technology Program
        courses_it = [
            {"code": "IT101", "name": "Introduction to IT", "credits": 3, "type": "core", "semester": 1, "year": 1},
            {"code": "IT102", "name": "System Administration", "credits": 3, "type": "core", "semester": 2, "year": 1},
            {"code": "IT201", "name": "Network Security", "credits": 3, "type": "core", "semester": 1, "year": 2},
            {"code": "IT202", "name": "Database Management", "credits": 3, "type": "core", "semester": 2, "year": 2},
            {"code": "IT301", "name": "Cybersecurity", "credits": 3, "type": "core", "semester": 1, "year": 3},
            {"code": "IT302", "name": "Cloud Computing", "credits": 3, "type": "core", "semester": 2, "year": 3},
            {"code": "IT401", "name": "IT Project Management", "credits": 3, "type": "core", "semester": 1, "year": 4},
            {"code": "IT402", "name": "IT Internship", "credits": 6, "type": "core", "semester": 2, "year": 4},
        ]
        
        for course_data in courses_it:
            Course.objects.create(program=program3, **course_data)
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated database with sample data')
        )
