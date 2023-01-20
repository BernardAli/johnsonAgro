from django.shortcuts import render

# Create your views here.


def index_page(request):
    return render(request, 'home.html')


def about_page(request):
    return render(request, 'about.html')


def resume_page(request):
    return render(request, 'resume.html')


def services_page(request):
    return render(request, 'services.html')


def contact_page(request):
    return render(request, 'contact.html')