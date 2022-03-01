from django.db import models

'''
class Country(models.Model):
    country_name=models.CharField(max_length=200,default="None")
    def __str__(self):
        return self.country_name
'''
class All(models.Model):
    username=models.CharField(max_length=2000,default="None")
    firstname=models.CharField(max_length=2000,default="None")
    lastname=models.CharField(max_length=5000,default="None")
    email=models.CharField(max_length=5000,default="None")
    country=models.CharField(max_length=500,default="None")
    history=models.CharField(max_length=50000,default="")
    age=models.IntegerField(default=0)

    #country=models.ForeignKey(Country,on_delete=models.CASCADE,null=True)
    def __str__(self):
        return self.username