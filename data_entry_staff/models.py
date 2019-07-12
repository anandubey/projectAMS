from django.db import models

# Create your models here.
class DES_Credential(models.Model):
    username = models.CharField(max_length=20, primary_key=True)
    password = models.CharField(max_length=64, null=False)