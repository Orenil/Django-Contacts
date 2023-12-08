from django.db import models

class Contact(models.Model):
    first_name = models.CharField(max_length=50, default='Null')
    last_name = models.CharField(max_length=50, default='Null')
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    title = models.CharField(max_length=100, default='No Title')
    company = models.CharField(max_length=100, default='No Company')
    type = models.CharField(max_length=100, default='None')
    location = models.CharField(max_length=100)
    level = models.CharField(max_length=100, default='None')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Lead(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    company = models.CharField(max_length=100)
    type = models.CharField(max_length=50)
    location = models.CharField(max_length=100)
    level = models.CharField(max_length=50)

