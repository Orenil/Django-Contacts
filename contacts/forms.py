from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from phonenumber_field.formfields import PhoneNumberField
from .models import Profile

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    phone = PhoneNumberField()

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.save()

        # Check if a profile exists for the user
        profile, created = Profile.objects.get_or_create(user=user)

        # Update the phone number in the existing profile
        profile.phone = self.cleaned_data['phone']
        profile.save()

        return user
        
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['username', 'email']
        
class ProfileUpdateForm(forms.ModelForm):
    phone = PhoneNumberField()
    class Meta:
        model = Profile
        fields = ['phone', 'image']
        
class ContactSearchForm(forms.Form):
    search_term = forms.CharField(required=False, max_length=100)