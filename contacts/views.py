from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import Contact
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login
import csv

def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            # Redirect to a specific URL after successful login
            return redirect('home')  # Replace 'home' with your desired URL
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def home(request):
    home = Contact.objects.all()
    return render(request, 'home.html')

def contact_list(request):
    contacts = Contact.objects.all()
    return render(request, 'contact_list.html', {'contacts': contacts})

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

