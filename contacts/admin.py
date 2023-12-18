from django.contrib import admin
from .models import Contact
from .models import Campaign_Emails
class ContactAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone', 'title', 'company', 'type', 'location','level')
    search_fields = ('first_name', 'last_name', 'email', 'company', 'title')

admin.site.register(Contact, ContactAdmin)


class CampaignEmailsAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'campaign_name')

admin.site.register(Campaign_Emails, CampaignEmailsAdmin)