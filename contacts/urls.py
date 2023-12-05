from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('contact-list/', views.contact_list, name='contact-list'),
    path('upload-csv/', views.upload_csv, name='upload_csv')
]
