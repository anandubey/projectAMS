from django.db import models


class StudentCredential(models.Model):
    reg_no = models.OneToOneField('student.StudentProfile', on_delete=models.CASCADE)
    password = models.CharField(max_length=30, null=False)

    def __str__(self):
        return str(self.reg_no)


class FacultyCredential(models.Model):
    fac_id = models.OneToOneField('faculty.FacultyProfile', on_delete=models.CASCADE)
    password = models.CharField(max_length=30, null=False)

    def __str__(self):
    	return str(self.fac_id)