from django.urls import path
from . import views


urlpatterns = [
    path('', views.index_page, name='home'),
    path('about/', views.about_page, name='about'),
    path('resume/', views.resume_page, name='resume'),
    path('services/', views.services_page, name='services'),
    path('products/', views.products_page, name='products'),
    path('contact/', views.contact_page, name='contact'),
]