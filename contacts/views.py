from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.core import serializers as django_serializers
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
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .models import Contact, Campaign_Emails, Campaign, Email, Instructions
from .serializers import ContactSerializer, Campaign_EmailsSerializer, CampaignSerializer, EmailSerializer, InstructionsSerializer, UserRegisterSerializer, ProfileSerializer, DeleteLeadsSerializer
from rest_framework.authentication import SessionAuthentication
from knox.auth import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from knox.views import LoginView as KnoxLoginView
from knox.views import LogoutView as KnoxLogoutView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.decorators import authentication_classes, permission_classes
from knox.models import AuthToken
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
from django.conf import settings
import smtplib
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from .utils import process_linkedin_html
from email import encoders
import os
import smtplib
import imaplib
from .helpers import getEmailFromContactId, getFirstNameFromContactId, getLastNameFromContactId, getCompanyNameFromContactId, getTypeFromContactId, getTitleFromContactId
import csv
import json
import requests
import logging
from datetime import date
import os

def about(request):
    return render(request, 'about.html')

class LoginAPIView(KnoxLoginView):
    permission_classes = []

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        auth_login(request, user)        
        return super(LoginAPIView, self).post(request, format=None)

class LogoutAPIView(KnoxLogoutView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        # Logout the user and invalidate the token
        request._auth.delete()
        return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)

class UserRegisterAPIView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Your account has been created!'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
def print_user_info(request):
    # Retrieve all users from the User model
    all_users = User.objects.all()

    # Create a string to store user IDs and usernames
    user_info_str = "User Information:\n"

    # Iterate through each user and append their ID and username to the string
    for user in all_users:
        user_info_str += f"User ID: {user.id}, Username: {user.username}\n"

    # Print the user information to the console
    print(user_info_str)

    # Return an HTTP response with the user information for testing purposes
    return HttpResponse(user_info_str, content_type="text/plain")

class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile_instance = request.user.profile
        serializer = ProfileSerializer(profile_instance)
        return Response(serializer.data)

    def put(self, request):
        profile_instance = request.user.profile
        serializer = ProfileSerializer(profile_instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class HomeAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        # Retrieve existing Instructions data for the current user
        instructions = Instructions.objects.filter(user=request.user).first()
        serializer = InstructionsSerializer(instructions)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ContactListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        # Ensure the user is authenticated before accessing request.user
        user_campaigns = Campaign.objects.filter(user=request.user)
        campaign_names = list(user_campaigns.values_list('name', flat=True))
        distinct_types = Contact.objects.order_by('type').values_list('type', flat=True).distinct()
        distinct_companies = Contact.objects.order_by('company').values_list('company', flat=True).distinct()
        distinct_locations = Contact.objects.order_by('location').values_list('location', flat=True).distinct()
        distinct_levels = Contact.objects.order_by('level').values_list('level', flat=True).distinct()
        distinct_university = Contact.objects.order_by('university').values_list('university', flat=True).distinct()
        
        contacts = Contact.objects.all()
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

        contacts = contacts.filter(filter_conditions)

        items_per_page = 50
        page = request.GET.get('page', 1)

        paginator = Paginator(contacts, items_per_page)
        try:
            contacts = paginator.page(page)
        except PageNotAnInteger:
            contacts = paginator.page(1)
        except EmptyPage:
            contacts = paginator.page(paginator.num_pages)

        filter_params = {
            'typeFilter': type_filter,
            'companyFilter': company_filter,
            'locationFilter': location_filter,
            'levelFilter': level_filter,
            'universityFilter': university_filter,
        }

        serializer = ContactSerializer(contacts, many=True)
        return Response({
            'contacts': serializer.data,
            'distinct_types': distinct_types,
            'distinct_companies': distinct_companies,
            'distinct_locations': distinct_locations,
            'distinct_levels': distinct_levels,
            'distinct_university': distinct_university,
            'campaign_names': campaign_names,
            'query': query,
            'filter_params': filter_params,
        })

class TotalContactsAPIView(APIView):
    def get(self, request):
        total_contacts = Contact.objects.count()
        return Response({'total_contacts': total_contacts})
    
@login_required
def get_campaign_names(request):
    if request.method == 'GET':
        user_campaigns = Campaign.objects.filter(user=request.user)
        campaign_names = list(user_campaigns.values_list('name', flat=True))
        return JsonResponse({'campaigns': campaign_names})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

class SelectedContactsAPIView(APIView):
    def get(self, request):
        contact_ids = request.GET.getlist('contactIds[]')  # Fetch the contact IDs from the request
        if not contact_ids:
            contact_ids = request.GET.getlist('contactIds')  # Fallback to 'contactIds' if 'contactIds[]' is not found
        
        contacts = Contact.objects.filter(id__in=contact_ids)
        serializer = ContactSerializer(contacts, many=True)
        return Response({'contacts': serializer.data}, status=status.HTTP_200_OK)

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

class UploadCampaignEmailsAPIView(APIView):
    def post(self, request):
        try:
            # Parse the request data
            selected_leads = request.data.get('selected_leads', [])
            campaign_name = request.data.get('campaign_name')
            user_id = request.data.get('user_id')

            if not selected_leads or not campaign_name or not user_id:
                return Response({'error': 'Incomplete data received'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            # Upload to the database
            leads_to_upload = []
            for lead in selected_leads:
                email = lead.get('email', '')
                if not Campaign_Emails.objects.filter(email=email, user=user).exists():
                    leads_to_upload.append(Campaign_Emails(
                        user=user,
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
            except Exception as e:
                logging.error("Failed to upload leads to campaign_emails model.")
                logging.error("Error: %s", str(e))
                return Response({'detail': 'Failed to upload leads'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Upload to the campaign
            api_key = '6efvz60989m4q3jnwvyhm2x7wa1c'
            campaign_id = get_campaign_id(api_key, campaign_name)

            # Ensure unique leads based on email
            selected_leads = [dict(t) for t in {tuple(d.items()) for d in selected_leads}]
            
            upload_result = upload_to_campaign(api_key, campaign_id, selected_leads)

            return Response({'detail': 'Leads uploaded successfully and campaign updated'}, status=status.HTTP_201_CREATED)

        except Exception as e:
            logging.error("Error occurred during the combined upload process.")
            logging.error("Error: %s", str(e))
            return HttpResponseServerError('Error occurred while processing the request.')

class CampaignPageAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user_campaigns = Campaign.objects.filter(user=request.user)
        type_filter = request.GET.get('typeFilter')
        company_filter = request.GET.get('companyFilter')
        location_filter = request.GET.get('locationFilter')
        university_filter = request.GET.get('universityFilter')
        campaign_filter = request.GET.get('campaignFilter')
        
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

        search_query = request.GET.get('searchQuery')

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

        all_campaign_emails = Campaign_Emails.objects.filter(campaign_name__in=user_campaigns.values_list('name', flat=True)).order_by('campaign_name')

        filtered_campaign_emails = all_campaign_emails.filter(filter_conditions)

        items_per_page = 50
        page = request.GET.get('page', 1)

        paginator = Paginator(filtered_campaign_emails, items_per_page)
        try:
            campaign_emails = paginator.page(page)
        except PageNotAnInteger:
            campaign_emails = paginator.page(1)
        except EmptyPage:
            campaign_emails = paginator.page(paginator.num_pages)

        distinct_campaigns = user_campaigns.values_list('name', flat=True).distinct()
        distinct_types = all_campaign_emails.values_list('type', flat=True).distinct()
        distinct_companies = all_campaign_emails.values_list('company', flat=True).distinct()
        distinct_locations = all_campaign_emails.values_list('location', flat=True).distinct()
        distinct_university = all_campaign_emails.values_list('university', flat=True).distinct()

        filter_params = {
            'typeFilter': type_filter,
            'companyFilter': company_filter,
            'locationFilter': location_filter,
            'universityFilter': university_filter,
            'campaignFilter': campaign_filter,
            'searchQuery': search_query,
        }

        serializer = Campaign_EmailsSerializer(campaign_emails, many=True)
        return Response({
            'campaign_emails': serializer.data,
            'distinct_campaigns': distinct_campaigns,
            'distinct_types': distinct_types,
            'distinct_companies': distinct_companies,
            'distinct_locations': distinct_locations,
            'distinct_university': distinct_university,
            'filter_params': filter_params,
        })
class TotalLeadsInCampaignAPIView(APIView):

    def get(self, request, *args, **kwargs):
        campaign_name = request.GET.get('campaign_name')
        user_id = request.GET.get('user_id')
        
        # Check if user_id and campaign_name exist in the request data
        if not campaign_name:
            return JsonResponse({'error': 'Campaign name is required'}, status=400)
        if not user_id:
            return JsonResponse({'error': 'User ID is required'}, status=400)
        
        # Retrieve user using filter().first() to handle non-existent users gracefully
        user = User.objects.filter(id=user_id).first()
        if user is not None:
            total_leads = Campaign_Emails.objects.filter(campaign_name=campaign_name, user=user).count()
            return Response({'total_leads': total_leads})
        else:
            return JsonResponse({'error': 'User not found'}, status=404)

class DeleteLeadsFromCampaignAPIView(APIView):

    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        serializer = DeleteLeadsSerializer(data=request.data)
        if serializer.is_valid():
            delete_list = serializer.validated_data.get('delete_list')
            campaign_name = serializer.validated_data.get('campaign_name')
            user_id = request.data.get('user_id')  # Extract user_id from request data

            # Check if user_id exists in the request data
            if user_id is None:
                return JsonResponse({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)

            # Retrieve user using filter().first() to handle non-existent users gracefully
            user = User.objects.filter(id=user_id).first()
            if user is not None:
                # First, delete leads from the campaign database
                try:
                    Campaign_Emails.objects.filter(email__in=delete_list, user=user).delete()
                except Exception as e:
                    return JsonResponse({'error': f'Failed to delete from campaign database: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                # Now, delete leads from Instantly AI
                api_key = '6efvz60989m4q3jnwvyhm2x7wa1c'
                campaign_id = get_campaign_id(api_key, campaign_name)

                if campaign_id:
                    payload = {
                        "api_key": api_key,
                        "campaign_id": campaign_id,
                        "delete_all_from_company": False,
                        "delete_list": delete_list  # Pass the list of emails to be deleted
                    }

                    url = "https://api.instantly.ai/api/v1/lead/delete"
                    headers = {'Content-Type': 'application/json'}
                    response = requests.post(url, headers=headers, json=payload)

                    if response.status_code == 200:
                        return JsonResponse({'message': 'Leads deleted successfully from both the campaign database and Instantly AI'})
                    else:
                        # If deletion from Instantly AI fails, handle this scenario accordingly
                        return JsonResponse({'error': 'Failed to delete leads from Instantly AI'}, status=response.status_code)
                else:
                    return JsonResponse({'error': 'Invalid campaign name'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return JsonResponse({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
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


@api_view(['GET'])
@login_required
def email_template_page(request):
    # Retrieve emails associated with the logged-in user
    user_emails = Email.objects.filter(user=request.user)
    email_serializer = EmailSerializer(user_emails, many=True)
    
    # Fetch campaign names associated with the logged-in user
    user_campaigns = Campaign.objects.filter(user=request.user)
    campaign_serializer = CampaignSerializer(user_campaigns, many=True)

    data = {
        'user_emails': email_serializer.data if user_emails.exists() else [],
        'campaign_names': campaign_serializer.data
    }

    return Response(data)

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
            else:
                # Create a new email
                email = Email.objects.create(
                    user=request.user,
                    subject=subject,
                    email_content1=email_content1,
                    email_content2=email_content2,
                    email_content3=email_content3,
                    font_family=font_family,
                    font_size=font_size,
                    campaign=selected_campaign
                )

            # Send email notification
            send_mail(
                'Email Updated' if email.pk else 'New Email Created',
                f'The email for campaign "{selected_campaign_name}" has been updated.' if email.pk else f'A new email for campaign "{selected_campaign_name}" has been created.',
                os.environ.get('EMAIL_USER'),  # Sender's email
                ['followupnowinfo@gmail.com', 'oreoluwaadesina1999@gmail.com'],  
                fail_silently=False,
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

class SaveInstructionsAPIView(APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = InstructionsSerializer(data=request.data)
        if serializer.is_valid():
            # Fetch user based on user_id
            try:
                user = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            # Extract data from the validated serializer
            data = serializer.validated_data

            # If an existing instruction exists, update it, else create a new one
            existing_instruction = Instructions.objects.filter(user=user).first()
            if existing_instruction:
                instruction = existing_instruction
                status_code = status.HTTP_200_OK  # Indicate update
                message = 'Updated successfully'
            else:
                instruction = Instructions(user=user)
                status_code = status.HTTP_201_CREATED  # Indicate creation
                message = 'Saved successfully'

            # Update instruction data
            instruction.first_name = data.get('first_name')
            instruction.last_name = data.get('last_name')
            instruction.email = data.get('email')
            instruction.app_password = data.get('app_password')
            instruction.second_email = data.get('second_email')
            instruction.second_app_password = data.get('second_app_password')
            instruction.third_email = data.get('third_email')
            instruction.third_app_password = data.get('third_app_password')
            instruction.save()

            # Send email notification
            send_mail(
                'App password updated',
                f'The profile details for user "{instruction.first_name} {instruction.last_name}" have been updated.',
                os.environ.get('EMAIL_USER'),  # Sender's email
                ['followupnowinfo@gmail.com', 'oreoluwaadesina1999@gmail.com'],  # Recipient's email
                fail_silently=False,
            )

            return Response({'message': message}, status=status_code)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#sending individual emails
class SendIndividualEmailAPIView(APIView):
    def post(self, request):
        try:
            # Load JSON data from request body
            data = json.loads(request.body)
            
            # Extract parameters from JSON data
            smtp_host = data.get('smtpHost')
            smtp_port = data.get('smtpPort', 465)  # Using SSL port
            mail_uname = data.get('mailUname')
            mail_pwd = data.get('mailPwd')
            from_email = data.get('fromEmail')
            mail_subject = data.get('mailSubject', '')
            mail_content_html = data.get('mailContentHtml', '')
            recepients_mail_list = data.get('recepientsMailList', [])  # Use empty list if not provided

            # Check for required parameters
            if not all([smtp_host, mail_uname, mail_pwd, from_email, recepients_mail_list]):
                raise ValueError("Required parameters missing or empty")

            # Create message object
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = ','.join(recepients_mail_list)
            msg['Subject'] = mail_subject
            msg.attach(MIMEText(mail_content_html, 'html'))

            # Send message object as email using smtplib
            s = smtplib.SMTP_SSL(smtp_host, smtp_port)  # Use SMTP_SSL for port 465
            s.login(mail_uname, mail_pwd)
            msgText = msg.as_string()
            sendErrs = s.sendmail(from_email, recepients_mail_list, msgText)
            s.quit()

            # Check if errors occurred and handle them accordingly
            if not sendErrs:
                return Response({'message': 'Email sent successfully'})
            else:
                raise Exception("Errors occurred while sending email", sendErrs)
        except json.JSONDecodeError:
            return Response({'error': 'Invalid JSON data in request body'}, status=status.HTTP_400_BAD_REQUEST)
        except smtplib.SMTPException as e:
            return Response({'error': f'SMTP error occurred: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class EmailCountsAPIView(APIView):
    def get(self, request):
        try:
            data = json.loads(request.body) if request.body else {}  # Get JSON data from request body

            # Extract parameters from JSON data
            host = data.get('host')
            username = data.get('username')
            password = data.get('password')
            subject_keyword = data.get('subject_keyword')

            if not all([host, username, password, subject_keyword]):
                return JsonResponse({'error': 'Host, username, password, or subject keyword missing'}, status=400)

            mail = imaplib.IMAP4_SSL(host)
            mail.login(username, password)
            mail.select("inbox")

            # Get count of unseen messages with the subject keyword
            _, unseen_data = mail.search(None, '(UNSEEN)', '(SUBJECT "{}")'.format(subject_keyword))
            unseen_count = len(unseen_data[0].split())

            # Get count of seen messages with the subject keyword
            _, seen_data = mail.search(None, '(SEEN)', '(SUBJECT "{}")'.format(subject_keyword))
            seen_count = len(seen_data[0].split())

            return JsonResponse({'unseen_count': unseen_count, 'seen_count': seen_count})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
class CheckRepliedEmailsAPIView(APIView):
    def get(self, request):
        try:
            data = json.loads(request.body) if request.body else {} # Get JSON data from request

            # Extract parameters from JSON data
            host = data.get('host')
            username = data.get('username')
            password = data.get('password')
            subject_keyword = data.get('subject_keyword')

            if not all([host, username, password, subject_keyword]):
                return JsonResponse({'error': 'Missing required parameters'}, status=400)

            # Your email checking logic here
            mail = imaplib.IMAP4_SSL(host)
            mail.login(username, password)
            mail.select("inbox")

            _, search_data = mail.search(None, '(UNSEEN SUBJECT "{}")'.format(subject_keyword))
            replies_info = []

            for num in search_data[0].split():
                _, data = mail.fetch(num, '(FLAGS)')
                replied = '\\Answered' in data[0].decode('utf-8')
                replied_status = 'NO' if replied else 'YES'
                replies_info.append({'subject': subject_keyword, 'replied': replied_status})

            mail.close()
            mail.logout()

            return JsonResponse({'replies_info': replies_info})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_POST
def update_sequences(request):
    # Parse request data
    data = json.loads(request.body)
    user_id = data.get('user_id')  # User ID
    email = data.get('email')  # FollowUp Instantly Email
    password = data.get('password')  # FollowUp Instantly Password
    campaign_name = data.get('campaign_name')
    sequence_data = data.get('sequence_data')

    # Extract sequence steps
    sequences = sequence_data.get('sequences', [])

    # Prepare lists to store email contents and subjects
    email_contents = []
    subjects = []

    # Iterate over sequences and steps
    for sequence in sequences:
        for step in sequence.get('steps', []):
            for variant in step.get('variants', []):
                # Extract subject and body from each variant
                subject = variant.get('subject', '')
                body = variant.get('body', '')

                # Append to lists
                subjects.append(subject)
                email_contents.append(body)

    # Ensure we have at least three contents for the Email fields
    while len(email_contents) < 3:
        email_contents.append('')

    # Get the campaign ID
    api_key = '6efvz60989m4q3jnwvyhm2x7wa1c'  # Replace with your API key
    campaign_id = get_campaign_id(api_key, campaign_name)

    if campaign_id is None:
        return JsonResponse({'message': 'Failed to get campaign ID'}, status=400)

    # Call the combined function
    result_message = authenticate_and_update_sequences(email, password, campaign_id, sequence_data)

    # Save the email data to the database if sequences are updated successfully
    if result_message == "Sequences updated successfully!":
        try:
            # Get the user by ID
            user = User.objects.get(id=user_id)

            # Get or create the campaign
            campaign, created = Campaign.objects.get_or_create(name=campaign_name, user=user)

            # Check for an existing email object by matching user, campaign, and subjects
            email_obj = Email.objects.filter(
                user=user,
                campaign=campaign,
                subject=subjects[0] if subjects else ''
            ).first()

            if email_obj:
                # Update the existing record
                email_obj.email_content1 = email_contents[0]
                email_obj.email_content2 = email_contents[1]
                email_obj.email_content3 = email_contents[2]
                email_obj.save()
            else:
                # Create a new record if no existing email is found
                Email.objects.create(
                    user=user,
                    campaign=campaign,
                    subject=subjects[0] if subjects else '',
                    email_content1=email_contents[0],
                    email_content2=email_contents[1],
                    email_content3=email_contents[2],
                )

            return JsonResponse({'message': 'Sequences updated and email data saved successfully!'}, status=200)

        except User.DoesNotExist:
            return JsonResponse({'message': 'User not found'}, status=400)

    return JsonResponse({'message': result_message}, status=400)

def authenticate_and_update_sequences(email, password, campaign_id, sequence_data):
    # Authentication
    auth_url = 'https://app.instantly.ai/api/auth/login'
    auth_payload = {'email': email, 'password': password}
    auth_response = requests.post(auth_url, json=auth_payload)
    
    if auth_response.status_code != 200:
        return "Authentication failed."
    
    # Get the cookies from the authentication response
    cookies = auth_response.cookies
    
    # Update Sequences
    update_url = 'https://app.instantly.ai/api/campaign/update/sequences'
    headers = {
        'accept': 'application/json',
        'content-type': 'application/json',
        'referer': f'https://app.instantly.ai/app/campaign/{campaign_id}/sequences',
    }
    
    update_response = requests.post(update_url, cookies=cookies, headers=headers, json=sequence_data)
    
    if update_response.status_code == 200:
        return "Sequences updated successfully!"
    else:
        return "Failed to update sequences."
    
class ProcessLinkedInView(APIView):
    def post(self, request, *args, **kwargs):
        html_file_path = request.data.get('html_file_path')
        
        if not html_file_path:
            return Response({'error': 'html_file_path is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            contacts, matches = process_linkedin_html(html_file_path)

            # Prepare CSV data
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'Full_Contacts.csv'

            # Write CSV data to the response
            writer = csv.DictWriter(response, fieldnames=matches[0].keys())
            writer.writeheader()
            for match in matches:
                writer.writerow(match)

            return response
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)