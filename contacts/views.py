from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseServerError
from .models import Contact
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login
from django.db.models import Count
from .forms import UserRegisterForm
from django.http import HttpResponse
from .helpers import getEmailFromContactId, getFirstNameFromContactId, getLastNameFromContactId, getCompanyNameFromContactId, getTypeFromContactId, getTitleFromContactId
import csv
import json
import requests
import logging

def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            # Redirect to a specific URL after successful login
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Your Account has been created! Please login')            
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})

@login_required
def profile(request):
    return render(request, 'profile.html')

def home(request):
    home = Contact.objects.all()
    return render(request, 'home.html')

@login_required
def contact_list(request):
    distinct_types = Contact.objects.values_list('type', flat=True).distinct()
    distinct_companies = Contact.objects.values_list('company', flat=True).distinct()
    distinct_locations = Contact.objects.values_list('location', flat=True).distinct()
    distinct_levels = Contact.objects.values_list('level', flat=True).distinct()

    contacts = Contact.objects.all()
    return render(request, 'contact_list.html', {
        'contacts': contacts,
        'distinct_types': distinct_types,
        'distinct_companies': distinct_companies,
        'distinct_locations': distinct_locations,
        'distinct_levels': distinct_levels,
    })

def upload_csv(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']

        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Please upload a CSV file.')
        else:
            try:
                decoded_file = csv_file.read().decode('utf-8')
                csv_data = csv.reader(decoded_file.splitlines(), delimiter=',')
                headers = next(csv_data)  # Read header row
                row_count = 1  # Counter for rows (excluding header)

                for row in csv_data:
                    row_count += 1
                    if len(row) == len(headers):  # Validate row against headers
                        name, email, phone, title, company = row
                        existing_contact = Contact.objects.filter(email=email).first()
                        if existing_contact:
                            messages.warning(request, f"Skipped row at index {row_count}: {row}. Contact with email '{email}' already exists.")
                        else:
                            Contact.objects.create(name=name, email=email, phone=phone, title=title, company=company)
                    else:
                        messages.warning(request, f"Skipped row at index {row_count}: {row}. Unexpected number of values.")

                messages.success(request, 'Contacts uploaded successfully.')
            except Exception as e:
                messages.error(request, f"Error uploading contacts: {e}")
    return render(request, 'upload_csv.html')


@csrf_exempt
def filter_contacts(request):
    if request.method == 'POST':
        type_filter = request.POST.get('type')
        company_filter = request.POST.get('company')
        location_filter = request.POST.get('location')
        level_filter = request.POST.get('level')

        # Filter contacts based on received parameters
        filtered_contacts = Contact.objects.all()

        if type_filter:
            filtered_contacts = filtered_contacts.filter(type=type_filter)
        if company_filter:
            filtered_contacts = filtered_contacts.filter(company=company_filter)
        if location_filter:
            filtered_contacts = filtered_contacts.filter(location=location_filter)
        if level_filter:
            filtered_contacts = filtered_contacts.filter(level=level_filter)

        # Prepare filtered contacts data to send back as JSON
        contacts_data = list(filtered_contacts.values())  # Convert QuerySet to list of dictionaries

        return JsonResponse({'contacts': contacts_data}, status=200)

    return JsonResponse({'error': 'Invalid request method'}, status=400)

def get_selected_contacts(request):
    contact_ids = request.GET.getlist('contactIds[]')  # Fetch the contact IDs from the request
    contacts = Contact.objects.filter(id__in=contact_ids).values('first_name', 'last_name', 'email', 'phone', 'company', 'type', 'location', 'level')

    return JsonResponse({'contacts': list(contacts)})

# Function to get the campaign ID based on the campaign name
def get_campaign_id(api_key, campaign_name):
    url = f"https://api.instantly.ai/api/v1/campaign/list?api_key={api_key}&skip=0&limit=100"
    headers = {'Content-Type': 'application/json'}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        campaigns = response.json()
        for campaign in campaigns:
            if campaign.get('name') == campaign_name:
                return campaign.get('id')
        print("Campaign not found:", campaign_name)
        return None
    else:
        print("Failed to fetch campaigns")
        print("Status code:", response.status_code)
        print(response.text)
        return None

# Function to upload leads to the specified campaign
def upload_to_campaign(api_key, campaign_id, selected_leads):
    url = "https://api.instantly.ai/api/v1/lead/add"
    leads = []

    if selected_leads and isinstance(selected_leads, list):
        for lead in selected_leads:
            if isinstance(lead, dict) and all(key in lead for key in ('email', 'first_name', 'last_name', 'company', 'type', 'title')):
                leads.append({
                    "email": lead['email'],
                    "first_name": lead['first_name'],
                    "last_name": lead['last_name'],
                    "company_name": lead['company'],
                    "type": lead['type'],
                    "title": lead['title'], 
                })
            else:
                logging.error("Invalid lead format: %s", lead)
    else:
        logging.error("No leads found in selected_leads or selected_leads is not a list.")

    payload = {
        "api_key": api_key,
        "campaign_id": campaign_id,
        "skip_if_in_workspace": False,
        "leads": leads
    }
    headers = {
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an error for bad status codes

        if response.status_code == 200:
            logging.info("Leads uploaded successfully to campaign: %s", campaign_id)
            logging.info(response.json())
    except requests.exceptions.RequestException as e:
        logging.error("Failed to upload leads to campaign: %s", campaign_id)
        logging.error("Error: %s", str(e))
        logging.error("Response text: %s", response.text if 'response' in locals() else "No response available")

    return response.status_code if 'response' in locals() else None  # Return status code or None if no response

@csrf_exempt
def upload_to_campaign_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # Load JSON data from request body

            selected_leads = data.get('selected_leads')
            campaign_name = data.get('campaign_name')

            # Validate if selected_leads and campaign_name exist in the request
            if not selected_leads or not campaign_name:
                return JsonResponse({'error': 'Incomplete data received'}, status=400)

            # Assuming api_key and campaign_id are available, fetch them from session or elsewhere
            api_key = '6efvz60989m4q3jnwvyhm2x7wa1c'
            campaign_id = get_campaign_id(api_key, campaign_name)

            # Attempt to upload to campaign
            upload_result = upload_to_campaign(api_key, campaign_id, selected_leads)

            # Return a JSON response indicating the status or success/failure of the upload
            return JsonResponse({'success': True, 'upload_result': upload_result})
        
        except Exception as e:
            # Log the error for debugging purposes
            logger.error(f"Error uploading to campaign: {e}", exc_info=True)
            return HttpResponseServerError('Error occurred while processing the request.')
        
@login_required
def campaign_page(request):
    return render(request, 'campaign.html')

