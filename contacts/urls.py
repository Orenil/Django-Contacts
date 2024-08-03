from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.contrib.auth import views as auth_views
from .views import ContactListAPIView, CampaignPageAPIView, SaveInstructionsAPIView, HomeAPIView, LoginAPIView, LogoutAPIView, UserRegisterAPIView, UploadCampaignEmailsAPIView, SelectedContactsAPIView, ProfileAPIView, DeleteLeadsFromCampaignAPIView, SendIndividualEmailAPIView, EmailCountsAPIView, CheckRepliedEmailsAPIView, ProcessLinkedInView, TotalContactsAPIView, TotalLeadsInCampaignAPIView

urlpatterns = [
    path('', HomeAPIView.as_view(), name='home'),
    path('about/', views.about, name='about'),
    path('register/', UserRegisterAPIView.as_view(), name='register'),
    path('user-info/', views.print_user_info, name='user-info'),
    path('profile/', ProfileAPIView.as_view(), name='profile'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
    path('contact-list/', ContactListAPIView.as_view(), name='contact-list'),
    path('get_campaign_names/', views.get_campaign_names, name='get_campaign_names'),
    path('get_selected_contacts/', SelectedContactsAPIView.as_view(), name='get_selected_contacts'),
    path('upload_to_campaign/', UploadCampaignEmailsAPIView.as_view(), name='upload_to_campaign'),
    path('campaign/', CampaignPageAPIView.as_view(), name='campaign_page'),
    path('delete_leads/', DeleteLeadsFromCampaignAPIView.as_view(), name='delete_leads'),
    path('launch_campaign/', views.launch_campaign, name='launch_campaign'),
    path('pause_campaign/', views.pause_campaign, name='pause_campaign'),
    path('get_campaign_status/', views.get_campaign_status, name='get_campaign_status'),
    path('campaign-analytics/', views.campaign_analytics, name='campaign_analytics'),
    path('get_campaign_summary/', views.get_campaign_summary, name='get_campaign_summary'),
    path('email-template/', views.email_template_page, name='email_template'),
    path('send_email/', views.send_email, name='send_email'),
    path('get_email_details/', views.get_email_details, name='get_email_details'),
    path('save-instructions/', SaveInstructionsAPIView.as_view(), name='save_instructions'),
    path('send-individual-emails/', SendIndividualEmailAPIView.as_view(), name='send_individual_emails'),
    path('email-counts/', EmailCountsAPIView.as_view(), name='email_counts'),
    path('check_replied/', CheckRepliedEmailsAPIView.as_view(), name='check_replied'),
    path('update_sequences/', views.update_sequences, name='update_sequences'),
    path('api/process-linkedin/', ProcessLinkedInView.as_view(), name='process-linkedin'),
    path('contacts/total/', TotalContactsAPIView.as_view(), name='total-contacts'),
    path('leads/total/', TotalLeadsInCampaignAPIView.as_view(), name='total-leads'), 
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

