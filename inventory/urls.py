from django.urls import path
from . import views

appname = "index_page"

urlpatterns = [
    path('', views.index_page, name='home'),
]