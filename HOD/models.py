from django.db import models
from datetime import date
from faculty.models import FacultyProfile

def this_year():
    return str(date.today().year)
    
dep_choices = [('CSE', 'CSE'), ('ECE', 'ECE'), ('EEE', 'EEE'), ('EIE', 'EIE'),('ME', 'ME'), ('CE', 'CE'), ('SH','SH')]

class Hod_credential(models.Model):
    hod_id = models.CharField(max_length=5, primary_key=True)
    password = models.CharField(max_length=64, null=False, unique=True)
    department = models.CharField(max_length=3, unique=True, choices=dep_choices, default='CSE')

    def __str__(self):
        return self.department + ' | ' + self.hod_id 


class Course(models.Model):
    course_code =  models.CharField(max_length=5, primary_key=True)
    title = models.CharField(max_length=100, unique=True, null=False)
    elective = models.BooleanField(default=False)

    def __str__(self):
        return self.course_code + ' | ' + self.title

class Semester_wise_course(models.Model):
    department = models.CharField(max_length=3, null=False, choices=dep_choices, default='CSE')
    semester = models.IntegerField(null=False, choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10)])
    courses = models.CharField(max_length=53, null=False, default='')

    # courses_max_length is 53 = 9*sub_code(len = 5) + 8*separator(-)  --Assumed 6 sub and 3 prac in general, may change
    # courses stores course codes for given semester and department in format <CODE-CODE-...>

    def __str__(self):
        return self.department + ' | ' + str(self.semester) + ' | ' + self.courses


class Semester_wise_electives(models.Model):
    department = models.CharField(max_length=3, null=False, choices=dep_choices, default='CSE')
    semester = models.IntegerField(null=False, choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10)])
    elective_courses = models.CharField(max_length=17, null=False, default='')
    year = models.CharField(default=this_year, max_length=4, null=False)

    def __str__(self):
        return self.department + ' | ' + str(self.semester) + ' | ' + self.year + ' | ' + self.elective_courses


class Course_allot(models.Model):
    year = models.CharField(default=this_year, max_length=4, null=False)
    department = models.CharField(max_length=3, null=False, choices=dep_choices, default='CSE')
    course_code = models.ForeignKey('Course', on_delete=models.CASCADE)
    faculty_id = models.ForeignKey('faculty.FacultyProfile', on_delete=models.CASCADE)
    semester = models.IntegerField(null=False, default=1, choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10)])

    def __str__(self):
        return self.department + ' | ' + self.year + '-' + str(int(self.year)+4) + ' | Sem:' + str(self.semester) + ' | ' + self.course_code.title + ' | ' + self.faculty_id.name