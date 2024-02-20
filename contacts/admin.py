import json
import csv

from django.http import HttpResponse
from django.contrib import admin
from django.shortcuts import render
from django import forms
from import_export.admin import ImportExportModelAdmin
from .models import Contact
from .models import Campaign_Emails, Campaign, Profile, Email, Instructions

class ContactAdmin(ImportExportModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'title', 'company', 'type', 'location', 'level', 'university', 'linkedin')
    search_fields = ['first_name', 'last_name', 'email', 'company', 'type', 'location', 'university']
      
admin.site.register(Contact, ContactAdmin)

class Campaign_EmailsAdmin(admin.ModelAdmin):
    list_display = ('user', 'email','first_name', 'last_name', 'company', 'type', 'location', 'title', 'university', 'campaign_name')

admin.site.register(Campaign_Emails, Campaign_EmailsAdmin)

class CampaignAdmin(admin.ModelAdmin):
    list_display = ('user', 'name')  # Display these fields in the admin list view

    def save_model(self, request, obj, form, change):
        # Ensure the selected user in the admin interface is associated with the campaign
        if 'user' in form.cleaned_data:
            obj.user = form.cleaned_data['user']
        super().save_model(request, obj, form, change)

# Register the Campaign model with the custom CampaignAdmin in the admin site
admin.site.register(Campaign, CampaignAdmin)

class EmailAdmin(admin.ModelAdmin):
    list_display = ('subject', 'user', 'campaign', 'font_family', 'font_size')  # Add 'campaign' to list_display if needed
    search_fields = ['subject', 'user__username', 'campaign__name']  # Add 'campaign__name' to search_fields if needed

admin.site.register(Email, EmailAdmin)

admin.site.register(Profile)

class InstructionsAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'email', 'app_password', 'second_email', 'second_app_password', 'third_email', 'third_app_password')

admin.site.register(Instructions, InstructionsAdmin)