import json
import csv

from django.http import HttpResponse
from django.contrib import admin
from django.shortcuts import render
from django import forms
from import_export.admin import ImportExportModelAdmin
from .models import Contact
from .models import Campaign_Emails, Campaign, Profile

class ContactAdmin(ImportExportModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone', 'title', 'company', 'type', 'location', 'level')
    search_fields = ['first_name', 'last_name', 'email', 'company', 'type', 'location']
    
    
admin.site.register(Contact, ContactAdmin)

class Campaign_EmailsAdmin(admin.ModelAdmin):
    list_display = ('user', 'email','first_name', 'last_name', 'company', 'type', 'location', 'title', 'campaign_name')

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

admin.site.register(Profile)