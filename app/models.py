from django.db import models

# Create your models here.
class Books(models.Model):
    ISBN=models.CharField(max_length=2000)
    BookTitle=models.CharField(max_length=2000)
    BookAuthor=models.CharField(max_length=5000)
    YearOfPublication=models.CharField(max_length=5000)
    Publisher=models.CharField(max_length=5000)
    ImageURLS=models.CharField(max_length=5000)
    ImageURLM=models.CharField(max_length=5000)
    ImageURLL=models.CharField(max_length=5000)

    def __str__(self):
        return self.BookTitle
