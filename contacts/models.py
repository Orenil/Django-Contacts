from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField
from PIL import Image

class Contact(models.Model):
    first_name = models.CharField(max_length=50, default='')
    last_name = models.CharField(max_length=50, default='')
    email = models.EmailField()
    title = models.CharField(max_length=100, default='')
    company = models.CharField(max_length=100, default='')
    type = models.CharField(max_length=100, default='')
    location = models.CharField(max_length=100, default='')
    level = models.CharField(max_length=100, default='')
    university = models.CharField(max_length=200, default='')
    linkedin = models.CharField(max_length=100, default='')
    
    class Meta:
        verbose_name = "Contact"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class SelectedContacts(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    contact_ids = models.TextField()  # Store contact IDs as a comma-separated list or JSON string
    created_at = models.DateTimeField(auto_now_add=True)

#Create Campaign_Emails:
class Campaign_Emails(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    email = models.EmailField()
    first_name = models.CharField(max_length=100, default='')
    last_name = models.CharField(max_length=100, default='')
    company = models.CharField(max_length=100, default='')
    type = models.CharField(max_length=100, default='')
    location = models.CharField(max_length=100, default='None')  
    title = models.CharField(max_length=100, default='')
    university = models.CharField(max_length=200, default='')
    campaign_name = models.CharField(max_length=255, default='')
    
    def __str__(self):
        return self.email
    
#Create Campaign:
class Campaign(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Email(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_emails')
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, null=True, blank=True)
    subject = models.CharField(max_length=255)
    email_content1 = models.TextField()
    email_content2 = models.TextField()
    email_content3 = models.TextField()
    font_family = models.CharField(max_length=50, null=True, blank=True)
    font_size = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return self.subject
    
class Instructions(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.TextField()
    last_name = models.TextField()
    email = models.TextField()
    app_password = models.TextField()
    second_email = models.TextField(default='')  # New field for second email
    second_app_password = models.TextField(default='')  # New field for second app password
    third_email = models.TextField(default='')  # New field for third email
    third_app_password = models.TextField(default='')  # New field for third app password

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    phone = PhoneNumberField(blank=True, null=True)
    
    def __str__(self):
        return f'{self.user.username} Profile'

    # def save(self, *args, **kwargs):
    #   super().save(*args, **kwargs)
        
    #    img = Image.open(self.image.path)
        
    #    if img.height > 300 or img.width > 300:
    #        output_size = (300, 300)
    #        img.thumbnail(output_size)
    #        img.save(self.image.path)
        