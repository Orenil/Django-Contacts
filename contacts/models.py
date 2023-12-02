from django.db import models

class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    title = models.CharField(max_length=100, default='No Title')
    company = models.CharField(max_length=100, default='No Company')
    
    def __str__(self):
        return self.name

