from django.contrib import admin
from .models import Contact

class ContactAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'email', 'phone', 'title', 'company', 'type', 'location','level')
    search_fields = ('first_name', 'last_name', 'email', 'company', 'title')

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    get_full_name.admin_order_field = 'last_name'  # Allows column sorting
    get_full_name.short_description = 'Full Name'

admin.site.register(Contact, ContactAdmin)
