from django.db import models
from datetime import date

class FacultyProfile(models.Model):
    faculty_id = models.CharField(max_length=6, primary_key=True)
    name = models.CharField(max_length=40, null=False)
    email = models.EmailField(max_length=255, null=False, unique=True)
    department = models.CharField(max_length=4, choices=[('CSE', 'CSE'), ('ECE', 'ECE'), ('EEE', 'EEE'), ('EIE', 'EIE'),
                                                         ('ME', 'ME'), ('CE', 'CE'), ('SH','SH')])

    def __str__(self):
    	return self.department + ' | ' + self.faculty_id + ' | ' + self.name


class attendance(models.Model):
    reg_no = models.ForeignKey('student.studentProfile', on_delete=models.CASCADE)
    date = models.DateField( default=date.today)
    course_code = models.CharField(max_length=5)
    attendance = models.CharField(max_length=1)
    topic = models.CharField(max_length=80, null=False, default='')
    no_of_classes = models.IntegerField(null=False, default=1, choices=[(1,1),(2,2),(3,3),(4,4),(5,5),(6,6),(7,7),(8,8)])
    if_mod = models.BooleanField(default=False)

    def __str__(self):
        return self.course_code + " | " + self.topic + " | " + str(self.no_of_classes) + " | " + str(self.date) + ' | ' + self.reg_no.reg_no + " | " + self.attendance

