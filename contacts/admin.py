import csv
from django.contrib import admin
from .models import Contact
from .models import Campaign_Emails, Campaign, Profile
class ContactAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone', 'title', 'company', 'type', 'location','level')
    search_fields = ('first_name', 'last_name', 'email', 'company', 'title')
    
    # Define a custom admin action for importing CSV
    def import_csv(self, request, queryset):
        # This action assumes the CSV file has the same structure as the model fields
        # You may need to modify this logic based on your specific CSV format and model
        for obj in queryset:
            # Assuming 'csv_file' is the field name for the CSV file
            if obj.csv_file:
                csv_file = obj.csv_file.read().decode('utf-8').splitlines()
                csv_reader = csv.DictReader(csv_file)
                for row in csv_reader:
                    # Create objects from CSV data
                    Contact.objects.create(**row)
        self.message_user(request, "CSV file imported successfully.")
    
    import_csv.short_description = "Import CSV"  # Display name for the action in the admin interface
    # Register the custom action in the admin interface
    actions = ['import_csv']


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