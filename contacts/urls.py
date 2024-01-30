from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
    path('contact-list/', views.contact_list, name='contact-list'),
    path('get_campaign_names/', views.get_campaign_names, name='get_campaign_names'),
    path('contact/filter/', views.filter_contacts, name='filter_contacts'),
    path('get_selected_contacts/', views.get_selected_contacts, name='get_selected_contacts'),
    path('upload_to_campaign/', views.upload_to_campaign_view, name='upload_to_campaign'),
    path('upload_to_campaign_emails/', views.upload_to_campaign_emails, name='upload_to_campaign_emails'),
    path('campaign/', views.campaign_page, name='campaign_page'),
    path('filter_leads/', views.filter_leads, name='filter_leads'),
    path('delete_selected_leads/', views.delete_selected_leads, name='delete_selected_leads'),
    path('launch_campaign/', views.launch_campaign, name='launch_campaign'),
    path('pause_campaign/', views.pause_campaign, name='pause_campaign'),
    path('get_campaign_status/', views.get_campaign_status, name='get_campaign_status'),
    path('campaign-analytics/', views.campaign_analytics, name='campaign_analytics'),
    path('get_campaign_summary/', views.get_campaign_summary, name='get_campaign_summary'),
    path('email-template/', views.email_template_page, name='email_template'),
    path('send_email/', views.send_email, name='send_email'),
    path('get_email_details/', views.get_email_details, name='get_email_details'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

