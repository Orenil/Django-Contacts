from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),
    path('contact-list/', views.contact_list, name='contact-list'),
    path('get_campaign_names/', views.get_campaign_names, name='get_campaign_names'),
    path('upload-csv/', views.upload_csv, name='upload_csv'),
    path('contact/filter/', views.filter_contacts, name='filter_contacts'),
    path('get_selected_contacts/', views.get_selected_contacts, name='get_selected_contacts'),
    path('upload_to_campaign/', views.upload_to_campaign_view, name='upload_to_campaign'),
    path('upload_to_campaign_emails/', views.upload_to_campaign_emails, name='upload_to_campaign_emails'),
    path('campaign/', views.campaign_page, name='campaign_page'),
    path('filter_leads/', views.filter_leads, name='filter_leads'),
    path('delete_selected_leads/', views.delete_selected_leads, name='delete_selected_leads'),
]

