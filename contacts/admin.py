from django.contrib import admin
from .models import Contact

class ContactAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone', 'title', 'company', 'type', 'location','level')
    search_fields = ('first_name', 'last_name', 'email', 'company', 'title')

admin.site.register(Contact, ContactAdmin)

