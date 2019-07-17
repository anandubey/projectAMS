from django.db import models


class StudentProfile(models.Model):
    reg_no = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=40, null=False)
    email = models.EmailField(max_length=255, null=False, unique=True)
    department = models.CharField(max_length=4, choices=[('CSE', 'CSE'), ('ECE', 'ECE'), ('EEE', 'EEE'), ('EIE', 'EIE'),
                                                         ('ME', 'ME'), ('CE', 'CE'), ('BSMS', 'BSMS')])

    def __str__(self):
    	return str(self.department + ' | ' + self.reg_no + ' | ' + self.name)
