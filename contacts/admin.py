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
class ContactAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone', 'title', 'company', 'type', 'location', 'level')
    search_fields = ('first_name', 'last_name', 'email', 'company', 'title')
    
    def import_action(self, request):
        import_object_status = []
        create_new_contacts = []
        if request.method == "POST":
            create_new_contacts = []
            # capture payload from request
            csv_file = json.loads(request.POST.get("contacts"))
            reader = json.loads(request.POST.get("rows"))
            column_headers = json.loads(request.POST.get("csv_headers"))
            util_obj = ImportUtils(column_headers)

            for row in reader:
                first_name = row[util_obj.get_column("FIRST NAME")]
                last_name = util_obj.validate_data(row[util_obj.get_column("LAST NAME")])
                email = util_obj.validate_data(row[util_obj.get_column("EMAIL")])
                phone = row[util_obj.get_column("PHONE")]
                title = row[util_obj.get_column("TITLE")]
                company = row[util_obj.get_column("COMPANY")]
                type = row[util_obj.get_column("TYPE")]
                location = row[util_obj.get_column("LOCATION")]     
                level = row[util_obj.get_column("LEVEL")]
                create_new_contacts.append(
                    Contact(
                        first_name=first_name, last_name=last_name, email=email, phone=phone, title=title,
                        company=company, type=type, location=location, level=level))
                import_object_status.append({"contact": first_name, "status": "FINISHED",
                                            "msg": "Contact created successfully!"})

            Contact.objects.bulk_create(create_new_contacts)

            context = {
                "file": csv_file,
                "entries": len(import_object_status),
                "results": import_object_status
            }
            return HttpResponse(json.dumps(context), content_type="application/json")
        form = CsvImportForm()
        context = {"form": form, "form_title": "Upload users csv file.",
                   "description": "The file should have following headers: "
                   "[FIRSTNAME, LASTNAME, EMAIL, PHONE, TITLE, COMPANY, TYPE, LOCATION, LEVEL]."
                   " The Following rows should contain information for the same.",
                   "endpoint": "/admin/contacts/contact/import/"}
        return render(
            request, "admin/import_contacts_contact.html", context
        )
        
    
    # global variables to improve performance
    export_qs = None
    total_count = 0
    contacts = []

    def export_action(self, request):
        if request.method == 'POST':
            offset = json.loads(request.POST.get('offset'))
            limit = json.loads(request.POST.get('limit'))
            self.contacts = []
            if not self.export_qs:
                self.export_qs = Contact.objects.all().values_list("first_name", "last_name", "email", "company", "title")

            for obj in self.export_qs[offset:limit]:
                self.contacts.append({
                    "first_name": obj[0],
                    "last_name": obj[1],
                    "email": obj[2],
                    "company": obj[3],
                    "title": obj[4]
                })

            context = {
                "results": self.contacts
            }
            return HttpResponse(json.dumps(context), content_type="application/json")

        # define the queryset you want to export and get the count of rows
        self.total_count = Contact.objects.all().count()
        context = {"total_count": self.total_count, "form_title": "Export Characters to csv file",
                   "description": "",
                   "headers": ["First Name", "Last Name", "Email", "Company", "Title"],
                   "endpoint": "/admin/contacts/contact/export/",
                   "fileName": "contacts"}
        return render(
            request, "admin/export_contacts_contact.html", context
        )

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