from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, ContactSearchForm, InstructionsForm
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.middleware.csrf import get_token
from django.http import JsonResponse, HttpResponseServerError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Contact, Campaign_Emails, Campaign, Email, Instructions
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.db.models import Count
from django.db.models import Q
from django.contrib.auth.models import User
from .forms import UserRegisterForm
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from .helpers import getEmailFromContactId, getFirstNameFromContactId, getLastNameFromContactId, getCompanyNameFromContactId, getTypeFromContactId, getTitleFromContactId
import csv
import json
import requests
import logging
from datetime import date
import os

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
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your Account has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'profile.html', context)

@login_required
def home(request):
    # Retrieve existing Instructions data for the current user
    instructions = Instructions.objects.filter(user=request.user).first()
    return render(request, 'home.html', {'instructions': instructions})

@login_required
def contact_list(request):
    # Filter campaigns associated with the logged-in user
    user_campaigns = Campaign.objects.filter(user=request.user)

    # Extract campaign names as a list
    campaign_names = list(user_campaigns.values_list('name', flat=True))

    distinct_types = Contact.objects.order_by('type').values_list('type', flat=True).distinct()
    distinct_companies = Contact.objects.order_by('company').values_list('company', flat=True).distinct()
    distinct_locations = Contact.objects.order_by('location').values_list('location', flat=True).distinct()
    distinct_levels = Contact.objects.order_by('level').values_list('level', flat=True).distinct()
    distinct_university = Contact.objects.order_by('university').values_list('university', flat=True).distinct()

    # Get all contacts
    contacts = Contact.objects.all()

    # Apply search query
    query = request.GET.get('q')
    if query:
        contacts = contacts.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(title__icontains=query) |
            Q(company__icontains=query) |
            Q(type__icontains=query) |
            Q(location__icontains=query) |
            Q(level__icontains=query) |
            Q(university__icontains=query) |
            Q(linkedin__icontains=query)
        )

    # Apply filters based on filter parameters
    type_filter = request.GET.get('typeFilter')
    company_filter = request.GET.get('companyFilter')
    location_filter = request.GET.get('locationFilter')
    level_filter = request.GET.get('levelFilter')
    university_filter = request.GET.get('universityFilter')

    filter_conditions = Q()

    if type_filter:
        filter_conditions &= Q(type__icontains=type_filter)

    if company_filter:
        filter_conditions &= Q(company__icontains=company_filter)

    if location_filter:
        filter_conditions &= Q(location__icontains=location_filter)

    if level_filter:
        filter_conditions &= Q(level__icontains=level_filter)

    if university_filter:
        filter_conditions &= Q(university__icontains=university_filter)

    # Combine search query and filters
    contacts = contacts.filter(filter_conditions)

    # Pagination
    items_per_page = 50
    page = request.GET.get('page', 1)

    paginator = Paginator(contacts, items_per_page)
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        contacts = paginator.page(1)
    except EmptyPage:
        contacts = paginator.page(paginator.num_pages)

    # Pass filter parameters in the context
    filter_params = {
        'typeFilter': type_filter,
        'companyFilter': company_filter,
        'locationFilter': location_filter,
        'levelFilter': level_filter,
        'universityFilter': university_filter,
    }

    return render(request, 'contact_list.html', {
        'contacts': contacts,
        'distinct_types': distinct_types,
        'distinct_companies': distinct_companies,
        'distinct_locations': distinct_locations,
        'distinct_levels': distinct_levels,
        'distinct_university': distinct_university,
        'campaign_names': campaign_names,
        'query': query,  # Pass the query to the template for display
        'filter_params': filter_params,  # Pass filter parameters to maintain consistency
    })

@login_required
def get_campaign_names(request):
    if request.method == 'GET':
        user_campaigns = Campaign.objects.filter(user=request.user)
        campaign_names = list(user_campaigns.values_list('name', flat=True))
        return JsonResponse({'campaigns': campaign_names})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

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
                        first_name, last_name, email, title, company, type, location, level = row
                        existing_contact = Contact.objects.filter(email=email).first()
                        if existing_contact:
                            messages.warning(request, f"Skipped row at index {row_count}: {row}. Contact with email '{email}' already exists.")
                        else:
                            Contact.objects.create(
                                first_name=first_name, last_name=last_name, email=email,
                                title=title, company=company, type=type,
                                location=location, level=level
                            )
                    else:
                        messages.warning(request, f"Skipped row at index {row_count}: {row}. Unexpected number of values.")

                messages.success(request, 'Contacts uploaded successfully.')
            except Exception as e:
                messages.error(request, f"Error uploading contacts: {e}")
    return render(request, 'upload_csv.html')

@csrf_exempt
def filter_contacts(request):
    if request.method == 'POST':
        # Get filter parameters from the frontend
        type_filter = request.POST.get('type')
        company_filter = request.POST.get('company')
        location_filter = request.POST.get('location')
        level_filter = request.POST.get('level')
        university_filter = request.GET.get('universityFilter')
        page_number = request.POST.get('page')  # Get the requested page number

        # Retrieve all contacts
        all_contacts = Contact.objects.all()

        # Apply filters to the Contact queryset
        filtered_contacts = all_contacts  # Start with all contacts
        
        if type_filter:
            filtered_contacts = filtered_contacts.filter(type=type_filter)
        if company_filter:
            filtered_contacts = filtered_contacts.filter(company=company_filter)
        if location_filter:
            filtered_contacts = filtered_contacts.filter(location=location_filter)
        if level_filter:
            filtered_contacts = filtered_contacts.filter(level=level_filter)
        if university_filter:
            filtered_contacts = filtered_contacts.filter(university=university_filter)

        # Pagination logic
        contacts_per_page = 50  # Set the number of contacts per page

        paginator = Paginator(filtered_contacts, contacts_per_page)

        try:
            contacts_page = paginator.page(page_number)
        except PageNotAnInteger:
            # If page is not an integer, return the first page
            contacts_page = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g., 9999), return the last page of results
            contacts_page = paginator.page(paginator.num_pages)

        # Prepare paginated emails data to send back as JSON
        contacts_data = list(contacts_page.object_list.values())  # Convert QuerySet to list of dictionaries

        return JsonResponse({
            'contacts': contacts_data,
            'total_pages': paginator.num_pages,
            'has_next': contacts_page.has_next(),
            'has_previous': contacts_page.has_previous(),
        }, status=200)

    return JsonResponse({'error': 'Invalid request method'}, status=400)

def get_selected_contacts(request):
    contact_ids = request.GET.getlist('contactIds[]')  # Fetch the contact IDs from the request
    contacts = Contact.objects.filter(id__in=contact_ids).values('first_name', 'last_name', 'email', 'company', 'type', 'location', 'level', 'university','linkedin')

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

def upload_to_campaign_emails(selected_leads, user_id, campaign_name):
    user = User.objects.get(id=user_id)  # Retrieve the user based on the provided ID

    leads_to_upload = []

    for lead in selected_leads:
        email = lead.get('email', '')
        if not Campaign_Emails.objects.filter(email=email, user=user).exists():
            leads_to_upload.append(Campaign_Emails(
                user=user,  # Associate the contact with the logged-in user
                email=email,
                first_name=lead.get('first_name', ''),
                last_name=lead.get('last_name', ''),
                company=lead.get('company', ''),
                type=lead.get('type', ''),
                location=lead.get('location', 'None'),
                title=lead.get('title', ''),
                university=lead.get('university', ''),
                campaign_name=campaign_name
            ))

    try:
        Campaign_Emails.objects.bulk_create(leads_to_upload)
        logging.info("Leads uploaded successfully to campaign_emails model.")
        return True
    except Exception as e:
        logging.error("Failed to upload leads to campaign_emails model.")
        logging.error("Error: %s", str(e))
        return False

@csrf_exempt
def upload_to_campaign_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            selected_leads = data.get('selected_leads')
            campaign_name = data.get('campaign_name')
            user_id = request.user.id 

            if not selected_leads or not campaign_name:
                return JsonResponse({'error': 'Incomplete data received'}, status=400)

            # Filter out duplicates from selected leads based on email addresses
            selected_leads = [dict(t) for t in {tuple(d.items()) for d in selected_leads}]
            
            print('Received campaign name:', campaign_name)
            print('Received selected leads:', selected_leads)

            api_key = '6efvz60989m4q3jnwvyhm2x7wa1c'
            campaign_id = get_campaign_id(api_key, campaign_name)

            upload_result = upload_to_campaign(api_key, campaign_id, selected_leads)
            
            # Attempt to upload lead information to campaign_emails model without duplicates
            campaign_emails_upload_success = upload_to_campaign_emails(selected_leads, user_id, campaign_name)

            if upload_result is not None and campaign_emails_upload_success:
                return JsonResponse({'success': True, 'instantly_upload_result': upload_result})
            else:
                return JsonResponse({'error': 'Failed to upload leads'}, status=500)
        
        except Exception as e:
            print('Error occurred during lead upload:', str(e))
            return HttpResponseServerError('Error occurred while processing the request.')

@login_required
def campaign_page(request):
    # Fetch campaigns associated with the logged-in user only
    user_campaigns = Campaign.objects.filter(user=request.user)

    # Fetch filter parameters
    type_filter = request.GET.get('typeFilter')
    company_filter = request.GET.get('companyFilter')
    location_filter = request.GET.get('locationFilter')
    university_filter = request.GET.get('universityFilter')
    campaign_filter = request.GET.get('campaignFilter')
    
    # Apply filters to campaign emails based on filter parameters
    filter_conditions = Q()

    if type_filter:
        filter_conditions &= Q(type__icontains=type_filter)

    if company_filter:
        filter_conditions &= Q(company__icontains=company_filter)

    if location_filter:
        filter_conditions &= Q(location__icontains=location_filter)
        
    if university_filter:
        filter_conditions &= Q(university__icontains=university_filter)

    if campaign_filter:
        filter_conditions &= Q(campaign_name__icontains=campaign_filter)

    # Fetch search query parameter
    search_query = request.GET.get('searchQuery')

    # Apply search query to filter conditions
    if search_query:
        filter_conditions &= (
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(title__icontains=search_query) |
            Q(campaign_name__icontains=search_query) |
            Q(type__icontains=search_query) |
            Q(company__icontains=search_query) |
            Q(university__icontains=search_query) |
            Q(location__icontains=search_query) 
        )

    # Fetch all campaign emails for the campaigns associated with the logged-in user and apply filters
    all_campaign_emails = Campaign_Emails.objects.filter(campaign_name__in=user_campaigns.values_list('name', flat=True)).order_by('campaign_name')

    # Apply filters and search query to the entire dataset
    filtered_campaign_emails = all_campaign_emails.filter(filter_conditions)

    # Pagination
    items_per_page = 50
    page = request.GET.get('page', 1)

    paginator = Paginator(filtered_campaign_emails, items_per_page)
    try:
        campaign_emails = paginator.page(page)
    except PageNotAnInteger:
        campaign_emails = paginator.page(1)
    except EmptyPage:
        campaign_emails = paginator.page(paginator.num_pages)

    # Fetch distinct campaign names for filtering purposes
    distinct_campaigns = user_campaigns.values_list('name', flat=True).distinct()
    distinct_types = all_campaign_emails.values_list('type', flat=True).distinct()
    distinct_companies = all_campaign_emails.values_list('company', flat=True).distinct()
    distinct_locations = all_campaign_emails.values_list('location', flat=True).distinct()
    distinct_university = all_campaign_emails.values_list('university', flat=True).distinct()

    # Pass filter parameters and search query in the context
    filter_params = {
        'typeFilter': type_filter,
        'companyFilter': company_filter,
        'locationFilter': location_filter,
        'universityFilter': university_filter,
        'campaignFilter': campaign_filter,
        'searchQuery': search_query,
    }

    return render(request, 'campaign.html', {
        'campaign_emails': campaign_emails,
        'distinct_campaigns': distinct_campaigns,
        'distinct_types': distinct_types,
        'distinct_companies': distinct_companies,
        'distinct_locations': distinct_locations,
        'distinct_university': distinct_university,
        'filter_params': filter_params,
    })
    
    
@csrf_exempt
def filter_leads(request):
    if request.method == 'POST':
        type_filter = request.POST.get('type')
        company_filter = request.POST.get('company')
        location_filter = request.POST.get('location')
        university_filter = request.POST.get('university')
        page_number = request.POST.get('page')  # Get the requested page number

        # Filter campaign emails based on received parameters
        filtered_emails = Campaign_Emails.objects.all()

        if type_filter:
            filtered_emails = filtered_emails.filter(type=type_filter)
        if company_filter:
            filtered_emails = filtered_emails.filter(company=company_filter)
        if location_filter:
            filtered_emails = filtered_emails.filter(location=location_filter)
        if university_filter:
            filtered_emails = filtered_emails.filter(university=location_filter)

        # Pagination
        emails_per_page = 50  # Set the number of emails per page

        paginator = Paginator(filtered_emails, emails_per_page)

        try:
            emails_page = paginator.page(page_number)
        except PageNotAnInteger:
            # If page is not an integer, return the first page
            emails_page = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g., 9999), return the last page of results
            emails_page = paginator.page(paginator.num_pages)

        # Prepare paginated emails data to send back as JSON
        emails_data = list(emails_page.object_list.values())  # Convert QuerySet to list of dictionaries

        return JsonResponse({
            'emails': emails_data,
            'total_emails': paginator.count,
            'total_pages': paginator.num_pages,
            'has_next': emails_page.has_next(),
            'has_previous': emails_page.has_previous(),
        }, status=200)

    return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def delete_selected_leads(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # Load JSON data from request body

            delete_list = data.get('delete_list')  # Retrieve list of emails for deletion
            campaign_name = data.get('campaign_name')
            user_id = request.user.id  # Retrieve the logged-in user ID
            user = User.objects.get(id=user_id)  # Retrieve the user based on the provided ID

            # Delete selected leads associated with the logged-in user from the database based on email
            Campaign_Emails.objects.filter(email__in=delete_list, user=user).delete()

            # Now, also delete from Instantly AI
            api_key = '6efvz60989m4q3jnwvyhm2x7wa1c'
            campaign_id = get_campaign_id(api_key, campaign_name)

            if campaign_id:
                payload = {
                    "api_key": "6efvz60989m4q3jnwvyhm2x7wa1c",
                    "campaign_id": campaign_id,
                    "delete_all_from_company": False,
                    "delete_list": delete_list  # Pass the list of emails to be deleted
                }

                url = "https://api.instantly.ai/api/v1/lead/delete"
                headers = {'Content-Type': 'application/json'}
                response = requests.post(url, headers=headers, json=payload)

                if response.status_code == 200:
                    return JsonResponse({'message': 'Leads deleted successfully from both the database and Instantly AI'})
                else:
                    # If deletion from Instantly AI fails, handle this scenario accordingly
                    return JsonResponse({'error': 'Failed to delete leads from Instantly AI'}, status=response.status_code)
            else:
                return JsonResponse({'error': 'Invalid campaign name'}, status=400)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def launch_campaign(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # Load JSON data from request body

            campaign_name = data.get('campaign_name')
            api_key = '6efvz60989m4q3jnwvyhm2x7wa1c' 

            if campaign_name and api_key:
                campaign_id = get_campaign_id(api_key, campaign_name)

                if campaign_id:
                    url = "https://api.instantly.ai/api/v1/campaign/launch"

                    payload = json.dumps({
                        "api_key": api_key,
                        "campaign_id": campaign_id
                    })

                    headers = {'Content-Type': 'application/json'}

                    response = requests.post(url, headers=headers, data=payload)

                    if response.status_code == 200:
                        return JsonResponse({'message': 'Campaign launched successfully'})
                    else:
                        return JsonResponse({'error': 'Failed to launch campaign'}, status=response.status_code)
                else:
                    return JsonResponse({'error': 'Campaign not found'}, status=404)
            else:
                return JsonResponse({'error': 'Missing campaign name or API key'}, status=400)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
@csrf_exempt
def pause_campaign(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # Load JSON data from request body

            campaign_name = data.get('campaign_name')
            api_key = '6efvz60989m4q3jnwvyhm2x7wa1c'

            if campaign_name and api_key:
                campaign_id = get_campaign_id(api_key, campaign_name)

                if campaign_id:
                    url = "https://api.instantly.ai/api/v1/campaign/pause"

                    payload = json.dumps({
                        "api_key": api_key,
                        "campaign_id": campaign_id
                    })

                    headers = {'Content-Type': 'application/json'}

                    response = requests.post(url, headers=headers, data=payload)

                    if response.status_code == 200:
                        return JsonResponse({'message': 'Campaign paused successfully'})
                    else:
                        return JsonResponse({'error': 'Failed to pause campaign'}, status=response.status_code)
                else:
                    return JsonResponse({'error': 'Campaign not found'}, status=404)
            else:
                return JsonResponse({'error': 'Missing campaign name or API key'}, status=400)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
@login_required
def campaign_analytics(request):
    # Fetch campaigns associated with the logged-in user only
    user_campaigns = Campaign.objects.filter(user=request.user)
    # Retrieve distinct campaign names
    distinct_campaigns = user_campaigns.values_list('name', flat=True).distinct()

    # Render the HTML template with the retrieved data
    return render(request, 'analytics.html', {'distinct_campaigns': distinct_campaigns})
    
@csrf_exempt
def get_campaign_summary(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            campaign_name = data.get('campaign_name')
            print("Received Campaign Name:", campaign_name)
            api_key = '6efvz60989m4q3jnwvyhm2x7wa1c'

            if campaign_name and api_key: 
                campaign_id = get_campaign_id(api_key, campaign_name)

                if campaign_id:
                    url = "https://api.instantly.ai/api/v1/analytics/campaign/summary"
                    params = {
                        "api_key": api_key,
                        "campaign_id": campaign_id
                    }

                    response = requests.get(url, params=params)

                    if response.status_code == 200:
                        analytics_data = response.json()
                        print(analytics_data)
                        return JsonResponse(analytics_data, safe=False)
                    else:
                        return JsonResponse({'error': 'Failed to fetch analytics'}, status=response.status_code)
                else:
                    return JsonResponse({'error': 'Invalid campaign name'}, status=400)
            else:
                return JsonResponse({'error': 'Missing campaign_name or api_key'}, status=400)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=500, safe=False)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
@csrf_exempt
def get_campaign_status(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            campaign_name = data.get('campaign_name')
            print("Received Campaign Name:", campaign_name)
            api_key = '6efvz60989m4q3jnwvyhm2x7wa1c'

            if campaign_name and api_key: 
                campaign_id = get_campaign_id(api_key, campaign_name)

                if campaign_id:
                    url = "https://api.instantly.ai/api/v1/campaign/get/status"
                    params = {
                        "api_key": api_key,
                        "campaign_id": campaign_id
                    }

                    response = requests.get(url, params=params)

                    if response.status_code == 200:
                        status_data = response.json()
                        print(status_data)
                        return JsonResponse(status_data, safe=False)
                    else:
                        return JsonResponse({'error': 'Failed to fetch analytics'}, status=response.status_code)
                else:
                    return JsonResponse({'error': 'Invalid campaign name'}, status=400)
            else:
                return JsonResponse({'error': 'Missing campaign_name or api_key'}, status=400)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=500, safe=False)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

@login_required
def email_template_page(request):
    # Retrieve emails associated with the logged-in user
    user_emails = Email.objects.filter(user=request.user)

    # Fetch campaign names associated with the logged-in user
    user_campaigns = Campaign.objects.filter(user=request.user)
    campaign_names = user_campaigns.values_list('name', flat=True)

    return render(request, 'email_template.html', {'user_emails': user_emails, 'campaign_names': campaign_names})

@login_required
def send_email(request):
    if request.method == 'POST':
        selected_campaign_name = request.POST.get('selected_campaign', None)
        subject = request.POST.get('subject', '')
        email_content1 = request.POST.get('emailContent1', '')
        email_content2 = request.POST.get('emailContent2', '')
        email_content3 = request.POST.get('emailContent3', '')
        font_family = request.POST.get('font_family', '')  # Updated to match the form field name
        font_size = request.POST.get('font_size', '')  # Updated to match the form field name

        if not selected_campaign_name:
            return JsonResponse({'error': 'Please select a campaign'}, status=400)

        user_campaigns = Campaign.objects.filter(user=request.user, name=selected_campaign_name)
        if user_campaigns.exists():
            selected_campaign = user_campaigns.first()
            # Check if an email already exists for this campaign
            email = Email.objects.filter(user=request.user, campaign=selected_campaign).first()

            if email:
                # Update existing email
                email.subject = subject
                email.email_content1 = email_content1
                email.email_content2 = email_content2
                email.email_content3 = email_content3
                email.font_family = font_family
                email.font_size = font_size
                email.save()

                # Send email notification
                send_mail(
                    'Email Updated',
                    f'The email for campaign "{selected_campaign_name}" has been updated.',
                    os.environ.get('EMAIL_USER'),  # Sender's email
                    ['followupnowinfo@gmail.com', 'oreoluwaadesina1999@gmail.com'],  # Replace with the recipient's email
                    fail_silently=False,
                )

            else:
                # Create a new email
                Email.objects.create(
                    user=request.user,
                    subject=subject,
                    email_content1=email_content1,
                    email_content2=email_content2,
                    email_content3=email_content3,
                    font_family=font_family,
                    font_size=font_size,
                    campaign=selected_campaign
                )

            return HttpResponseRedirect(reverse('email_template'))

    return HttpResponseRedirect(reverse('email_template'))

def get_email_details(request):
    if request.method == 'GET' and 'campaign' in request.GET:
        selected_campaign_name = request.GET['campaign']
        try:
            # Retrieve the email associated with the selected campaign
            selected_email = Email.objects.get(user=request.user, campaign__name=selected_campaign_name)
            email_contents = {
                'emailContent1': selected_email.email_content1,
                'emailContent2': selected_email.email_content2,
                'emailContent3': selected_email.email_content3,
                'subject': selected_email.subject,
            }
            return JsonResponse(email_contents)
        except Email.DoesNotExist:
            # Return default values when no email is found
            return JsonResponse({
                'emailContent1': '',
                'emailContent2': '',
                'emailContent3': '',
                'subject': '',
            })

    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def save_instructions(request):
    if request.method == 'POST':
        instruction_id = request.POST.get('instruction_id')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        app_password = request.POST.get('app_password')
        second_email = request.POST.get('second_email')
        second_app_password = request.POST.get('second_app_password')
        third_email = request.POST.get('third_email')
        third_app_password = request.POST.get('third_app_password')

        # If instruction_id exists, update the existing data
        if instruction_id:
            instruction = Instructions.objects.get(pk=instruction_id)
            instruction.first_name = first_name
            instruction.last_name = last_name
            instruction.email = email
            instruction.app_password = app_password
            instruction.second_email = second_email
            instruction.second_app_password = second_app_password
            instruction.third_email = third_email
            instruction.third_app_password = third_app_password
            instruction.save()
        else:
            # If instruction_id does not exist, create a new entry
            instruction = Instructions.objects.create(
                user=request.user,
                first_name=first_name,
                last_name=last_name,
                email=email,
                app_password=app_password,
                second_email=second_email,
                second_app_password=second_app_password,
                third_email=third_email,
                third_app_password=third_app_password
            )

        # Send email notification
        send_mail(
            'Instructions Updated',
            f'The email for user "{first_name} {last_name}" has been updated.',
            os.environ.get('EMAIL_USER'),  # Sender's email
            ['followpnowinfo@gmail.com','oreoluwaadesina1999@gmail.com'],  # Recipient's email
            fail_silently=False,
        )

        return redirect('home')  # Redirect to the home page after saving

    return redirect('home')  # Redirect to the home page if not a POST request

