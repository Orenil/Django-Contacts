from django.urls import path
from . import views

urlpatterns = [
    path('contact-list/', views.contact_list, name='contact_list')
]
