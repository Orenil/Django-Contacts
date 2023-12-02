import csv
from django.contrib import admin
from django.contrib import messages
from .models import Contact

class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'title', 'company')
    
    def import_contacts(self, request, queryset):
        csv_file = request.FILES.get('csv_file')  # Get the uploaded file
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'File is not a CSV file.')
            return

        try:
            decoded_file = csv_file.read().decode('utf-8')
            csv_data = csv.reader(decoded_file.splitlines())
            for row in csv_data:
                name, email, phone, title, company = row[:5]  # Extract data assuming these columns exist
                Contact.objects.create(name=name, email=email, phone=phone, title=title, company=company)
            
            messages.success(request, 'Contacts imported successfully.')
        except Exception as e:
            messages.error(request, f'Error importing contacts: {str(e)}')

    import_contacts.short_description = "Import Contacts from CSV"

admin.site.register(Contact, ContactAdmin)



