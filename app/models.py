from statistics import mode
from django.db import models
from django.contrib.auth.models import User

class All(models.Model):
    username=models.CharField(max_length=2000,default="None")
    firstname=models.CharField(max_length=2000,default="None")
    lastname=models.CharField(max_length=5000,default="None")
    email=models.CharField(max_length=5000,default="None")
    country=models.CharField(max_length=500,default="India")
    history=models.CharField(max_length=50000,default="")
    age=models.IntegerField(default=18)

    #country=models.ForeignKey(Country,on_delete=models.CASCADE,null=True)
    def __str__(self):
        return self.username 

class Like(models.Model):
    username=models.CharField(max_length=2000,default="None")
    ISBN=models.CharField(max_length=2000,default="None")
    like=models.CharField(max_length=2000,default="unlike")

