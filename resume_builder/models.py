from django.db import models
from numpy import True_

# Create your models here.
class personal(models.Model):
    file = models.FileField(upload_to='Resumes')

class Candi_Personal(models.Model):
    Cid = models.AutoField(primary_key=True)
    Cname = models.CharField(max_length=240, null=True)
    Cemail = models.CharField(max_length=240, null=True)
    #Cphone = models.CharField(max_length = 20, null=True)
    #Cdesignation= models.CharField()
class Skills(models.Model):
    skill_of_cand= models.TextField(null=True)

class designation(models.Model):
    designation_of_cand = models.TextField(null=True)

class Cand_personal_skills(models.Model):
    personalid=models.ForeignKey(Candi_Personal,on_delete=models.CASCADE)
    skillid=models.ForeignKey(Skills,on_delete=models.CASCADE)