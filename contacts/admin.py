from django.contrib import admin
from .models import Contact

class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'company')  # Display these fields in the admin list view

admin.site.register(Contact, ContactAdmin)
