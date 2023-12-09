from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Contact, SelectedContacts
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login
from django.db.models import Count
from .forms import UserRegisterForm
from django.http import HttpResponse
import csv
import json

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

def campaignA(request):
    if request.method == 'GET':
        try:
            selected_contacts_param = request.GET.get('selected_contacts')
            selected_contacts_ids = selected_contacts_param.split(',') if selected_contacts_param else []

            # Fetch contacts based on the selected contact IDs
            selected_contacts = Contact.objects.filter(id__in=selected_contacts_ids)

            context = {'selected_contacts': selected_contacts}
            return render(request, 'campaignA.html', context)
        except Exception as e:
            return render(request, 'error.html', {'error_message': str(e)})

    
    return render(request, 'campaignA.html')

def campaignB(request):
    if request.method == 'GET':
        try:
            selected_contacts_param = request.GET.get('selected_contacts')
            selected_contacts_ids = selected_contacts_param.split(',') if selected_contacts_param else []

            # Fetch contacts based on the selected contact IDs
            selected_contacts = Contact.objects.filter(id__in=selected_contacts_ids)

            context = {'selected_contacts': selected_contacts}
            return render(request, 'campaignB.html', context)
        except Exception as e:
            # Handle exceptions or errors
            # redirect or display an error message here
            return render(request, 'error.html', {'error_message': str(e)})

    return render(request, 'campaignB.html')

@login_required
def add_to_campaign(request):
    if request.method == 'POST':
        contact_ids = request.POST.getlist('selected_contacts[]')  # Assuming contact IDs are sent in POST data

        # Get or create SelectedContacts instance for the current user
        selected_contacts, created = SelectedContacts.objects.get_or_create(user=request.user)

        # Update contact_ids field with new selected contact IDs
        selected_contacts.contact_ids = ','.join(contact_ids)
        selected_contacts.save()

        return HttpResponse('Selected contacts added successfully.')

    return HttpResponse('Invalid request.')

def view_campaign(request):
    return render(request, 'campaign.html')