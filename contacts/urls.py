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
    path('upload-csv/', views.upload_csv, name='upload_csv'),
    path('contact/filter/', views.filter_contacts, name='filter_contacts'),
    path('leads/', views.leads, name='leads'),
    path('get_selected_contacts/', views.get_selected_contacts, name='get_selected_contacts')
]
