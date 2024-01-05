import json
import csv

from django.http import HttpResponse
from django.contrib import admin
from django.shortcuts import render
from django import forms
from import_export.admin import ImportExportModelAdmin
from .models import Contact
from .models import Campaign_Emails, Campaign, Profile


from .utils import ImportUtils


class CsvImportForm(forms.Form):
    csv_file = forms.FileField()

@admin.register(Contact)  # Using @admin.register decorator instead of admin.site.register
class ContactAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone', 'title', 'company', 'type', 'location', 'level')
    search_fields = ('first_name', 'last_name', 'email', 'company', 'title')
    
    def import_action(self, request):
        if request.method == "POST":
            form = CsvImportForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = request.FILES['csv_file']  # Get the uploaded file

                # Process the uploaded CSV file
                decoded_file = csv_file.read().decode('utf-8')  # Decode CSV file
                csv_data = csv.reader(decoded_file.splitlines())  # Read CSV data

                import_object_status = []
                create_new_contacts = []

                column_headers = next(csv_data)  # Extract headers
                util_obj = ImportUtils(column_headers)  # Initialize ImportUtils (adjust as needed)

                # Process each row in the CSV data
                for row in csv_data:
                    first_name = row[util_obj.get_column("FIRST NAME")]
                    last_name = util_obj.validate_data(row[util_obj.get_column("LAST NAME")])
                    email = util_obj.validate_data(row[util_obj.get_column("EMAIL")])
                    phone = row[util_obj.get_column("PHONE")]
                    title = row[util_obj.get_column("TITLE")]
                    company = row[util_obj.get_column("COMPANY")]
                    type = row[util_obj.get_column("TYPE")]
                    location = row[util_obj.get_column("LOCATION")]
                    level = row[util_obj.get_column("LEVEL")]

                    # Create Contact objects
                    contact = Contact(
                        first_name=first_name, last_name=last_name, email=email, phone=phone, title=title,
                        company=company, type=type, location=location, level=level
                    )
                    create_new_contacts.append(contact)

                    # Append status info for each contact
                    import_object_status.append({
                        "contact": first_name,
                        "status": "FINISHED",
                        "msg": "Contact created successfully!"
                    })

                # Bulk create contacts
                Contact.objects.bulk_create(create_new_contacts)

                # Prepare response context
                context = {
                    "file": csv_file.name,
                    "entries": len(import_object_status),
                    "results": import_object_status
                }

                return HttpResponse(json.dumps(context), content_type="application/json")
        else:
            form = CsvImportForm()

        # Context for rendering form
        context = {
            "form": form,
            "form_title": "Upload users CSV file.",
            "description": "Please upload a CSV file with the specified headers.",
            "endpoint": "/admin/contacts/contact/import/",
        }
        return render(request, "admin/import_contacts_contact.html", context)
        
    
    def export_action(self, request):
        if request.method == 'POST':
            offset = json.loads(request.POST.get('offset'))
            limit = json.loads(request.POST.get('limit'))
            contacts_data = []

            # Fetch contacts queryset based on offset and limit
            contacts_qs = Contact.objects.all().values("first_name", "last_name", "email", "company", "title")[offset:limit]

            # Process queryset and create data for export
            for contact in contacts_qs:
                contacts_data.append({
                    "first_name": contact["first_name"],
                    "last_name": contact["last_name"],
                    "email": contact["email"],
                    "company": contact["company"],
                    "title": contact["title"]
                })

            context = {"results": contacts_data}
            return HttpResponse(json.dumps(context), content_type="application/json")
        
        # Fetch total count of contacts
        total_count = Contact.objects.all().count()
        context = {
            "total_count": total_count,
            "form_title": "Export Contacts to CSV file",
            "description": "",
            "headers": ["First Name", "Last Name", "Email", "Company", "Title"],
            "endpoint": "/admin/contacts/contact/export/",
            "fileName": "contacts_contact"
        }
        return render(request, "admin/export_contacts_contact.html", context)

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