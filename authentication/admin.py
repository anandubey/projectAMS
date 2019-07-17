from django.contrib import admin
from . import models


admin.site.register(models.StudentCredential)
admin.site.register(models.FacultyCredential)

